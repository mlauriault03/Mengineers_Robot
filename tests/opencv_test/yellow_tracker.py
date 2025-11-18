import cv2
from picamera2 import Picamera2

picam2 = Picamera2()
picam2.start()

lower_yellow = (20, 100, 100)
upper_yellow = (30, 255, 255)

print("Tracking yellow objects. Press Ctrl+C to quit.")

try:
    while True:
        frame = picam2.capture_array()
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)
            if area > 500:
                x, y, w, h = cv2.boundingRect(c)
                cx, cy = x + w // 2, y + h // 2
                print(f"Center: ({cx}, {cy}), Area: {int(area)}")
except KeyboardInterrupt:
    picam2.stop()
