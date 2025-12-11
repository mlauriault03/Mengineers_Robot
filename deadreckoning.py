from codrone_edu.drone import *
import time


def start():
        POWER = 50
        FORWARD = 0.6
        BACKWARD = 0.3
        JUMP = 0.2
        print("Connecting to CoDrone...")
        drone = Drone()
        drone.pair()
        print("Connected!")
        drone.reset_trim()
        drone.takeoff()
        print("hovering")
        drone.hover(1)
        drone.turn_degree(0)
        drone.set_pitch(POWER)

        drone.move(FORWARD)
        drone.hover(1)
        print("returning")
        drone.go("up",100,JUMP)
        # d.turn_degree(180)
        drone.turn_degree(0)
        drone.set_pitch(-POWER)
        drone.move(BACKWARD)
        drone.hover(1)
        print("landing")
        drone.land()
        drone.close()

        print("Done.")