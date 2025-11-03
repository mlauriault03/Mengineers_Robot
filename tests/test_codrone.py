from codrone_edu.drone import Drone
import time

print("Connecting to CoDrone...")
d = Drone()
d.pair()
print("Connected!")

d.takeoff()
d.hover(1)
d.land()
d.close()

print("Done.")