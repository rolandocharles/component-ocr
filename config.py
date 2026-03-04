import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class AppConfig:
    mouser_part_key: str = os.getenv("MOUSER_PART_API_KEY", "dummy_key_not_used")
    mouser_order_key: str = os.getenv("MOUSER_ORDER_API_KEY", "dummy_key_not_used")
    snipe_url: str = os.getenv("SNIPE_URL", "http://saber-lab.local/inventory/api/v1")
    snipe_token: str = os.getenv("SNIPE_IT_API_KEY", "dummy_key_not_used")

    # hardware settings
    camera_index: int = int(os.getenv("CAMERA_INDEX", 0))