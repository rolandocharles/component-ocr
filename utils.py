import requests
import re
import json
import random

def print_full_search_output(part_data):
    """
    Prints the full JSON dictionary for the selected Mouser part.
    """
    print("\n" + "="*55)
    print(f" DEBUG: FULL DATA FOR {part_data.get('MouserPartNumber', 'SELECTED PART')}")
    print("="*55)
    
    try:
        # Pretty-print the dictionary
        print(json.dumps(part_data, indent=4))
    except Exception as e:
        print(f"Could not format part data: {e}")
        print(part_data)
        
    print("="*55 + "\n")

def filter_ocr(ocr_texts: list) -> list:
    """
    Filters raw OCR text to find likely electronic component part numbers.
    Strips common labels (P/N, QTY) and evaluates both spaced and space-removed strings.
    """
    candidates = []
    
    # Matches electrical values (e.g., 5V, 10uF, 100mA)
    units_pattern = re.compile(
        r'^\d+(?:\.\d+)?\s*(?:uF|pF|nF|mF|V|mV|A|mA|Ohm|kOhm|MHz|Hz|W|mW|C|%)\b', 
        re.IGNORECASE
    )
    
    # Common prefixes on component bags that we want to delete from the start of lines
    prefix_pattern = re.compile(
        r'^(?:MFG P/N|MOUSER P/N|P/N|QTY|DESC|COO|LINE ITEM|LOT)\s*[:\-]?\s*', 
        re.IGNORECASE
    )
    
    # Exact words we want to completely ignore
    ignore_words = {
        'MADE', 'IN', 'CHINA', 'TAIWAN', 'MALAYSIA', 'PHILIPPINES', 
        'MEXICO', 'LOT', 'REV', 'VER', 'DATE', 'MOUSER', 'WWW', 'COM',
        'ELECTRONICS', 'CUST', 'DESC', 'ROHS', 'COMPLIANT', 'QTY', 'COO',
        'MFG', 'PN', 'LINE', 'ITEM', 'BARCODE'
    }

    for text in ocr_texts:
        text_upper = text.strip().upper()
        if not text_upper:
            continue

        # 1. Strip off known prefixes (e.g., "MFG P/N: nRF54L15-DK" becomes "nRF54L15-DK")
        text_upper = prefix_pattern.sub('', text_upper)
        
        # 2. Convert colons to spaces, then split into tokens
        tokens = text_upper.replace(':', ' ').split()
        
        # 3. Also add the space-removed version to handle OCR accidentally adding spaces 
        # to a single part number (e.g., "LM 358" -> "LM358")
        if len(tokens) > 1:
            tokens.append("".join(tokens))

        for token in tokens:
            if not token:
                continue
                
            # Rule A: Skip exact ignore words
            if token in ignore_words:
                continue
                
            # Rule B: Skip electrical units
            if units_pattern.search(token):
                continue
                
            # Rule C: Length check (skip tiny garbage and massively long strings)
            if len(token) < 4 or len(token) > 25:
                continue
                
            # Rule D: Must be a mix of letters and numbers, OR a pure number >= 5 digits
            has_letter = any(c.isalpha() for c in token)
            has_number = any(c.isdigit() for c in token)
            
            if (has_letter and has_number) or (not has_letter and has_number and len(token) >= 5):
                
                # Rule E: Final sanitization 
                clean_part = re.sub(r'[^A-Z0-9\-+]', '', token)
                
                # Prevent duplicates while keeping order
                if len(clean_part) >= 4 and clean_part not in candidates:
                    candidates.append(clean_part)
                    
    return candidates

def generate_random_asset_tag():
    """
    Placeholder function to generate a random asset tag.
    Replace with your actual logic if needed.
    """
    asset_tag = random.randint(10000, 99999)
    print(f"Generated Asset Tag: {asset_tag}")
    return asset_tag

def update_snipeit(cfg, part_data):
    """
    Creates a new hardware Asset in Snipe-IT using the Mouser part data
    and maps them to the 'Electronic Components' custom fieldset.
    """
    headers = {
        "Authorization": f"Bearer {cfg.snipe_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Base payload for a Snipe-IT Asset
    payload = {
        "name": part_data.get("ManufacturerPartNumber", "Unknown Part"), 
        "model_id": 2,  # Assuming 'Electronic Components' model has ID 2
        "asset_tag": generate_random_asset_tag(),
        "status_id": 2,  # Assuming 'Ready To Deploy' status has ID 2
        
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