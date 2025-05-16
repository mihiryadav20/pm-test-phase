from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# OpenRouter API configuration
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = "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"

@app.route("/chat", methods=["POST"])
def chat():
    # Get user input from the request
    data = request.get_json()
    user_prompt = data.get("prompt", "Hello, how can I assist you today?")

    # Prepare headers
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",  # Optional
        "X-Title": "Flask OpenRouter App"  # Optional
    }

    # Prepare payload
    payload = {
        "model": "meta-llama/llama-3-8b-instruct",  # Free-tier model
        "messages": [{"role": "user", "content": user_prompt}],
        "max_tokens": 100,
        "temperature": 0.7
    }

    # Debug: Print headers, auth header, and payload
    print("Headers:", headers)
    print("Authorization Header:", headers["Authorization"])
    print("Payload:", payload)

    try:
        # Make POST request to OpenRouter
        response = requests.post(OPENROUTER_API_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raise error for bad status
        result = response.json()
        model_response = result["choices"][0]["message"]["content"]
        return jsonify({"response": model_response})

    except requests.exceptions.HTTPError as e:
        print("HTTP Error:", response.text)  # Log detailed error
        return jsonify({"error": str(e), "details": response.text}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return """
    <h1>OpenRouter Flask Demo</h1>
    <form method="POST" action="/chat">
        <input type="text" name="prompt" placeholder="Enter your prompt">
        <button type="submit">Send</button>
    </form>
    """

if __name__ == "__main__":
    app.run(debug=True)