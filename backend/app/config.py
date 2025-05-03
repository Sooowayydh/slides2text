from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "models/gemini-2.5-flash-preview-04-17"
    
    # Processing settings
    PROCESSING_DELAY: float = 1.0  # seconds between API calls
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 