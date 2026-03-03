import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

# Dummy key for Mouser Order API
if not os.getenv("MOUSER_ORDER_API_KEY"):
    os.environ['MOUSER_ORDER_API_KEY'] = 'dummy_key_not_used'

@dataclass
class AppConfig:
    mouser_key: str = os.getenv("MOUSER_PART_API_KEY")
    snipe_url: str = os.getenv("SNIPE_URL", "http://localhost:8080/api/v1")
    snipe_token: str = os.getenv("SNIPE_IT_API_KEY")

    # default inventory settings
    category_id: int = int(os.getenv("DEFAULT_CATEGORY_ID", 1))
    location_id: int = int(os.getenv("DEFAULT_LOCATION_ID", 1))
    manufacturer_id: int = int(os.getenv("DEFAULT_MANUFACTURER_ID", 1))
    
    # hardware settings
    # Defaulting to 1 for the USB webcam, but allowing override via .env
    camera_index: int = int(os.getenv("CAMERA_INDEX", 0))