from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ionos_email: str
    ionos_password: SecretStr
    imap_host: str = "imap.ionos.de"
    imap_port: int = 993
    smtp_host: str = "smtp.ionos.de"
    smtp_port: int = 465
    api_key: SecretStr


@lru_cache
def get_settings() -> Settings:
    return Settings()
