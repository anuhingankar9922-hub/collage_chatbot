import pickle
import os
import json
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "intent_classifier.pkl")
INTENTS_PATH = os.path.join(BASE_DIR, "data", "intents.json")

CONFIDENCE_THRESHOLD = 0.25

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

with open(INTENTS_PATH, "r", encoding="utf-8") as f:
    intents_data = json.load(f)

RESPONSE_MAP = {i["tag"]: i["responses"] for i in intents_data["intents"]}


def predict_intent(user_message: str):
    """Returns (tag, confidence)."""
    probs = model.predict_proba([user_message])[0]
    classes = model.classes_
    best_idx = probs.argmax()
    tag = classes[best_idx]
    confidence = float(probs[best_idx])

    if confidence < CONFIDENCE_THRESHOLD:
        return "out_of_scope", confidence

    return tag, confidence


def get_static_response(tag: str) -> str:
    responses = RESPONSE_MAP.get(tag, RESPONSE_MAP["out_of_scope"])
    return random.choice(responses)
