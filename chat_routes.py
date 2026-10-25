from flask import Blueprint, request, jsonify, session
import uuid
import re
from chatbot.predict import predict_intent, get_static_response
from chatbot.entity_extractor import extract_entities
from database.db_connection import execute_query

chat_bp = Blueprint("chat", __name__)

EMAIL_REGEX = r"[\w\.-]+@[\w\.-]+\.\w+"
PHONE_REGEX = r"\b[6-9]\d{9}\b"

LEAD_FIELDS = ["name", "email", "phone", "preferred_course"]
LEAD_PROMPTS = {
    "name": "Great! Could you tell me your full name?",
    "email": "Thanks! What's your email address?",
    "phone": "Got it. Could you share your 10-digit phone number?",
    "preferred_course": "Last thing — which course are you interested in?",
}


def get_course_fee(course_name):
    rows = execute_query(
        "SELECT * FROM courses WHERE LOWER(course_name) LIKE ?",
        (f"%{course_name.lower()}%",), fetch=True
    )
    if rows:
        c = rows[0]
        return (f"The fee for {c['course_name']} is ₹{c['fee_per_year']:,.0f} per year "
                f"(₹{c['fee_per_year']*c['duration_years']:,.0f} total for {c['duration_years']} years). "
                f"Eligibility: {c['eligibility']}.")
    return ("I couldn't find fee details for that exact course name. We offer Computer Engineering, "
            "Information Technology, Mechanical Engineering, and Civil Engineering — could you specify one of these?")


def get_all_fees():
    rows = execute_query("SELECT * FROM courses", fetch=True)
    if not rows:
        return "Fee details aren't available right now. Please contact our admissions office."
    lines = [f"{r['course_name']}: ₹{r['fee_per_year']:,.0f}/year" for r in rows]
    return "Here's our fee structure per year:\n" + "\n".join(lines)


def get_placement_stats(course_name=None):
    if course_name:
        rows = execute_query(
            """SELECT c.course_name, p.avg_package_lpa, p.highest_package_lpa, p.placement_percent, p.top_recruiters, p.year
               FROM placements p JOIN courses c ON p.course_id = c.course_id
               WHERE LOWER(c.course_name) LIKE ? ORDER BY p.year DESC LIMIT 1""",
            (f"%{course_name.lower()}%",), fetch=True
        )
        if rows:
            r = rows[0]
            return (f"For {r['course_name']} ({r['year']}): placement rate {r['placement_percent']}%, "
                    f"average package ₹{r['avg_package_lpa']} LPA, highest package ₹{r['highest_package_lpa']} LPA. "
                    f"Top recruiters: {r['top_recruiters']}.")
    rows = execute_query(
        """SELECT c.course_name, p.avg_package_lpa, p.placement_percent
           FROM placements p JOIN courses c ON p.course_id = c.course_id
           WHERE p.year = (SELECT MAX(year) FROM placements)""",
        fetch=True
    )
    if not rows:
        return "Placement statistics aren't available right now. Please contact our Training & Placement Cell."
    lines = [f"{r['course_name']}: {r['placement_percent']}% placed, avg ₹{r['avg_package_lpa']} LPA" for r in rows]
    return "Latest placement stats by branch:\n" + "\n".join(lines)


@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "message is required"}), 400

    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    if "lead_flow" not in session:
        session["lead_flow"] = None
    if "lead_data" not in session:
        session["lead_data"] = {}

    # ---- If we're mid-way through collecting lead info, keep collecting ----
    if session["lead_flow"]:
        field = session["lead_flow"]
        value = user_message

        if field == "email" and not re.search(EMAIL_REGEX, value):
            return jsonify({"response": "That doesn't look like a valid email. Could you re-enter it?",
                             "intent": "provide_lead_info", "confidence": 1.0, "entities": {}})
        if field == "phone":
            phone_match = re.search(PHONE_REGEX, value)
            if not phone_match:
                return jsonify({"response": "Please enter a valid 10-digit phone number starting with 6-9.",
                                 "intent": "provide_lead_info", "confidence": 1.0, "entities": {}})
            value = phone_match.group()

        session["lead_data"][field] = value
        remaining = [f for f in LEAD_FIELDS if f not in session["lead_data"]]

        if remaining:
            session["lead_flow"] = remaining[0]
            session.modified = True
            return jsonify({"response": LEAD_PROMPTS[remaining[0]], "intent": "provide_lead_info",
                             "confidence": 1.0, "entities": {}})
        else:
            ld = session["lead_data"]
            execute_query(
                """INSERT INTO leads (name, email, phone, preferred_course, source_query)
                   VALUES (?, ?, ?, ?, ?)""",
                (ld["name"], ld["email"], ld["phone"], ld["preferred_course"], "chat_flow")
            )
            session["lead_flow"] = None
            session["lead_data"] = {}
            session.modified = True
            response = ("Thank you! I've saved your details — our admissions counselor will reach out to you "
                        "within 24 hours. Is there anything else I can help with?")
            execute_query(
                """INSERT INTO chat_logs (session_id, user_message, predicted_intent, confidence_score, bot_response, was_fallback)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (session["session_id"], user_message, "provide_lead_info", 1.0, response, False)
            )
            return jsonify({"response": response, "intent": "provide_lead_info", "confidence": 1.0, "entities": {}})

    # ---- Normal intent prediction ----
    tag, confidence = predict_intent(user_message)
    entities = extract_entities(user_message)

    if tag == "fee_query":
        response = get_course_fee(entities["course"]) if entities["course"] else get_all_fees()
    elif tag == "placements":
        response = get_placement_stats(entities["course"])
    elif tag == "provide_lead_info":
        session["lead_flow"] = "name"
        session["lead_data"] = {}
        session.modified = True
        response = get_static_response(tag)
    else:
        response = get_static_response(tag)

    execute_query(
        """INSERT INTO chat_logs (session_id, user_message, predicted_intent, confidence_score, bot_response, was_fallback)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (session["session_id"], user_message, tag, confidence, response, tag == "out_of_scope")
    )

    return jsonify({
        "response": response,
        "intent": tag,
        "confidence": round(confidence, 3),
        "entities": entities
    })
