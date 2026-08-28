from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "GANDOM"
    debug: bool = False
    secret_key: str
    access_token_minutes: int = 30
    refresh_token_days: int = 30
    database_url: str
    redis_url: str
    cors_origins: str = "http://localhost:5173"
    default_currency: str = "IRR"
    admin_phone: str
    admin_password: str
    payment_callback_base: str = "http://localhost:8000/api/v1/payments/callback"
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

settings = Settings()
