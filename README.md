# Trello Board Manager

A Flask application that integrates with Trello using OAuth and provides AI-powered board summaries using OpenRouter API.

## Setup Instructions

### Prerequisites
- Python 3.7+
- Trello account
- OpenRouter account (for AI summaries)

### Configuration

#### 1. Trello API Configuration

1. Go to https://trello.com/app-key and log in with your Trello account
2. You'll see your API Key on that page
3. Click on "Generate a new Secret" to get your API Secret
4. **Important:** Under "Allowed Origins", add `http://localhost:5001` to enable OAuth callbacks

#### 2. Environment Variables

Create a `.env` file in the root directory with the following variables:

```
TRELLO_KEY=your_trello_api_key
TRELLO_SECRET=your_trello_api_secret
TRELLO_CALLBACK_URI=http://localhost:5001/callback
OPENROUTER_API_KEY=your_openrouter_api_key
```

Alternatively, you can set these environment variables in your system.

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python app.py
   ```
4. Open your browser and navigate to `http://localhost:5001`

## Troubleshooting

### OAuth Issues

If you encounter the error "Invalid return_url. The return URL should match the application's allowed origins", make sure:

1. You've added `http://localhost:5001` to the "Allowed Origins" in your Trello API settings
2. Your `TRELLO_CALLBACK_URI` matches exactly what's configured in Trello

### API Key Issues

For security, the application uses environment variables for API keys. If you're testing locally and haven't set up environment variables, the code will fall back to hardcoded values, but this is not recommended for production.
