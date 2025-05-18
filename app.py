from flask import Flask, redirect, url_for, request, jsonify, session
from requests_oauthlib import OAuth1Session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

# Trello OAuth 1.0 configuration
TRELLO_KEY = "your_trello_api_key"  # Replace with your Trello API Key
TRELLO_SECRET = "your_trello_app_secret"  # Replace with your Trello App Secret
REQUEST_TOKEN_URL = "https://trello.com/1/OAuthGetRequestToken"
AUTHORIZE_URL = "https://trello.com/1/OAuthAuthorizeToken"
ACCESS_TOKEN_URL = "https://trello.com/1/OAuthGetAccessToken"
CALLBACK_URI = "http://localhost:5000/callback"

@app.route("/")
def index():
    return """
    <h1>Trello OAuth Flask Demo</h1>
    <a href="/login">Login with Trello</a>
    """

@app.route("/login")
def login():
    # Step 1: Get request token
    oauth = OAuth1Session(TRELLO_KEY, client_secret=TRELLO_SECRET, callback_uri=CALLBACK_URI)
    try:
        fetch_response = oauth.fetch_request_token(REQUEST_TOKEN_URL)
        session["request_token"] = fetch_response.get("oauth_token")
        session["request_token_secret"] = fetch_response.get("oauth_token_secret")
        
        # Step 2: Redirect user to Trello for authorization
        authorization_url = f"{AUTHORIZE_URL}?oauth_token={fetch_response.get('oauth_token')}&scope=read,write&expiration=never&name=FlaskTrelloApp"
        return redirect(authorization_url)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/callback")
def callback():
    # Step 3: Get access token after user authorization
    oauth_token = request.args.get("oauth_token")
    oauth_verifier = request.args.get("oauth_verifier")
    
    if not oauth_token or not oauth_verifier:
        return jsonify({"error": "Missing oauth_token or oauth_verifier"}), 400
    
    # Rebuild OAuth session with stored request token and secret
    oauth = OAuth1Session(
        TRELLO_KEY,
        client_secret=TRELLO_SECRET,
        resource_owner_key=session.get("request_token"),
        resource_owner_secret=session.get("request_token_secret"),
        verifier=oauth_verifier
    )
    
    try:
        # Exchange request token for access token
        access_tokens = oauth.fetch_access_token(ACCESS_TOKEN_URL)
        session["access_token"] = access_tokens.get("oauth_token")
        session["access_token_secret"] = access_tokens.get("oauth_token_secret")
        
        # Step 4: Make an authenticated API call (e.g., get user's boards)
        trello = OAuth1Session(
            TRELLO_KEY,
            client_secret=TRELLO_SECRET,
            resource_owner_key=session["access_token"],
            resource_owner_secret=session["access_token_secret"]
        )
        response = trello.get("https://api.trello.com/1/members/me/boards")
        response.raise_for_status()
        boards = response.json()
        
        return jsonify({"boards": boards})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)