import cv2
import math
import sys
import time
from picamera2 import Picamera2
from codrone_edu.drone import *

drone = Drone()
drone.pair()

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "XRGB8888", "size": (640, 480)}))
picam2.start()

# LED physical dimensions in mm
FRONT_WIDTH = 24  # Distance between green LEDs
REAR_WIDTH = 24   # Distance between red LEDs
LENGTH = 38       # Distance front to back

# Camera parameters (Pi Camera V2 typical values)
FOCAL_LENGTH = 3.04  # mm
SENSOR_WIDTH = 3.68  # mm
IMAGE_WIDTH = 640    # pixels

lower_green = (80, 90, 135)
upper_green = (100, 255, 255)
lower_red1 = (0, 70, 70)
upper_red1 = (10, 255, 255)
lower_red2 = (170, 70, 70)
upper_red2 = (180, 255, 255)

# Store last known values
last_distance = 0
last_offset_x = 0
last_offset_y = 0
last_yaw = 0
last_seen_time = time.time()

# Control parameters
CENTER_THRESHOLD = 30  # pixels - consider centered if within this
LANDING_HEIGHT = 200   # mm - land when closer than this
YAW_THRESHOLD = 10     # degrees
LOST_TIMEOUT = 5       # seconds before landing
EMERGENCY_TIMEOUT = 10 # seconds before emergency land

print("Press 'q' to quit.")
print("Taking off...")
drone.takeoff()
drone.hover(2)

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
            
            # Calculate distance using front green LEDs
            pixel_width = math.sqrt((green_centers[0][0] - green_centers[1][0])**2 + 
                                   (green_centers[0][1] - green_centers[1][1])**2)
            
            if pixel_width > 0:
                # Distance = (real_width * focal_length * image_width) / (pixel_width * sensor_width)
                distance = (FRONT_WIDTH * FOCAL_LENGTH * IMAGE_WIDTH) / (pixel_width * SENSOR_WIDTH)
                
                # Calculate center of all LEDs
                avg_x = sum(p[0] for p in all_points) / 4
                avg_y = sum(p[1] for p in all_points) / 4
                
                # Calculate offset from image center
                offset_x = avg_x - IMAGE_WIDTH / 2
                offset_y = 240 - avg_y  # Flip Y (positive = up)
                
                # Calculate orientation (yaw)
                front_center_x = (green_centers[0][0] + green_centers[1][0]) / 2
                rear_center_x = (red_centers[0][0] + red_centers[1][0]) / 2
                front_center_y = (green_centers[0][1] + green_centers[1][1]) / 2
                rear_center_y = (red_centers[0][1] + red_centers[1][1]) / 2
                
                yaw = math.degrees(math.atan2(rear_center_x - front_center_x, 
                                             front_center_y - rear_center_y))
                
                # Update last known values
                last_distance = distance
                last_offset_x = offset_x
                last_offset_y = offset_y
                last_yaw = yaw
                last_seen_time = time.time()
        
        # Always display last known values (even if tracking is lost)
        cv2.putText(frame, f"Distance: {last_distance:.1f}mm", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Offset X: {last_offset_x:.1f}px", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Offset Y: {last_offset_y:.1f}px", (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Yaw: {last_yaw:.1f}deg", (10, 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Print to CLI on same line
        time_lost = time.time() - last_seen_time
        sys.stdout.write(f"\rDist: {last_distance:.1f}mm | X: {last_offset_x:.1f}px | Y: {last_offset_y:.1f}px | Yaw: {last_yaw:.1f}° | Lost: {time_lost:.1f}s ")
        sys.stdout.flush()
        
        # Check if lost for too long
        if time_lost > EMERGENCY_TIMEOUT:
            print("\nLost target for 10s - Emergency landing!")
            drone.emergency_stop()
            break
        elif time_lost > LOST_TIMEOUT:
            print("\nLost target for 5s - Landing...")
            drone.land()
            break
        
        # Control drone to center over camera
        if last_distance > 0 and time_lost < 1:
            # Check if centered and at landing height
            centered = abs(last_offset_x) < CENTER_THRESHOLD and abs(last_offset_y) < CENTER_THRESHOLD
            aligned = abs(last_yaw) < YAW_THRESHOLD
            
            if centered and aligned and last_distance < LANDING_HEIGHT:
                print("\nCentered and low - Landing...")
                drone.land()
                break
            
            # Convert pixel offsets to movement distances (rough calibration)
            # Positive offset_x = drone is to the right, need to move left (negative)
            # Positive offset_y = drone is above center, need to move forward (positive pitch)
            move_right = int(last_offset_x * 0.1)  # pixels to cm
            move_forward = int(last_offset_y * 0.1)
            
            # Rotate to align
            if abs(last_yaw) > YAW_THRESHOLD:
                drone.turn_degree(int(-last_yaw))
            
            # Move to center
            if abs(last_offset_x) > CENTER_THRESHOLD or abs(last_offset_y) > CENTER_THRESHOLD:
                drone.move(0.5, move_right, move_forward, 0, 0)
        
        cv2.imshow('LED Tracker', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except KeyboardInterrupt:
    print("\nStopping...")
finally:
    drone.land()
    drone.close()
    cv2.destroyAllWindows()
    picam2.stop()
