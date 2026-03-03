import requests

def update_snipeit(cfg, part_data):
    """Creates a component in Snipe-IT using the provided config object."""
    headers = {
        "Authorization": f"Bearer {cfg.snipe_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "name": part_data.get('ManufacturerPartNumber', 'Unknown Part'),
        "category_id": cfg.category_id,
        "qty": 1,
        "location_id": cfg.location_id,
        "manufacturer_id": cfg.manufacturer_id,
        "notes": f"Auto-added from Mouser. Desc: {part_data.get('Description')}"
    }
    
    try:
        response = requests.post(f"{cfg.snipe_url}/components", headers=headers, json=payload)
        return response.status_code
    except Exception as e:
        print(f"Snipe-IT API Error: {e}")
        return None