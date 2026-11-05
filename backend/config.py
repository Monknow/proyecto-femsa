from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  postgre_uri: str
  allowed_origins: list[str] = [""]
  environment: str = ""

  model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()