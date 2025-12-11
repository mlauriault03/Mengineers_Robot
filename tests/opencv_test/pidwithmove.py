#!/usr/bin/env python3
from codrone_edu.drone import Drone
from picamera2 import Picamera2
import cv2
import numpy as np
import time
import math

# PID Controller
class PID:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0
    
    def update(self, error, dt):
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt if dt > 0 else 0
        self.prev_error = error
        return self.kp * error + self.ki * self.integral + self.kd * derivative

# Initialize drone
drone = Drone()
drone.pair()

# Initialize camera
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format":"XRGB8888", "size":(IMAGE_WIDTH, IMAGE_HEIGHT)})
picam2.configure(config)
picam2.start()

cv2.namedWindow('LED Tracker')

# Color ranges
lower_green = np.array([77, 24, 200])  # Lower saturation, higher value
upper_green = np.array([98, 255, 255])  # Extended hue range into cyan
lower_red1 = np.array([0, 10, 200])    # Lower saturation, higher value
upper_red1 = np.array([33, 255, 255])  # Extended into orange range
lower_red2 = np.array([170, 21, 160])  # Covers pure red end
upper_red2 = np.array([180, 255, 255])

# PID controllers for pitch and roll
pid_x = PID(kp=0.3, ki=0.01, kd=0.15)
pid_y = PID(kp=0.3, ki=0.01, kd=0.15)

# Control parameters
DESCENT_THROTTLE = -15
MAX_CONTROL = 80
CENTERING_THRESHOLD = 50

# State variables
landing_mode = False
prev_time = time.time()

print("Camera ready. Press 'l' to start landing, 'q' to quit, 'e' for emergency stop")

drone.takeoff()
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
        
        # Find two strongest green LEDs
        green_candidates = []
        for c in green_contours:
            area = cv2.contourArea(c)
            if area > 50:
                M = cv2.moments(c)
                if M["m00"] > 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    green_candidates.append((cx, cy, area))
        
        green_candidates.sort(key=lambda x: x[2], reverse=True)
        green_centers = [(x, y) for x, y, _ in green_candidates[:2]]
        for cx, cy in green_centers:
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
        
        # Find two strongest red LEDs
        red_candidates = []
        for c in red_contours:
            area = cv2.contourArea(c)
            if area > 50:
                M = cv2.moments(c)
                if M["m00"] > 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    red_candidates.append((cx, cy, area))
        
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
        
        if len(green_centers) >= 2 and len(red_centers) >= 2:
            target_detected = True
            all_points = green_centers + red_centers
            
            # Draw lines between all points
            for i, pt in enumerate(all_points):
                for j in range(i + 1, len(all_points)):
                    cv2.line(frame, pt, all_points[j], (255, 255, 0), 1)
            
            # Calculate centroid
            avg_x = sum(p[0] for p in all_points) / 4
            avg_y = sum(p[1] for p in all_points) / 4
            offset_x = avg_x - IMAGE_WIDTH / 2
            offset_y = IMAGE_HEIGHT / 2 - avg_y
            
            # Draw target center
            cv2.circle(frame, (int(avg_x), int(avg_y)), 10, (0, 255, 255), 2)
            
            # Apply PID control if in landing mode
            if landing_mode:
                current_time = time.time()
                dt = current_time - prev_time
                prev_time = current_time
                
                # Calculate control outputs
                roll = np.clip(pid_x.update(offset_x, dt), -MAX_CONTROL, MAX_CONTROL)
                pitch = np.clip(pid_y.update(offset_y, dt), -MAX_CONTROL, MAX_CONTROL)
                
                # Apply control
                drone.set_roll(int(-roll))
                drone.set_pitch(int(pitch))
                drone.set_throttle(DESCENT_THROTTLE)
                drone.move()
                
                status = "CENTERED" if abs(offset_x) < CENTERING_THRESHOLD and abs(offset_y) < CENTERING_THRESHOLD else "CORRECTING"
                print(f"X: {offset_x:.1f}px | Y: {offset_y:.1f}px | Roll: {roll:.1f} | Pitch: {pitch:.1f} | {status}")
                drone.go("down",100,0.2)  if abs(offset_x) < CENTERING_THRESHOLD and abs(offset_y) < CENTERING_THRESHOLD else "CORRECTING"

        
        # Display mode
        if landing_mode:
            mode_text = "LANDING MODE"
            cv2.putText(frame, mode_text, (10, IMAGE_HEIGHT - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            if not target_detected:
                cv2.putText(frame, "TARGET LOST!", (10, IMAGE_HEIGHT - 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                # Stop movement if target lost
                drone.set_roll(0)
                drone.set_pitch(0)
                drone.set_throttle(0)
                drone.move()
        
        cv2.imshow('LED Tracker', frame)
        
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
            prev_time = time.time()

except KeyboardInterrupt:
    print("Interrupted - Emergency stop!")
    drone.emergency_stop()
finally:
    print("Cleaning up...")
    drone.land()
    drone.close()
    cv2.destroyAllWindows()
    picam2.stop()
