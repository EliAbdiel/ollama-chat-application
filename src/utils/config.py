import os


COMMANDS = {"Search", "Chat", "Summary"}

OLLAMA_API_KEY=os.environ.get("OLLAMA_SECRET_KEY")

OLLAMA_BASE_URL=os.environ.get("OLLAMA_BASE_URL")

DEFAULT_MODEL=os.environ.get("DEFAULT_MODEL")

VISION_MODEL=os.environ.get("VISION_MODEL")

ELEVENLABS_KEY=os.environ.get("ELEVENLABS_API_KEY")

DATABASE=os.environ.get("LOCAL_DATABASE")

CONTAINER = os.environ.get("CONTAINER_NAME")

STORAGE_ACCOUNT = os.environ.get("STORAGE_ACCOUNT_NAME")

STORAGE_SECRET = os.environ.get("STORAGE_KEY")