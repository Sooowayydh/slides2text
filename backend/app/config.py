from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # Models
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    GEMINI_MODEL: str = "gemini-pro"
    
    # Other settings
    MAX_TOKENS: int = 150
    TEMPERATURE: float = 0.7
    
    # Processing settings
    PROCESSING_DELAY: float = 1.0  # seconds between API calls
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 