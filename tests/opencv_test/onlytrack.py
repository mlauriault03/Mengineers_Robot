import cv2
import math
from itertools import combinations
from picamera2 import Picamera2


picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "XRGB8888", "size": (640, 480)}))
picam2.start()

FRONT_WIDTH = 24
FOCAL_LENGTH = 3.04
SENSOR_WIDTH = 3.68
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480

lower_green = (80, 45, 135)
upper_green = (100, 255, 255)
lower_red1 = (0, 60, 70)
upper_red1 = (20, 255, 255)
lower_red2 = (160, 60, 70)
upper_red2 = (180, 255, 255)

cv2.namedWindow('LED Tracker')
landing_mode = False
should_exit = False

try:
    while True:
        frame = picam2.capture_array()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        
        green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find all green LEDs with area (brightness proxy)
        green_candidates = []
        for c in green_contours:
            area = cv2.contourArea(c)
            if area > 50:
                M = cv2.moments(c)
                if M["m00"] > 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    green_candidates.append((cx, cy, area))
        
        # Keep only the two strongest (largest area) green LEDs
        green_candidates.sort(key=lambda x: x[2], reverse=True)
        green_centers = [(x, y) for x, y, _ in green_candidates[:2]]
        for cx, cy in green_centers:
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
        
        # Find all red LEDs with area (brightness proxy)
        red_candidates = []
        for c in red_contours:
            area = cv2.contourArea(c)
            if area > 50:
                M = cv2.moments(c)
                if M["m00"] > 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    red_candidates.append((cx, cy, area))
        
        # Keep only the two strongest (largest area) red LEDs
        red_candidates.sort(key=lambda x: x[2], reverse=True)
        red_centers = [(x, y) for x, y, _ in red_candidates[:2]]
        for cx, cy in red_centers:
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
        
        # Draw center crosshairs
        cv2.line(frame, (IMAGE_WIDTH // 2 - 20, IMAGE_HEIGHT // 2), 
                (IMAGE_WIDTH // 2 + 20, IMAGE_HEIGHT // 2), (255, 0, 255), 2)
        cv2.line(frame, (IMAGE_WIDTH // 2, IMAGE_HEIGHT // 2 - 20), 
                (IMAGE_WIDTH // 2, IMAGE_HEIGHT // 2 + 20), (255, 0, 255), 2)
        cv2.circle(frame, (IMAGE_WIDTH // 2, IMAGE_HEIGHT // 2), 
                  50, (255, 0, 255), 2)
        
        target_detected = False
        offset_x = 0
        offset_y = 0
        yaw = 0
        
        if len(green_centers) >= 2 and len(red_centers) >= 2:
            target_detected = True
            all_points = green_centers + red_centers
            
            for i, pt in enumerate(all_points):
                for j in range(i + 1, len(all_points)):
                    cv2.line(frame, pt, all_points[j], (255, 255, 0), 1)
            
                pixel_width = math.sqrt((green_centers[0][0] - green_centers[1][0])**2 + 
                                       (green_centers[0][1] - green_centers[1][1])**2)
            
                if pixel_width > 0:
                    distance = (FRONT_WIDTH * FOCAL_LENGTH * IMAGE_WIDTH) / (pixel_width * SENSOR_WIDTH)
                    avg_x = sum(p[0] for p in all_points) / 4
                    avg_y = sum(p[1] for p in all_points) / 4
                    offset_x = avg_x - IMAGE_WIDTH / 2
                    offset_y = 240 - avg_y
                    
                    front_center_x = (green_centers[0][0] + green_centers[1][0]) / 2
                    rear_center_x = (red_centers[0][0] + red_centers[1][0]) / 2
                    front_center_y = (green_centers[0][1] + green_centers[1][1]) / 2
                    rear_center_y = (red_centers[0][1] + red_centers[1][1]) / 2
                    yaw = math.degrees(math.atan2(rear_center_x - front_center_x, 
                                                 front_center_y - rear_center_y))
                    
                    # Draw target center
                    cv2.circle(frame, (int(avg_x), int(avg_y)), 10, (0, 255, 255), 2)
                    
                    print(f"Distance: {distance:.1f}mm | X: {offset_x:.1f}px | Y: {offset_y:.1f}px | Yaw: {yaw:.1f}° | Height: {current_height}cm | {status}")
                        
        
        if landing_mode:
            mode_text = "LANDING MODE"
            cv2.putText(frame, mode_text, (10, IMAGE_HEIGHT - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            if not target_detected:
                cv2.putText(frame, "TARGET LOST!", (10, IMAGE_HEIGHT - 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        cv2.imshow('LED Tracker', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('e'):
            print("EMERGENCY STOP!")
            break
        elif key == ord('l') and not landing_mode:
            print("Starting landing sequence - centering over target...")
            landing_mode = True

except KeyboardInterrupt:
    print("Interrupted - Emergency stop!")
finally:
    print("Cleaning up...")
    cv2.destroyAllWindows()
    picam2.stop()
