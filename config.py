from dataclasses import dataclass

@dataclass
class AppConfig:
    # supplier (mouser with test API)
    mouser_key: str = "MOUSER_API_KEY"

    # inventory
    snipe_url: str = "http://localhost:8080/api/v1"
    snipe_token: str = "SNIPEIT_API_TOKEN"

    # default inventory settings
    category_id: int = 1
    location_id: int = 1
    manufacturer_id: int = 1