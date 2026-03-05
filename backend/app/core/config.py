from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    app_name: str = "CityBrain AI"
    api_v1_prefix: str = "/v1"

    # Defaults (MVP)
    default_city: str = "ankara"
    default_radius_m: int = 800
    default_h3_res: int = 8

    model_config = SettingsConfigDict(env_prefix="CITYBRAIN_", env_file=".env")


settings = Settings()