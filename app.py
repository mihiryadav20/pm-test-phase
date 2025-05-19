from flask import Flask, redirect, url_for, request, jsonify, session, render_template_string
import os

# Import our custom modules
from trello.api import (
    get_request_token, get_authorization_url, get_access_token,
    get_trello_client, get_boards, get_board_details
)
from trello.templates import INDEX_TEMPLATE, DASHBOARD_TEMPLATE, BOARD_TEMPLATE

app = Flask(__name__)
app.secret_key = "fixed_secret_key_for_testing_123456789"  # Fixed key for testing

@app.route("/")
def index():
    """Home page with login link"""
    if "access_token" in session:
        return redirect(url_for("dashboard"))
    return render_template_string(INDEX_TEMPLATE)

@app.route("/login")
def login():
    """Initiate OAuth flow with Trello"""
    try:
        # Get request token and authorization URL
        oauth_token, _ = get_request_token()
        authorization_url = get_authorization_url(oauth_token)
        
        print(f"Redirecting to: {authorization_url}")
        return redirect(authorization_url)
    except Exception as e:
        print(f"Error in login: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/callback")
def callback():
    """Handle OAuth callback from Trello"""
    oauth_token = request.args.get("oauth_token")
    oauth_verifier = request.args.get("oauth_verifier")
    
    print(f"Callback received - oauth_token: {oauth_token}, oauth_verifier: {oauth_verifier}")
    
    if not oauth_token or not oauth_verifier:
        print("Error: Missing required parameters")
        return jsonify({"error": "Missing oauth_token or oauth_verifier"}), 400
    
    try:
        # Exchange request token for access token
        access_token, access_token_secret = get_access_token(oauth_token, oauth_verifier)
        
        # Store access tokens in session
        session["access_token"] = access_token
        session["access_token_secret"] = access_token_secret
        print(f"Stored access token in session: {access_token}")
        
        return redirect(url_for("dashboard"))
    except Exception as e:
        print(f"Error in callback: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/dashboard")
def dashboard():
    """Show user's Trello boards"""
    if "access_token" not in session:
        return redirect(url_for("index"))
    
    try:
        # Get Trello client and fetch boards
        trello = get_trello_client(session["access_token"], session["access_token_secret"])
        boards = get_boards(trello)
        print("Fetched boards:", [board["name"] for board in boards])
        
        return render_template_string(DASHBOARD_TEMPLATE, boards=boards)
    except Exception as e:
        print(f"Dashboard error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/board/<board_id>")
def view_board(board_id):
    """Show details of a specific Trello board"""
    if "access_token" not in session:
        return redirect(url_for("index"))
    
    try:
        # Get Trello client and fetch board details
        trello = get_trello_client(session["access_token"], session["access_token_secret"])
        board, lists = get_board_details(trello, board_id)
        
        return render_template_string(BOARD_TEMPLATE, board=board, lists=lists)
    except Exception as e:
        print(f"Board view error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/logout")
def logout():
    """Log out user by clearing session"""
    session.clear()
    print("Session cleared")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)