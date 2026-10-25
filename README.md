# College Enquiry Chatbot — Ready-to-Run Project

An end-to-end AI chatbot for college admissions enquiries: intent classification (TF-IDF + Logistic
Regression), entity extraction (regex), dynamic fee/placement lookups from SQLite, lead capture
(name/email/phone/course), and a web chat UI.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize the database (only needed once, or to reset it)
python database/db_setup.py

# 3. Train the intent classifier (only needed once, or after editing intents.json)
python chatbot/train_model.py

# 4. Run the app
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

## What's already done for you

- Database created and seeded with sample courses + placement stats (`database/college_chatbot.db`)
- Model already trained on 19 intents / 114 sample phrases (`chatbot/model/intent_classifier.pkl`)
- Full chat UI wired up and working end-to-end

If you just want to run it as-is, you can skip straight to step 4 — steps 2 and 3 have already been
run once during setup, but re-running them is safe (harmless) if you want a clean slate.

## Project Structure

```
college_chatbot/
├── app.py                     # Flask entry point
├── database/
│   ├── db_setup.py            # Creates + seeds tables (run once)
│   ├── db_connection.py       # DB helper
│   └── college_chatbot.db     # SQLite file
├── chatbot/
│   ├── data/intents.json      # Training data (19 intents)
│   ├── train_model.py         # Trains the classifier
│   ├── model/intent_classifier.pkl
│   ├── predict.py             # Loads model, predicts intent
│   └── entity_extractor.py    # Extracts email/phone/course from text
├── routes/
│   ├── chat_routes.py         # POST /api/chat
│   └── lead_routes.py         # POST /api/lead, GET /api/leads
├── static/{css,js}/           # Frontend
└── templates/index.html       # Chat UI
```

## Key Features

1. **Ask about fees** — "What is the fee for Computer Engineering?" → looked up live from the `courses` table.
2. **Ask about placements** — "Placement stats for IT?" → looked up live from the `placements` table.
3. **Lead capture flow** — say "I want to share my details" and the bot will walk you through
   collecting Name → Email → Phone → Preferred Course, then save it to the `leads` table.
4. **Fallback handling** — anything off-topic or low-confidence routes to the `out_of_scope` intent
   instead of a wrong answer.
5. **Conversation logging** — every message is logged to `chat_logs` with predicted intent and
   confidence score, useful for your project report's accuracy evaluation section.

## Viewing captured leads

Visit **http://127.0.0.1:5000/api/leads** while the app is running to see all captured leads as JSON
(useful for a live demo — "look, it's actually saving to the database").

## Retraining after editing intents.json

If you add/edit intents in `chatbot/data/intents.json`, just re-run:
```bash
python chatbot/train_model.py
```
and restart the Flask app.

## For your project report

- **Accuracy evaluation**: split `intents.json` patterns into train/test and compute a confusion
  matrix — the current 114-sample dataset across 19 intents is a good starting point to expand from.
- **Tech justification**: TF-IDF + Logistic Regression was chosen over Rasa/Dialogflow for faster
  setup, full code transparency (good for a viva), and no external service dependency.
