from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )

    # App
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str
    TOKEN_TIME_EXPIRATION_SECS: int


settings = Settings()
