from dataclasses import dataclass
from typing import Optional, Dict, Set
from src.utils.config import DEFAULT_MODEL, VISION_MODEL

@dataclass
class ProcessingConfig:
    """Configuration for DocumentProcessor"""
    max_file_size: int = 100 * 1024 * 1024  # 100MB default
    text_extract_limit: int = 10000
    temperature: float = 0.0
    ollama_model: str = DEFAULT_MODEL
    vision_model: str = VISION_MODEL
    allowed_extensions: Optional[Set[str]] = None
    allowed_mime_types: Optional[Dict[str, Set[str]]] = None

    def __post_init__(self):
        if self.allowed_extensions is None:
            self.allowed_extensions = {
                '.pdf', '.docx', '.txt',
                '.jpg', '.jpeg', '.png'
            }
        if self.allowed_mime_types is None:
            self.allowed_mime_types = {
                '.pdf': {'application/pdf'},
                '.docx': {'application/vnd.openxmlformats-officedocument.wordprocessingml.document'},
                '.txt': {'text/plain', 'text/csv'},
                '.jpg': {'image/jpeg'},
                '.jpeg': {'image/jpeg'},
                '.png': {'image/png'},
            }