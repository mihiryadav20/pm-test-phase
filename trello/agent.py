import os
import requests
import json
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# It's crucial to manage API keys securely.
# Use environment variables instead of hardcoding them
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def _prepare_prompt_for_report(board_data):
    """
    Prepares a detailed prompt for the LLM to build a comprehensive report of the board.
    """
    board_name = board_data.get('name', 'N/A')
    board_desc = board_data.get('desc', 'No description')
    lists = board_data.get('lists', [])

    prompt_content = f"Analyze the following Trello board data and build a comprehensive report.\n\n"
    prompt_content += f"Board Name: {board_name}\n"
    prompt_content += f"Board Description: {board_desc}\n\n"

    if not lists:
        prompt_content += "The board has no lists or cards.\n"
        return prompt_content

    prompt_content += "Board Lists and Cards:\n"
    for lst in lists:
        list_name = lst.get('name', 'Unnamed List')
        prompt_content += f"\nList: {list_name}\n"
        cards = lst.get('cards', [])
        if not cards:
            prompt_content += "  - This list has no cards.\n"
        else:
            for card in cards:
                card_name = card.get('name', 'Unnamed Card')
                card_desc = card.get('desc', '')
                card_due = card.get('due', 'No due date')
                labels = [label.get('name', 'N/A') for label in card.get('labels', [])]
                members = [member.get('fullName', 'N/A') for member in card.get('members', [])]

                prompt_content += f"  - Card: {card_name}\n"
                if card_desc:
                    prompt_content += f"    Description: {card_desc}\n"
                prompt_content += f"    Due Date: {card_due}\n"
                if labels:
                    prompt_content += f"    Labels: {', '.join(labels)}\n"
                if members:
                    prompt_content += f"    Assigned Members: {', '.join(members)}\n"
    
    prompt_content += "\nBased on this data, please build a comprehensive report that includes:\n"  
    prompt_content += "1. Overall board status and progress\n"
    prompt_content += "2. Key metrics (number of cards in each list, completion percentage)\n"
    prompt_content += "3. Task distribution among team members\n"
    prompt_content += "4. Upcoming deadlines and priority items\n"
    prompt_content += "5. Recommendations for improving workflow or addressing bottlenecks\n"
    prompt_content += "\nIMPORTANT: Format the report in a clear, professional structure with plain text headings. DO NOT use markdown formatting like **, ##, or any other markdown syntax. The report should look like a natural document without any markdown formatting."
    return prompt_content

def _clean_markdown_formatting(text):
    """
    Removes markdown formatting from text to make it look more natural.
    """
    # Remove markdown headers (## and similar)
    text = re.sub(r'^\s*#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Remove bold/italic formatting (**text** or *text*)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    
    # Remove backticks (`code`)
    text = re.sub(r'`(.+?)`', r'\1', text)
    
    # Remove markdown links [text](url) -> text
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    
    return text

def generate_board_report(board_details_from_trello_api):
    """
    Uses Google's Gemini API to generate a comprehensive report of the Trello board.
    'board_details_from_trello_api' is a tuple (board, lists) as returned by get_board_details.
    """
    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY is not set. Please set it as an environment variable."

    board_object, lists_with_cards = board_details_from_trello_api
    
    # Combine board object and lists into a single structure for the prompt helper
    combined_board_data = {
        "name": board_object.get("name"),
        "desc": board_object.get("desc"),
        "lists": lists_with_cards
    }

    prompt = _prepare_prompt_for_report(combined_board_data)

    # Construct the URL with API key
    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    
    headers = {
        "Content-Type": "application/json"
    }

    # Payload structure for Gemini API based on the provided curl example
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "You are an AI assistant that builds comprehensive reports for Trello boards. Your reports are detailed, analytical, and provide actionable insights. IMPORTANT: Your reports must be formatted in plain text without any markdown formatting (no **, ##, or other markdown syntax). Use plain text headings and formatting only.\n\n" + prompt
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        response_data = response.json()
        # Extract text from Gemini API response
        if 'candidates' in response_data and len(response_data['candidates']) > 0:
            candidate = response_data['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                parts = candidate['content']['parts']
                if parts and 'text' in parts[0]:
                    # Clean any markdown formatting that might still be present
                    report_text = parts[0]['text'].strip()
                    clean_report = _clean_markdown_formatting(report_text)
                    return clean_report
        
        print(f"Unexpected response structure: {response.text}")
        return "Could not generate a board report due to unexpected API response structure."

    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        return f"Error: Could not connect to Gemini API to generate report. {e}"
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Error parsing Gemini API response: {e}")
        print(f"Response content: {response.text if 'response' in locals() else 'No response object'}")
        return "Error: Could not parse the report from Gemini API response."

if __name__ == '__main__':
    # Example usage (for testing this module directly)
    # This requires you to have GEMINI_API_KEY set as an environment variable
    # And to mock or provide actual board data.
    
    print("Testing agent.py directly...")
    if not GEMINI_API_KEY:
        print("Skipping test: GEMINI_API_KEY not set.")
    else:
        mock_board_data = {
            "name": "Project Alpha",
            "desc": "This is a project to develop a new app.",
            "lists": [
                {
                    "name": "To Do",
                    "cards": [
                        {"name": "Setup project", "desc": "Initial setup tasks", "due": "2024-01-10", "labels": [{"name":"Urgent"}], "members": [{"fullName": "Alice"}]},
                        {"name": "Design UI", "desc": "Create mockups", "due": "2024-01-15", "labels": [], "members": [{"fullName": "Bob"}]}
                    ]
                },
                {
                    "name": "In Progress",
                    "cards": [
                        {"name": "Develop API", "desc": "Build backend endpoints", "due": "2024-02-01", "labels": [{"name":"Backend"}], "members": [{"fullName": "Alice"}, {"fullName": "Charlie"}]}
                    ]
                },
                {
                    "name": "Done",
                    "cards": [
                        {"name": "Requirement gathering", "desc": "", "due": None, "labels": [], "members": []}
                    ]
                }
            ]
        }
        
        # The generate_board_report function expects a tuple (board_object, lists_with_cards)
        # So we adapt the mock_board_data
        mock_board_object = {"name": mock_board_data["name"], "desc": mock_board_data["desc"]}
        mock_lists_with_cards = mock_board_data["lists"]
        
        report = generate_board_report((mock_board_object, mock_lists_with_cards))
        print("\nGenerated Board Report:")
        print(report)
