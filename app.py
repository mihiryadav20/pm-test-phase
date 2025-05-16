from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

OPENROUTER_API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-3.5-turbo",  # or any other model available via OpenRouter
        "messages": [
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 256
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        # The response format is similar to OpenAI's
        reply = data["choices"][0]["message"]["content"]
        return jsonify({"response": reply})
    else:
        return jsonify({"error": response.text}), response.status_code

if __name__ == "__main__":
    app.run(debug=True)
