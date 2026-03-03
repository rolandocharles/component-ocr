import requests
import re

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