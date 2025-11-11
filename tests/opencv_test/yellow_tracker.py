
import cv2
import numpy as np

# Initialize camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Define yellow color range in HSV
# You may need to adjust these values based on your lighting
lower_yellow = np.array([20, 100, 100])
upper_yellow = np.array([30, 255, 255])

print("Yellow object tracker started. Press 'q' to quit.")

while True:
    # Capture frame
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
    
    # Convert BGR to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Create mask for yellow color
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    # Apply morphological operations to reduce noise
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Track the largest yellow object
    if contours:
        # Find the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        
        # Only track if area is significant (filter out noise)
        if area > 500:
            # Get bounding box
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Calculate center point
            cx = x + w // 2
            cy = y + h // 2
            
            # Draw center point
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            
            # Display coordinates and area
            cv2.putText(frame, f"Center: ({cx}, {cy})", (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(frame, f"Area: {int(area)}", (x, y + h + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Display frames
    cv2.imshow('Yellow Object Tracking', frame)
    cv2.imshow('Mask', mask)
    
    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
