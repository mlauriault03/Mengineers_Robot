#!/usr/bin/env python3
import cv2
import numpy as np
import sys

# Load image
if len(sys.argv) < 2:
    print("Usage: python hsv_tuner.py <image_path>")
    sys.exit(1)

image_path = sys.argv[1]
frame = cv2.imread(image_path)

if frame is None:
    print(f"Error: Could not load image '{image_path}'")
    sys.exit(1)

hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

# Create windows
cv2.namedWindow('Original')
cv2.namedWindow('Mask')
cv2.namedWindow('HSV Tuner')

# Default values (pale green/cyan)
def nothing(x):
    pass

cv2.createTrackbar('H Min', 'HSV Tuner', 40, 180, nothing)
cv2.createTrackbar('H Max', 'HSV Tuner', 90, 180, nothing)
cv2.createTrackbar('S Min', 'HSV Tuner', 30, 255, nothing)
cv2.createTrackbar('S Max', 'HSV Tuner', 150, 255, nothing)
cv2.createTrackbar('V Min', 'HSV Tuner', 100, 255, nothing)
cv2.createTrackbar('V Max', 'HSV Tuner', 255, 255, nothing)

print("HSV Color Tuner")
print(f"Loaded: {image_path}")
print("Adjust trackbars to isolate your LED color")
print("Press 'p' to print current values")
print("Press 'q' to quit")

try:
    while True:
        # Get trackbar values
        h_min = cv2.getTrackbarPos('H Min', 'HSV Tuner')
        h_max = cv2.getTrackbarPos('H Max', 'HSV Tuner')
        s_min = cv2.getTrackbarPos('S Min', 'HSV Tuner')
        s_max = cv2.getTrackbarPos('S Max', 'HSV Tuner')
        v_min = cv2.getTrackbarPos('V Min', 'HSV Tuner')
        v_max = cv2.getTrackbarPos('V Max', 'HSV Tuner')
        
        # Create mask
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])
        mask = cv2.inRange(hsv, lower, upper)
        
        # Apply mask to original
        result = cv2.bitwise_and(frame, frame, mask=mask)
        
        # Display
        cv2.imshow('Original', frame)
        cv2.imshow('Mask', mask)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('p'):
            print(f"\nlower = np.array([{h_min}, {s_min}, {v_min}])")
            print(f"upper = np.array([{h_max}, {s_max}, {v_max}])")

except KeyboardInterrupt:
    print("\nInterrupted!")
finally:
    print("Cleaning up...")
    cv2.destroyAllWindows()
