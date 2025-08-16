from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Simple Memo App"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
