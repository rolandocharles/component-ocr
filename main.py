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
            if result and result[0]:
                extracted_text = [line[1][0] for line in result[0]]
                part_number = extracted_text[0]
                print(f"Searching Mouser for: {part_number}")
                
                request = MouserPartSearchRequest('partnumber')
                
                success = request.part_search(part_number)
                
                if success:
                    cleaned_data = request.get_clean_response()
                    
                    if cleaned_data and len(cleaned_data) > 0:
                        best_match = cleaned_data[0]
                        print(f"Found: {best_match.get('Description')}")
                        
                        # Sync with Snipe-IT
                        status = utils.update_snipeit(cfg, best_match)
                        print(f"Snipe-IT Sync Status: {status}")
                    else:
                        print("Mouser returned a success code, but no matching part data was found.")
                else:
                    print("Mouser API request failed. Check API key, connection, or part number validity.")

        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()