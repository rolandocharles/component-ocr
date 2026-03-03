import cv2
from paddleocr import PaddleOCR
import utils
from config import AppConfig
from mouser import MouserAPI

def main():
    # iconfig instance
    cfg = AppConfig()
    
    # PaddleOCR init
    ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
    
    # camera init
    cap = cv2.VideoCapture(0) 
    print("System Ready. [SPACE] to Capture, [Q] to Quit.")

    while True:
        ret, frame = cap.read()
        if not ret: break
            
        cv2.imshow("Scanner - Press SPACE to Identify", frame)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):
            print("Processing...")
            result = ocr.ocr(frame, cls=True)
            
            if result and result[0]:
                extracted_text = [line[1][0] for line in result[0]]
                
                mouser_data = utils.query_mouser(cfg, extracted_text[0])
                
                if mouser_data:
                    status = utils.update_snipeit(cfg, mouser_data)
                    print(f"Snipe-IT Sync Status: {status}")
                else:
                    print("Part not found.")

        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()