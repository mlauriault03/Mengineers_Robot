import cv2
import math
from itertools import combinations
from picamera2 import Picamera2
from codrone_edu.drone import *

drone = Drone()
drone.pair()

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

# Centering parameters
CENTERING_THRESHOLD = 50  # pixels - how close to center is "good enough" (expanded)
YAW_THRESHOLD = 15  # degrees (expanded)
DESCENT_THRESHOLD = 150  # pixels - if within this, descend while adjusting
POSITION_GAIN = 0.0005  # conversion from pixels to meters (reduced for smaller adjustments)
YAW_GAIN = 0.3  # yaw correction gain (reduced)

# Movement parameters for go() function
# Assume: 1 second at 20% power = 10cm = 0.1m
BASE_POWER = 5  # base power percentage
DESCENT_POWER = 80  # power for gradual descent
DESCENT_DURATION = 0.3  # seconds to descend each iteration
MAX_DURATION = 0.5  # maximum duration per adjustment to prevent long freezes
MIN_HEIGHT = 30  # cm - emergency stop if below this height
LOW_ALT_STRIKES = 5



print("Press 't' to takeoff, 'q' to quit, 'e' for emergency stop, 'l' to start landing sequence")

cv2.namedWindow('LED Tracker')

# Show camera feed before takeoff
print("Camera feed active. Press 't' when ready to takeoff...")
takeoff_done = False
while not takeoff_done:
    frame = picam2.capture_array()
    cv2.putText(frame, "Press 't' to TAKEOFF", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow('LED Tracker', frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('t'):
        takeoff_done = True
        break
    elif key == ord('q'):
        drone.close()
        cv2.destroyAllWindows()
        picam2.stop()
        exit()

print("Taking off...")
drone.takeoff()
drone.hover(2)
drone.send_absolute_position(0,0,1,1,0,0)
landing_mode = False
low_alt_strikes = LOW_ALT_STRIKES
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
                  CENTERING_THRESHOLD, (255, 0, 255), 2)
        
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
                    
                    # Display status
                    status = "CENTERED" if (abs(offset_x) < CENTERING_THRESHOLD and 
                                           abs(offset_y) < CENTERING_THRESHOLD and 
                                           abs(yaw) < YAW_THRESHOLD) else "ADJUSTING"
                    cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                               1, (0, 255, 0) if status == "CENTERED" else (0, 165, 255), 2)
                    
                    # Landing mode: adjust position to center
                    if landing_mode:
                        # Check height and emergency stop if too low
                        current_height = drone.get_height()
                        
                        # Display height on screen
                        cv2.putText(frame, f"Height: {current_height}cm", (10, IMAGE_HEIGHT - 100), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                        
                        # Only check height if it's a valid reading (not 0)
                        if current_height > 0 and current_height < MIN_HEIGHT:
                            low_alt_strikes -= 1
                            print(f"HEIGHT LOW ({current_height}cm) - Strikes remaining: {low_alt_strikes}")
                            if low_alt_strikes <= 0:
                                print("EMERGENCY STOP!")
                                drone.emergency_stop()
                                should_exit = True
                        else:
                            low_alt_strikes = LOW_ALT_STRIKES
                        
                        print(f"Distance: {distance:.1f}mm | X: {offset_x:.1f}px | Y: {offset_y:.1f}px | Yaw: {yaw:.1f}° | Height: {current_height}cm | {status}")
                        
                        if abs(offset_x) < CENTERING_THRESHOLD and abs(offset_y) < CENTERING_THRESHOLD and abs(yaw) < YAW_THRESHOLD:
                            print("CENTERED - Landing now!")
                            drone.land()
                            should_exit = True
                        else:
                            # Calculate position adjustments in meters
                            move_right = offset_x * POSITION_GAIN    # right/left in meters
                            move_forward = offset_y * POSITION_GAIN  # forward/back in meters
                            turn_angle = -yaw * YAW_GAIN             # yaw correction
                            
                            # Convert meters to go() duration (seconds at BASE_POWER)
                            # 1 second at 20% = 0.1m, so duration = distance / 0.1
                            duration_right = abs(move_right) / 0.1
                            duration_forward = abs(move_forward) / 0.1
                            
                            # Apply movements using go(direction, power, duration)
                            if abs(move_forward) > 0.01:  # threshold 1cm
                                direction = "forward" if move_forward < 0 else "backward"
                                drone.go(direction, BASE_POWER, duration_forward)
                            
                            if abs(move_right) > 0.01:  # threshold 1cm
                                direction = "right" if move_right < 0 else "left"
                                drone.go(direction, BASE_POWER, duration_right)
                            
                            if abs(turn_angle) > 1:  # threshold 1 degree
                                drone.turn(turn_angle)
                            
                            # Only descend if target is detected and reasonably close to center
                            total_offset = math.sqrt(offset_x**2 + offset_y**2)
                            if total_offset < DESCENT_THRESHOLD:
                                drone.go("down", DESCENT_POWER, DESCENT_DURATION)
                                print(f"descending {DESCENT_DURATION}s (offset: {total_offset:.1f}px)")
        
        if landing_mode:
            mode_text = "LANDING MODE"
            cv2.putText(frame, mode_text, (10, IMAGE_HEIGHT - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            if not target_detected:
                cv2.putText(frame, "TARGET LOST!", (10, IMAGE_HEIGHT - 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        cv2.imshow('LED Tracker', frame)
        
        if should_exit:
            break
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('e'):
            print("EMERGENCY STOP!")
            drone.emergency_stop()
            break
        elif key == ord('l') and not landing_mode:
            print("Starting landing sequence - centering over target...")
            landing_mode = True

except KeyboardInterrupt:
    print("Interrupted - Emergency stop!")
    drone.emergency_stop()
finally:
    print("Cleaning up...")
    drone.close()
    cv2.destroyAllWindows()
    picam2.stop()
