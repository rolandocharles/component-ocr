import cv2
from paddleocr import PaddleOCR
import utils
from config import AppConfig
from mouser.api import MouserPartSearchRequest 

def main():
    cfg = AppConfig()
    
    ocr = PaddleOCR(use_textline_orientation=True, lang='en')

    cap = cv2.VideoCapture(cfg.camera_index) 

    if not cap.isOpened():
        print(f"Error: Could not open camera {cfg.camera_index}. Check your .env file or USB connection.")
        return
    
    print("System Ready. [SPACE] to Capture, [Q] to Quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break
            
        cv2.imshow("Scanner - Press SPACE to Identify", frame)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):
            print("Processing OCR...")
            result = list(ocr.predict(frame))
            print(f"OCR Result: {result}")

            if result and len(result) > 0:
                page_data = result[0]
                extracted_text = page_data['rec_texts']
                print(f"Raw OCR Text: {extracted_text}")
                
                possible_parts = utils.filter_ocr(extracted_text)
                print(f"Filtered Candidates: {possible_parts}")
                
                valid_matches = []
                seen_mouser_numbers = set()

                if possible_parts:
                    for part_number in possible_parts:                    
                        print(f"Searching Mouser for: {part_number}")
                        
                        request = MouserPartSearchRequest('partnumber')
                        success = request.part_search(part_number)
                        
                        if success:
                            cleaned_data = request.get_clean_response()
                            
                            if cleaned_data and len(cleaned_data) > 0:
                                best_match = cleaned_data[0]
                                mouser_pn = best_match.get('MouserPartNumber')
                                
                                if mouser_pn and mouser_pn not in seen_mouser_numbers:
                                    seen_mouser_numbers.add(mouser_pn)
                                    valid_matches.append((part_number, best_match))

                    if not valid_matches:
                        print("No matching part data found on Mouser for any candidates.")
                    
                    elif len(valid_matches) == 1:
                        selected_match = valid_matches[0][1]
                        print(f"\nExact Match Found: {selected_match.get('Description')}")
                        
                        utils.print_full_search_output(selected_match)
                        status = utils.update_snipeit(cfg, selected_match)
                        print(f"Snipe-IT Sync Status: {status}")
                    
                    else:
                        print("\nMultiple parts found. Please select the correct one:")
                        for idx, (scanned_code, match) in enumerate(valid_matches):
                            desc = match.get('Description', 'No Description')
                            m_pn = match.get('MouserPartNumber', 'Unknown PN')
                            print(f"  [{idx + 1}] {m_pn} (from '{scanned_code}') - {desc}")
                        
                        while True:
                            try:
                                choice = input(f"Enter choice (1-{len(valid_matches)}) or 'c' to cancel: ")
                                if choice.lower() == 'c':
                                    print("Selection cancelled.")
                                    break
                                
                                choice_idx = int(choice) - 1
                                if 0 <= choice_idx < len(valid_matches):
                                    selected_match = valid_matches[choice_idx][1]
                                    print(f"Selected: {selected_match.get('MouserPartNumber')}")
                                    
                                    utils.print_full_search_output(selected_match)
                                    status = utils.update_snipeit(cfg, selected_match)
                                    print(f"Snipe-IT Sync Status: {status}")
                                    break
                                else:
                                    print("Invalid selection. Out of range.")
                            except ValueError:
                                print("Invalid input. Please enter a number.")
                else:
                    print("OCR found text, but no valid part numbers passed the filter.")
            else:
                print("No text detected. Adjust focus or lighting.")

        elif key == ord('q'):
            break
        
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()