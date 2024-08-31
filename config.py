import os

import dotenv

# Load environment variables from.env file
dotenv.load_dotenv()

# Replace with your actual API endpoints
FUZZY_MATCH_API = os.getenv('FUZZY_MATCH_API')
TRANSLATE_API = os.getenv('TRANSLATE_API')
LANGUAGE_API = os.getenv('LANGUAGE_API')

# Get the bot token from environment variable
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
