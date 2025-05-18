from flask import Flask, redirect, url_for, request, jsonify, session, render_template_string
from requests_oauthlib import OAuth1Session
import os
import json
import uuid

app = Flask(__name__)
app.secret_key = "fixed_secret_key_for_testing_123456789"  # Fixed key for testing

# Directory for token storage
TOKEN_DIR = os.path.join(os.path.dirname(__file__), "tokens")
os.makedirs(TOKEN_DIR, exist_ok=True)

# Helper functions for token storage
def save_token(oauth_token, token_data):
    token_path = os.path.join(TOKEN_DIR, f"{oauth_token}.json")
    with open(token_path, "w") as f:
        json.dump(token_data, f)

def get_token(oauth_token):
    token_path = os.path.join(TOKEN_DIR, f"{oauth_token}.json")
    if os.path.exists(token_path):
        with open(token_path, "r") as f:
            return json.load(f)
    return None

# Trello configuration
TRELLO_KEY = "a2f217e66e60163384df3e891fd329a8"
TRELLO_SECRET = "904e785848d1994523d17337b16a4473da7a9747690587d76f1b78e1dfa3779f"
REQUEST_TOKEN_URL = "https://trello.com/1/OAuthGetRequestToken"
AUTHORIZE_URL = "https://trello.com/1/OAuthAuthorizeToken"
ACCESS_TOKEN_URL = "https://trello.com/1/OAuthGetAccessToken"
CALLBACK_URI = "http://localhost:5000/callback"

@app.route("/")
def index():
    if "access_token" in session:
        return redirect(url_for("dashboard"))
    return """
    <h1>Trello OAuth</h1>
    <a href="/login">Login with Trello</a>
    """

@app.route("/login")
def login():
    oauth = OAuth1Session(
        TRELLO_KEY,
        client_secret=TRELLO_SECRET,
        callback_uri=CALLBACK_URI
    )
    
    try:
        print("Fetching request token...")
        fetch_response = oauth.fetch_request_token(REQUEST_TOKEN_URL)
        if not fetch_response:
            print("Error: Failed to fetch request token")
            return jsonify({"error": "Failed to fetch request token"}), 500
            
        # Store tokens in file using oauth_token as the key
        oauth_token = fetch_response["oauth_token"]
        token_data = {
            "request_token": oauth_token,
            "request_token_secret": fetch_response["oauth_token_secret"]
        }
        save_token(oauth_token, token_data)
        print(f"Saved token data for: {oauth_token}")
        
        # Build authorization URL
        authorization_url = f"{AUTHORIZE_URL}?oauth_token={oauth_token}&scope=read,write&expiration=never&name=FlaskTrello"
        print(f"Redirecting to: {authorization_url}")
        return redirect(authorization_url)
    except Exception as e:
        print(f"Error in login: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/callback")
def callback():
    oauth_token = request.args.get("oauth_token")
    oauth_verifier = request.args.get("oauth_verifier")
    
    print(f"Callback received - oauth_token: {oauth_token}, oauth_verifier: {oauth_verifier}")
    
    if not oauth_token or not oauth_verifier:
        print("Error: Missing required parameters")
        return jsonify({"error": "Missing oauth_token or oauth_verifier"}), 400
        
    # Get tokens from file using oauth_token as the key
    token_data = get_token(oauth_token)
    if not token_data:
        print(f"Error: Could not find token data for oauth_token: {oauth_token}")
        return jsonify({"error": "Invalid oauth_token"}), 400
        
    request_token = token_data.get("request_token")
    request_token_secret = token_data.get("request_token_secret")
    
    if not request_token or not request_token_secret:
        print("Error: Missing token data")
        return jsonify({"error": "Invalid token data"}), 400

    # Verify the tokens match
    if oauth_token != request_token:
        print(f"Token mismatch: callback oauth_token ({oauth_token}) != request_token ({request_token})")
        return jsonify({"error": "Token mismatch"}), 400

    oauth = OAuth1Session(
        TRELLO_KEY,
        client_secret=TRELLO_SECRET,
        resource_owner_key=request_token,
        resource_owner_secret=request_token_secret,
        verifier=oauth_verifier
    )

    try:
        print("Fetching access token...")
        access_tokens = oauth.fetch_access_token(ACCESS_TOKEN_URL)
        if not access_tokens:
            print("Error: Failed to fetch access token")
            return jsonify({"error": "Failed to fetch access token"}), 500
            
        # Store access tokens securely
        session["access_token"] = access_tokens["oauth_token"]
        session["access_token_secret"] = access_tokens["oauth_token_secret"]
        print(f"Successfully stored access token: {session['access_token']}")
        
        return redirect(url_for("dashboard"))
    except Exception as e:
        print(f"Error in callback: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/dashboard")
def dashboard():
    if "access_token" not in session:
        return redirect(url_for("index"))
    
    trello = OAuth1Session(
        TRELLO_KEY,
        client_secret=TRELLO_SECRET,
        resource_owner_key=session["access_token"],
        resource_owner_secret=session["access_token_secret"]
    )

    try:
        print("Fetching boards...")
        response = trello.get("https://api.trello.com/1/members/me/boards?fields=name,id")
        response.raise_for_status()
        boards = response.json()
        print("Fetched boards:", [board["name"] for board in boards])
        
        return render_template_string("""
        <h1>Your Trello Boards</h1>
        <ul>
            {% for board in boards %}
                <li>{{ board.name }} (ID: {{ board.id }})</li>
            {% endfor %}
        </ul>
        <a href="/logout">Logout</a>
        """, boards=boards)
    except Exception as e:
        print(f"Dashboard error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/logout")
def logout():
    session.clear()
    print("Session cleared")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)