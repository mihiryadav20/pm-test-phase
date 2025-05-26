import os
import requests # We'll need this to call the OpenRouter API
import json

# It's crucial to manage your OpenRouter API key securely.
# Use environment variables instead of hardcoding it
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")  # Fallback to hardcoded value for testing only
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions" # Common endpoint

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
    prompt_content += "\nFormat the report in a clear, professional structure with headings and bullet points where appropriate."
    return prompt_content

def generate_board_report(board_details_from_trello_api):
    """
    Uses OpenRouter API to generate a comprehensive report of the Trello board.
    'board_details_from_trello_api' is a tuple (board, lists) as returned by get_board_details.
    """
    if not OPENROUTER_API_KEY:
        return "Error: OPENROUTER_API_KEY is not set. Please set it as an environment variable."

    board_object, lists_with_cards = board_details_from_trello_api
    
    # Combine board object and lists into a single structure for the prompt helper
    combined_board_data = {
        "name": board_object.get("name"),
        "desc": board_object.get("desc"),
        "lists": lists_with_cards
    }

    prompt = _prepare_prompt_for_report(combined_board_data)

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    # Example payload for a chat completion model on OpenRouter
    # You might need to adjust the model name and other parameters.
    # Refer to OpenRouter documentation for specific model details.
    payload = {
        "model": "openai/gpt-3.5-turbo", # Example model, choose one available on OpenRouter
        "messages": [
            {"role": "system", "content": "You are an AI assistant that builds comprehensive reports for Trello boards. Your reports are detailed, analytical, and provide actionable insights."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        report = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        return report.strip() if report else "Could not generate a board report."

    except requests.exceptions.RequestException as e:
        print(f"Error calling OpenRouter API: {e}")
        return f"Error: Could not connect to OpenRouter API to generate report. {e}"
    except (KeyError, IndexError) as e:
        print(f"Error parsing OpenRouter API response: {e}")
        print(f"Response content: {response.text if 'response' in locals() else 'No response object'}")
        return "Error: Could not parse the report from OpenRouter API response."

if __name__ == '__main__':
    # Example usage (for testing this module directly)
    # This requires you to have OPENROUTER_API_KEY set as an environment variable
    # And to mock or provide actual board data.
    
    print("Testing agent.py directly...")
    if not OPENROUTER_API_KEY:
        print("Skipping test: OPENROUTER_API_KEY not set.")
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
