"""
Trains a TF-IDF + Logistic Regression intent classifier
and saves the model to chatbot/model/intent_classifier.pkl
"""
import json
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTENTS_PATH = os.path.join(BASE_DIR, "data", "intents.json")
MODEL_DIR = os.path.join(BASE_DIR, "model")
os.makedirs(MODEL_DIR, exist_ok=True)


def load_training_data():
    with open(INTENTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    X, y = [], []
    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            X.append(pattern)
            y.append(intent["tag"])
    return X, y


def train_and_save():
    X, y = load_training_data()

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=1)),
        ("clf", LogisticRegression(max_iter=2000, C=15))
    ])
    pipeline.fit(X, y)

    with open(os.path.join(MODEL_DIR, "intent_classifier.pkl"), "wb") as f:
        pickle.dump(pipeline, f)

    print(f"Model trained on {len(X)} samples across {len(set(y))} intents.")
    print("Saved to chatbot/model/intent_classifier.pkl")


if __name__ == "__main__":
    train_and_save()
