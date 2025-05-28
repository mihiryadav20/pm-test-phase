# Trello Board Manager

A Flask application that integrates with Trello using OAuth and provides AI-powered board summaries using Google's Gemini API.

## Setup Instructions

### Prerequisites
- Python 3.7+
- Trello account
- Google Gemini API key (for AI summaries)

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
GEMINI_API_KEY=your_gemini_api_key
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

## Deployment Instructions

This application can be deployed to various cloud platforms. Here are instructions for deploying to Netlify:

### Deploying to Netlify

1. Make sure you have updated the `.env` file with production values:
   - Set `TRELLO_CALLBACK_URI` to your production URL (e.g., `https://your-app-name.netlify.app/callback`)
   - Ensure all API keys are properly set

2. Add your production URL to Trello's allowed origins in your Trello API settings

3. Create a `netlify.toml` file in the root directory with the following content:
   ```toml
   [build]
     command = "pip install -r requirements.txt"
     publish = "."

   [build.environment]
     PYTHON_VERSION = "3.9"

   [dev]
     command = "gunicorn app:app"
     port = 5001
     publish = "."
   ```

4. Deploy your application using the Netlify CLI or by connecting your repository to Netlify

5. Set environment variables in the Netlify dashboard under Site settings > Build & deploy > Environment

## Troubleshooting

### OAuth Issues

If you encounter the error "Invalid return_url. The return URL should match the application's allowed origins", make sure:

1. You've added your application URL to the "Allowed Origins" in your Trello API settings
2. Your `TRELLO_CALLBACK_URI` matches exactly what's configured in Trello

### API Key Issues

For security, the application uses environment variables for API keys. Make sure all required environment variables are set in your deployment environment. Never use hardcoded API keys in production.
