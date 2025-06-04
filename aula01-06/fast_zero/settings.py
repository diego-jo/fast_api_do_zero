from pydantic_settings import BaseSettings, SettingsConfigDict


# TODO: descobrir como definir valores default para as variáveis
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', enable_decoding='utf-8'
    )

    DATABASE_URL: str
