from flask import Blueprint, request, jsonify
from database.db_connection import execute_query

lead_bp = Blueprint("lead", __name__)


@lead_bp.route("/lead", methods=["POST"])
def save_lead():
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    course = (data.get("preferred_course") or "").strip()
    source_query = data.get("source_query", "manual_form")

    if not name or not email or not phone:
        return jsonify({"error": "name, email, and phone are required"}), 400

    execute_query(
        """INSERT INTO leads (name, email, phone, preferred_course, source_query)
           VALUES (?, ?, ?, ?, ?)""",
        (name, email, phone, course, source_query)
    )

    return jsonify({"message": "Thanks! Our admissions team will contact you shortly."}), 201


@lead_bp.route("/leads", methods=["GET"])
def list_leads():
    """Simple admin endpoint to view captured leads as JSON."""
    rows = execute_query("SELECT * FROM leads ORDER BY created_at DESC", fetch=True)
    leads = [dict(r) for r in rows]
    return jsonify(leads)
