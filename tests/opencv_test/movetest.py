from codrone_edu.drone import *

drone = Drone()
drone.pair()

# Take off
drone.takeoff()

drone.hover(2)
# Move forward with pitch
drone.set_pitch(50)  # Set positive pitch to move forward
print("pitching")
drone.move(1)  # Execute movement for 1 second

# Reset pitch to stop forward motion
print("stop")

drone.hover(2)
drone.set_pitch(0)
drone.move(0.5)  # Brief hover to stabilize

drone.set_yaw(0)
# Move backward with negative pitch to return
drone.set_pitch(-50)  # Set negative pitch to move backward
print("returning")
drone.move(1)  # Execute movement for 1 second

# Reset to hover before landing
drone.reset_move_values()
drone.hover(1)

# Land
drone.land()

drone.close()
