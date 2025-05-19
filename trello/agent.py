import os
import requests # We'll need this to call the OpenRouter API
import json

# It's crucial to manage your OpenRouter API key securely.
# Avoid hardcoding it. Use environment variables or a config file.
OPENROUTER_API_KEY = "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"  # Directly set for testing
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions" # Common endpoint

def _prepare_prompt_for_summary(board_data):
    """
    Prepares a detailed prompt for the LLM to summarize board activity.
    """
    board_name = board_data.get('name', 'N/A')
    board_desc = board_data.get('desc', 'No description')
    lists = board_data.get('lists', [])

    prompt_content = f"Analyze the following Trello board data and provide a concise summary of its activity and content.\n\n"
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
    
    prompt_content += "\nBased on this data, please provide a summary."
    return prompt_content

def summarize_board_activity(board_details_from_trello_api):
    """
    Uses OpenRouter API to generate a summary of the Trello board.
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

    prompt = _prepare_prompt_for_summary(combined_board_data)

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
            {"role": "system", "content": "You are an AI assistant that summarizes Trello board content."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        summary = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        return summary.strip() if summary else "Could not generate a summary."

    except requests.exceptions.RequestException as e:
        print(f"Error calling OpenRouter API: {e}")
        return f"Error: Could not connect to OpenRouter API. {e}"
    except (KeyError, IndexError) as e:
        print(f"Error parsing OpenRouter API response: {e}")
        print(f"Response content: {response.text if 'response' in locals() else 'No response object'}")
        return "Error: Could not parse the summary from OpenRouter API response."

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
        
        # The summarize_board_activity function expects a tuple (board_object, lists_with_cards)
        # So we adapt the mock_board_data
        mock_board_object = {"name": mock_board_data["name"], "desc": mock_board_data["desc"]}
        mock_lists_with_cards = mock_board_data["lists"]
        
        summary = summarize_board_activity((mock_board_object, mock_lists_with_cards))
        print("\nGenerated Summary:")
        print(summary)
