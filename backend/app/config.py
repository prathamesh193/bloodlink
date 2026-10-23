"""Application settings, read from environment variables (see .env.example).

Policy values are educational parameters, not medical rules (requirements section 6).
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://bloodlink:change-me@localhost:5432/bloodlink"
    secret_key: str = "change-me"

    # Policy parameters
    donor_min_age: int = 18
    donor_max_age: int = 65
    min_days_between_donations: int = 90
    red_cells_shelf_life_days: int = 42
    plasma_shelf_life_days: int = 365
    max_units_per_request: int = 10
    expiry_warning_days: int = 7
    low_stock_threshold: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()
