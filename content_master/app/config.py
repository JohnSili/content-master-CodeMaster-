from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "ContentMaster"
    NEWS_API_KEY: str = "d4c9d3e4a2d0475d84647121e55f6d97"
    # DATABASE_URL: str
    # OPENAI_API_KEY: str
    
    class Config:
        env_file = ".env"

settings = Settings()