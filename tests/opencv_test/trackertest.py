import cv2
import math
from picamera2 import Picamera2

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "XRGB8888", "size": (640, 480)}))
picam2.start()

FRONT_WIDTH = 24
FOCAL_LENGTH = 3.04
SENSOR_WIDTH = 3.68
IMAGE_WIDTH = 640

lower_green = (80, 90, 135)
upper_green = (100, 255, 255)
lower_red1 = (0, 70, 70)
upper_red1 = (10, 255, 255)
lower_red2 = (170, 70, 70)
upper_red2 = (180, 255, 255)

print("Press 'q' to quit")

while True:
    frame = picam2.capture_array()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    green_mask = cv2.inRange(hsv, lower_green, upper_green)
    red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)
    
    green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    green_centers = []
    for c in green_contours:
        if cv2.contourArea(c) > 50:
            M = cv2.moments(c)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                green_centers.append((cx, cy))
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
    
    red_centers = []
    for c in red_contours:
        if cv2.contourArea(c) > 50:
            M = cv2.moments(c)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                red_centers.append((cx, cy))
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
    
    if len(green_centers) >= 2 and len(red_centers) >= 2:
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
            
            print(f"Distance: {distance:.1f}mm | X: {offset_x:.1f}px | Y: {offset_y:.1f}px | Yaw: {yaw:.1f}°")
    
    cv2.imshow('LED Tracker', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()
