from codrone_edu.drone import *
import time

# Create drone object
drone = Drone()

# Pair with drone
drone.pair()

# Takeoff
print("Taking off...")
drone.takeoff()
drone.hover(3)  # Hover for 3 seconds to stabilize

# Land
print("\nLanding...")
drone.land()

# Disconnect
drone.close()
print("Flight complete!")
