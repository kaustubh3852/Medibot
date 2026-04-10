from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
import os
import time

load_dotenv()

app = Flask(__name__)
CORS(app)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message")
        print("Message received:", user_message)
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        for attempt in range(5):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=user_message,
                    config={
                        "system_instruction": "You are MediBot, a helpful AI healthcare assistant. Give short, concise answers in 2-5 lines only based on situations. And give treatment also. Always recommend consulting a doctor for serious conditions."
                    }
                )
                return jsonify({"reply": response.text})
            except Exception as e:
                if "503" in str(e) and attempt < 4:
                    print(f"Attempt {attempt+1} failed, retrying...")
                    time.sleep(5)
                    continue
                raise e

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)