from codrone_edu.drone import *
import time

print("Connecting to CoDrone...")
d = Drone()
d.pair()
print("Connected!")
d.reset_trim()
d.takeoff()
print("hovering")
d.hover(1)
d.go("forward", 20, 1)
d.hover(1)
print("returning")
d.go("up",20,0.6)
# d.turn_degree(180)
d.go("backward", 20, 1)
d.hover(1)
print("landing")
d.land()
d.close()

print("Done.")
