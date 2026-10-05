# here we are creating the setting instance to read the .env file when the app starts , it validates that all the variables defined in this Setting class are present in .env , if not then app crashes on start-up

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn

class Settings(BaseSettings):
    #App Settings
    PROJECT_NAME:str = "Test-Series-API"
    API_V1:str = "/api/v1"

    # Database Settings
    DATABASE_URL:str

    # Security Settings
    # SECRET_KEY: str
    #ACCESS_TOKEN_EXPIRE_MINUTES: int

    # tell pydantic to read from the .env file in the root directory
    model_config=SettingsConfigDict(env_file=".env",env_file_encoding="utf-8",extra="ignore")

setting=Settings()

    


