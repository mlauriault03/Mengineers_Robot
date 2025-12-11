from codrone_edu.drone import *
import time
import math
import threading

drone = Drone()
drone.pair()

# Position tracking variables
pos_x = 0.0
pos_y = 0.0
pos_z = 0.0
vel_x = 0.0
vel_y = 0.0
vel_z = 0.0

# Timing
last_time = time.time()
tracking = False

def position_tracking_loop():
    global pos_x, pos_y, pos_z, vel_x, vel_y, vel_z, last_time, tracking
    
    while tracking:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        # Get accelerometer data (in m/s^2, already scaled by 10)
        accel_x = drone.get_accel_x() / 10.0
        accel_y = drone.get_accel_y() / 10.0
        accel_z = drone.get_accel_z() / 10.0
        
        # Get orientation angles to compensate for gravity
        angle_roll = math.radians(drone.get_angle_x())
        angle_pitch = math.radians(drone.get_angle_y())
        
        # Remove gravity component (9.8 m/s^2)
        # Transform accelerations to world frame
        accel_x_world = accel_x - 9.8 * math.sin(angle_pitch)
        accel_y_world = accel_y + 9.8 * math.sin(angle_roll)
        accel_z_world = accel_z - 9.8 * math.cos(angle_pitch) * math.cos(angle_roll)
        
        # Integrate acceleration to get velocity
        vel_x += accel_x_world * dt
        vel_y += accel_y_world * dt
        vel_z += accel_z_world * dt
        
        # Integrate velocity to get position
        pos_x += vel_x * dt
        pos_y += vel_y * dt
        pos_z += vel_z * dt
        
        print(f"Position: X={pos_x:.3f}m, Y={pos_y:.3f}m, Z={pos_z:.3f}m")
        
        time.sleep(0.05)  # 20Hz update rate

# Takeoff
drone.takeoff()
time.sleep(3)

# Start position tracking thread
last_time = time.time()
tracking = True
tracking_thread = threading.Thread(target=position_tracking_loop)
tracking_thread.start()

# Move 0.2m (20cm) to the right
drone.send_absolute_position(0, 0.2, 0.8, 0.5, 0, 0)
time.sleep(5)

# Return to origin
drone.send_absolute_position(0, 0, 0.8, 0.5, 0, 0)
time.sleep(5)

# Stop tracking
tracking = False
tracking_thread.join()

print(f"\nFinal tracked position: X={pos_x:.3f}m, Y={pos_y:.3f}m, Z={pos_z:.3f}m")

# Compare with optical flow
flow_x = drone.get_pos_x("m")
flow_y = drone.get_pos_y("m")
print(f"Optical flow position: X={flow_x:.3f}m, Y={flow_y:.3f}m")

# Land
drone.land()
drone.close()
