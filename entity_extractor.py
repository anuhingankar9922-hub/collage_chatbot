import re

EMAIL_REGEX = r"[\w\.-]+@[\w\.-]+\.\w+"
PHONE_REGEX = r"\b[6-9]\d{9}\b"

KNOWN_COURSES = [
    "computer engineering", "computer science", "information technology",
    "mechanical engineering", "civil engineering",
    "mechanical", "civil", "cse", "it", "computer", "mech"
]


def extract_entities(text: str) -> dict:
    text_lower = text.lower()
    entities = {"email": None, "phone": None, "course": None}

    email_match = re.search(EMAIL_REGEX, text)
    if email_match:
        entities["email"] = email_match.group()

    phone_match = re.search(PHONE_REGEX, text)
    if phone_match:
        entities["phone"] = phone_match.group()

    for course in KNOWN_COURSES:
        if course in text_lower:
            entities["course"] = course
            break

    return entities
