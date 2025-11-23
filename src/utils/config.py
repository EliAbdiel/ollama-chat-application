import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_API_KEY=os.environ["OLLAMA_SECRET_KEY"]
OLLAMA_BASE_URL=os.environ["OLLAMA_BASE_URL"]
DEFAULT_MODEL=os.environ["DEFAULT_MODEL"]
VISION_MODEL=os.environ["VISION_MODEL"]

ELEVENLABS_KEY=os.environ["ELEVENLABS_API_KEY"]

DATABASE=os.environ["LOCAL_DATABASE"]

CONTAINER = os.environ["CONTAINER_NAME"]
STORAGE_ACCOUNT = os.environ["STORAGE_ACCOUNT_NAME"]
STORAGE_SECRET = os.environ["STORAGE_KEY"]