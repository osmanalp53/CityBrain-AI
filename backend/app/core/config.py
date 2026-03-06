from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # =========================
    # APP
    # =========================
    app_name: str = "CityBrain AI"
    api_v1_prefix: str = "/v1"

    # =========================
    # DEFAULTS
    # =========================
    default_city: str = "ankara"

    default_radius_m: int = 800
    default_h3_res: int = 7

    # scoring radius
    park_radius_m: int = 800
    metro_radius_m: int = 1200
    hospital_radius_m: int = 1500

    # =========================
    # BBOX
    # =========================
    # (min_lon, min_lat, max_lon, max_lat)
    ankara_bbox: tuple[float, float, float, float] = (
        32.60,
        39.86,
        32.95,
        40.00,
    )

    # =========================
    # ENV CONFIG
    # =========================
    model_config = SettingsConfigDict(
        env_prefix="CITYBRAIN_",
        env_file=".env",
    )


settings = Settings()