import requests
import re
import json
import random

def print_full_search_output(part_data):
    print("\n" + "="*55)
    print(f" DEBUG: FULL DATA FOR {part_data.get('MouserPartNumber', 'SELECTED PART')}")
    print("="*55)
    print(json.dumps(part_data, indent=4))
    print("="*55 + "\n")

def filter_ocr(ocr_texts: list) -> list:
    """
    Filters raw OCR text to find likely electronic component part numbers.
    """
    candidates = []
    
    # patterns:
    # electrical values
    units_pattern = re.compile(
        r'^\d+(?:\.\d+)?\s*(?:uF|pF|nF|mF|V|mV|A|mA|Ohm|kOhm|MHz|Hz|W|mW|C|%)\b', 
        re.IGNORECASE
    )
    # common prefixes
    prefix_pattern = re.compile(
        r'^(?:MFG P/N|MOUSER P/N|P/N|QTY|DESC|COO|LINE ITEM|LOT)\s*[:\-]?\s*', 
        re.IGNORECASE
    )
    # exact words to ignore
    ignore_words = {
        'MADE', 'IN', 'CHINA', 'TAIWAN', 'MALAYSIA', 'PHILIPPINES', 
        'MEXICO', 'LOT', 'REV', 'VER', 'DATE', 'MOUSER', 'WWW', 'COM',
        'ELECTRONICS', 'CUST', 'DESC', 'ROHS', 'COMPLIANT', 'QTY', 'COO',
        'MFG', 'PN', 'LINE', 'ITEM', 'BARCODE'
    }

    # filtering loop
    for text in ocr_texts:
        text_upper = text.strip().upper()
        if not text_upper:
            continue

        # 1. prefixes
        text_upper = prefix_pattern.sub('', text_upper)
        # 2. colons to spaces, then split into tokens
        tokens = text_upper.replace(':', ' ').split()
        # 3. space-removed version
        if len(tokens) > 1:
            tokens.append("".join(tokens))

        for token in tokens:
            if not token:
                continue
                
            if token in ignore_words:
                continue
                
            if units_pattern.search(token):
                continue
                
            # length check (skip tiny garbage and massively long strings)
            if len(token) < 3 or len(token) > 30:
                continue
                
            # must be a mix of letters and numbers, OR a pure number >= 4 digits
            has_letter = any(c.isalpha() for c in token)
            has_number = any(c.isdigit() for c in token)
            if (has_letter and has_number) or (not has_letter and has_number and len(token) >= 4):
                # sanitation
                clean_part = re.sub(r'[^A-Z0-9\-+]', '', token)
                # prevent duplicates
                if len(clean_part) >= 4 and clean_part not in candidates:
                    candidates.append(clean_part)
                    
    return candidates

def generate_random_asset_tag():
    """
    Generates a random 5-digit asset tag
    """
    asset_tag = random.randint(10000, 99999)
    print(f"Generated Asset Tag: {asset_tag}")
    return asset_tag

def update_snipeit(cfg, part_data):
    """
    Creates a new hardware Asset in Snipe-IT using the part data and maps them to the 'Electronic Components' custom fieldset.
    """
    headers = {
        "Authorization": f"Bearer {cfg.snipe_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {
        "name": part_data.get("ManufacturerPartNumber", "Unknown Part"), 
        "model_id": 2,  # assuming 'Electronic Components' model has ID 2
        "asset_tag": generate_random_asset_tag(),
        "status_id": 2,  # assuming 'Ready To Deploy' status has ID 2
        
        "_snipeit_manufacturer_product_number_8": part_data.get("ManufacturerPartNumber", ""),
        "_snipeit_component_category_9": part_data.get("Category", ""),
        "_snipeit_description_10": part_data.get("Description", ""),
        "_snipeit_datasheet_11": part_data.get("DataSheetUrl", ""),
        "_snipeit_manufacturer_12": part_data.get("Manufacturer", ""),
        "_snipeit_url_13": part_data.get("ProductDetailUrl", "")
    }

    try:
        url = f"{cfg.snipe_url}/hardware"
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get("status") == "success":
            print(f"Successfully created Asset! Tag: {response_data['payload']['asset_tag']}")
            return True
        else:
            print(f"Snipe-IT API Validation Error: {response_data.get('messages')}")
            return False
            
    except Exception as e:
        print(f"Snipe-IT Request Error: {e}")
        return False