import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BOT_LANGUAGE_NAME = os.getenv("BOT_LANGUAGE_NAME", "English")
BOT_LANGUAGE_CODE = os.getenv("BOT_LANGUAGE_CODE", "en")

# OpenAI Configuration
OPENAI_API_BASE_URL = "https://api.openai.com/v1"
OPENAI_MODEL = "gpt-4o-mini-realtime-preview-2024-12-17"
