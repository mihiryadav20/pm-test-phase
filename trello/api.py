from requests_oauthlib import OAuth1Session
import os
import json

# Trello configuration
TRELLO_KEY = "a2f217e66e60163384df3e891fd329a8"
TRELLO_SECRET = "904e785848d1994523d17337b16a4473da7a9747690587d76f1b78e1dfa3779f"
REQUEST_TOKEN_URL = "https://trello.com/1/OAuthGetRequestToken"
AUTHORIZE_URL = "https://trello.com/1/OAuthAuthorizeToken"
ACCESS_TOKEN_URL = "https://trello.com/1/OAuthGetAccessToken"
CALLBACK_URI = "http://localhost:5000/callback"

# Directory for token storage
TOKEN_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tokens")
os.makedirs(TOKEN_DIR, exist_ok=True)

def save_token(oauth_token, token_data):
    """Save token data to a file using oauth_token as the key"""
    token_path = os.path.join(TOKEN_DIR, f"{oauth_token}.json")
    with open(token_path, "w") as f:
        json.dump(token_data, f)

def get_token(oauth_token):
    """Retrieve token data from a file using oauth_token as the key"""
    token_path = os.path.join(TOKEN_DIR, f"{oauth_token}.json")
    if os.path.exists(token_path):
        with open(token_path, "r") as f:
            return json.load(f)
    return None

def get_request_token():
    """Get a request token from Trello"""
    oauth = OAuth1Session(
        TRELLO_KEY,
        client_secret=TRELLO_SECRET,
        callback_uri=CALLBACK_URI
    )
    
    fetch_response = oauth.fetch_request_token(REQUEST_TOKEN_URL)
    oauth_token = fetch_response["oauth_token"]
    
    # Store tokens in file
    token_data = {
        "request_token": oauth_token,
        "request_token_secret": fetch_response["oauth_token_secret"]
    }
    save_token(oauth_token, token_data)
    
    return oauth_token, fetch_response["oauth_token_secret"]

def get_authorization_url(oauth_token):
    """Get the authorization URL for Trello"""
    return f"{AUTHORIZE_URL}?oauth_token={oauth_token}&scope=read,write&expiration=never&name=FlaskTrello"

def get_access_token(oauth_token, oauth_verifier):
    """Get an access token from Trello"""
    # Get tokens from file
    token_data = get_token(oauth_token)
    if not token_data:
        raise ValueError(f"Could not find token data for oauth_token: {oauth_token}")
        
    request_token = token_data.get("request_token")
    request_token_secret = token_data.get("request_token_secret")
    
    if not request_token or not request_token_secret:
        raise ValueError("Invalid token data")

    # Verify the tokens match
    if oauth_token != request_token:
        raise ValueError(f"Token mismatch: callback oauth_token ({oauth_token}) != request_token ({request_token})")

    oauth = OAuth1Session(
        TRELLO_KEY,
        client_secret=TRELLO_SECRET,
        resource_owner_key=request_token,
        resource_owner_secret=request_token_secret,
        verifier=oauth_verifier
    )
    
    access_tokens = oauth.fetch_access_token(ACCESS_TOKEN_URL)
    return access_tokens["oauth_token"], access_tokens["oauth_token_secret"]

def get_trello_client(access_token, access_token_secret):
    """Get a Trello client using access tokens"""
    return OAuth1Session(
        TRELLO_KEY,
        client_secret=TRELLO_SECRET,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret
    )

def get_boards(trello):
    """Get all boards for the authenticated user"""
    response = trello.get("https://api.trello.com/1/members/me/boards?fields=name,id")
    response.raise_for_status()
    return response.json()

def get_board_details(trello, board_id):
    """Get details for a specific board"""
    # Fetch board details
    board_response = trello.get(f"https://api.trello.com/1/boards/{board_id}?fields=name,desc,url")
    board_response.raise_for_status()
    board = board_response.json()
    
    # Fetch lists on the board
    lists_response = trello.get(f"https://api.trello.com/1/boards/{board_id}/lists?fields=name,id")
    lists_response.raise_for_status()
    lists = lists_response.json()
    
    # Fetch cards for each list
    for trello_list in lists:
        cards_response = trello.get(f"https://api.trello.com/1/lists/{trello_list['id']}/cards?fields=name,desc,due,labels,idMembers")
        cards_response.raise_for_status()
        trello_list['cards'] = cards_response.json()
        
        # Get member details for each card
        for card in trello_list['cards']:
            if card.get('idMembers'):
                card['members'] = []
                for member_id in card['idMembers']:
                    member_response = trello.get(f"https://api.trello.com/1/members/{member_id}?fields=fullName,username")
                    member_response.raise_for_status()
                    card['members'].append(member_response.json())
    
    return board, lists
