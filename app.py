from flask import Flask, render_template
from routes.chat_routes import chat_bp
from routes.lead_routes import lead_bp

app = Flask(__name__)
app.secret_key = "college-chatbot-dev-secret-change-in-production"

app.register_blueprint(chat_bp, url_prefix="/api")
app.register_blueprint(lead_bp, url_prefix="/api")


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
