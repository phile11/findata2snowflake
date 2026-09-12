from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    apikey: str

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore" 
    )

# Instantiate the settings object for use across this application
settings = Settings()