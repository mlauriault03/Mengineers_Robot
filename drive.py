# Drive Controller 2.0
# 12/10/25


# PUBLIC LIBRARIES
import time
import math


# PRIVATE LIBRARIES
from pid import PID
from encoder import Encoder
from servo import Servo


class Drive:
    """
    Robot Drive Controller.
    Parameters:
    ----------
    pin_servo_left : int
        Left Servo GPIO pin number on the Raspberry PI
    pin_servo_right : int
        Right Servo GPIO pin number on the Raspberry PI
    addr_encoder_left : int
        Left Encoder I2C address
    addr_encoder_right : int
        Right Encoder I2C address
    """

    # GENERAL PARAMETERS

    WHEEL_DIAMETER_IN = 2.64      # Wheel diameter in inches
    WHEEL_BASE_IN = 8.5           # Space between wheel centers in inches

    # SERVO PARAMETERS
    LEFT_PULSE_REVERSE  = 1000    # 1000 [ms] full speed reverses
    LEFT_PULSE_NEUTRAL  = 1500    # 1500 [ms] stop (1491.5)
    LEFT_PULSE_FORWARD  = 2000    # 2000 [ms] full speed forward
    RIGHT_PULSE_REVERSE = 1000    # 1000 [ms] full speed reverse
    RIGHT_PULSE_NEUTRAL = 1500    # 1500 [ms] stop
    RIGHT_PULSE_FORWARD = 2000    # 2000 [ms] full speed forward

    # PID PARAMETERS
    DIR_KP = 0.07
    DIR_KI = 0.00
    DIR_KD = 0.00
    DIR_MAX_COMP = 0.3


    # CONSTRUCTOR

    def __init__(self, pin_servo_left: int, pin_servo_right: int, addr_encoder_left: int, addr_encoder_right: int):
        # Hardware control objects
        self.servo_left  = Servo(pin_servo_left, 1)
        #     pulse_reverse = self.LEFT_PULSE_REVERSE,
        #     pulse_neutral = self.LEFT_PULSE_NEUTRAL,
        #     pulse_forward = self.LEFT_PULSE_FORWARD
        # )
        self.servo_right = Servo(pin_servo_right, -1)
        #     pulse_reverse = self.RIGHT_PULSE_REVERSE,
        #     pulse_neutral = self.RIGHT_PULSE_NEUTRAL,
        #     pulse_forward = self.RIGHT_PULSE_FORWARD
        # )
        self.encoder_left = Encoder(addr_encoder_left, 1)
        self.encoder_right = Encoder(addr_encoder_right, -1)
        # Direction PID controller
        self.dir_pid = PID(self.DIR_KP, self.DIR_KI, self.DIR_KD, -self.DIR_MAX_COMP, self.DIR_MAX_COMP)


    # UTILITY METHODS

    def _distance_to_ticks(self, distance_in: float) -> int:
        """Calculate encoder ticks needed to travel specified distance"""
        circumference = math.pi * self.WHEEL_DIAMETER_IN    # circumference = pi * diameter
        rotations = distance_in / circumference             # rotations = distance / circumference
        encoder_ticks = rotations * Encoder.TICKS_PER_REV   # ticks = rotations * (ticks/rotations)
        return int(encoder_ticks) + 1                       # round to an integer (+1 because move_forward stops early by 1)
    
    def _angle_to_ticks(self, angle_deg: float) -> int:
        """Convert in-place rotation angle to encoder ticks."""
        # Convert angle to absolute magnitude
        angle = abs(angle_deg)
        # Arc length each wheel must travel for the robot to rotate by angle_deg
        arc_length = (math.pi * self.WHEEL_BASE_IN * angle) / 360.0
        # Convert arc length to ticks (reuse same formula as linear motion)
        return self._distance_to_ticks(arc_length)
    

    # MOVEMENT METHODS

    def _set_speed(self, left: float, right: float):
        """Set left and right servo speeds. Auto compensate for slight motor differences."""
        # TODO add left/right difference compensation
        self.servo_right.set_speed(right)
        self.servo_left.set_speed(left)

    def _stop(self):
        """Set both servo's speed to zero and then wait 0.5 seconds for it to take effect"""
        self.servo_right.stop()
        self.servo_left.stop()
        time.sleep(1)

    def _ramp_up(self, end_speed: int, steps: int = 20):
        for i in range(0, steps + 1):
            speed = (i/steps) * end_speed
            self._set_speed(speed, speed)
            time.sleep(0.05)


    # PUBLIC METHODS

    def startup(self):
        """Start servo and encoder control threads"""
        self.servo_left.startup()
        self.servo_right.startup()
        self.encoder_left.start()
        self.encoder_right.start()
        time.sleep(1) # wait for threads to start
    
    def shutdown(self):
        """Stop servo and encoder control threads (join them to the main thread)"""
        self.servo_left.shutdown()
        self.servo_right.shutdown()
        self.encoder_left.stop()
        self.encoder_right.stop()
        time.sleep(1) # wait for threads to join

    def move_forward(self, distance_in: float):
        """Move forward specified distance in inches"""
        # Reset encoders
        self.encoder_left.reset()
        self.encoder_right.reset()
        # Reset direction PID controller
        self.dir_pid.reset()
        # Calculate ticks to reach distance
        target_ticks = self._distance_to_ticks(distance_in)
        # Determine direction
        direction = 1 if distance_in > 0 else -1
        print(f"Target ticks: {target_ticks}")
        # servo speed variables
        base_speed = 1 - self.DIR_MAX_COMP
        left_speed = base_speed
        right_speed = base_speed
        # control loop
        while True:
            # determine left and right wheel position difference
            left_ticks = self.encoder_left.get_position()
            right_ticks = self.encoder_right.get_position()
            tick_diff = left_ticks - right_ticks
            # compute left servo speed compensation
            left_comp = self.dir_pid.update(target=0, current=tick_diff)
            # stop either servo if they have reached the target position
            if (abs(left_ticks - target_ticks) <= 1) and (left_speed is not None):
                print("Stopping LEFT servo...")
                self.servo_left.stop() # left servo reached target
                left_speed = None
            if (abs(right_ticks - target_ticks) <= 1 and (right_speed is not None)):
                print("Stopping RIGHT servo...")
                self.servo_right.stop() # right servo reached target
                right_speed = None
            # Debug
            print(f"Comp: {left_comp}\tLt: {left_ticks}\tRt: {right_ticks}\tDt: {tick_diff}\tLs: {left_speed}\tRs: {right_speed}\tDir: {direction}")
            # break condition
            if (left_speed is None) and (right_speed is None): 
                break
            # compensate left and right speeds if both servos are still running
            if (left_speed is not None) and (right_speed is not None):
                if direction == 1:        
                    left_speed  = base_speed + left_comp
                    right_speed = base_speed - left_comp
                else:
                    left_speed  = -base_speed + left_comp
                    right_speed = -base_speed - left_comp
            # update left servo speed (if still running)
            if left_speed is not None:
                self.servo_left.set_speed(left_speed)
            # update right servo speed (if still running)
            if right_speed is not None:
                self.servo_right.set_speed(right_speed)
            time.sleep(0.02) # 50 Hz control loop
        print("TARGET REACHED")

    def turn(self, angle_deg: float):
        """Turn robot by specified angle in degrees."""
        # Reset encoders
        self.encoder_left.reset()
        self.encoder_right.reset()
        # Reset direction PID controller
        self.dir_pid.reset()
        # Calculate ticks to reach distance
        target_ticks = self._angle_to_ticks(angle_deg)
        # Determine direction
        direction = 1 if angle_deg > 0 else -1
        print(f"Target ticks: {target_ticks}")
        # servo speed variables (based on direction)
        base_speed = 1 - self.DIR_MAX_COMP
        left_speed  =  base_speed * direction
        right_speed = -base_speed * direction
        # control loop
        while True:
            # determine left and right wheel position difference
            left_ticks = abs(self.encoder_left.get_position())
            right_ticks = abs(self.encoder_right.get_position())
            tick_diff = left_ticks - right_ticks
            # compute left servo speed compensation
            left_comp = self.dir_pid.update(target=0, current=tick_diff)
            # stop either servo if they have reached the target position
            if (abs(left_ticks - target_ticks) <= 1) and (left_speed is not None):
                print("Stopping LEFT servo...")
                self.servo_left.stop() # left servo reached target
                left_speed = None
            if (abs(right_ticks - target_ticks) <= 1 and (right_speed is not None)):
                print("Stopping RIGHT servo...")
                self.servo_right.stop() # right servo reached target
                right_speed = None
            # Debug
            print(f"Comp: {left_comp}\tLt: {left_ticks}\tRt: {right_ticks}\tDt: {tick_diff}\tLs: {left_speed}\tRs: {right_speed}\tDir: {direction}")
            # break condition
            if (left_speed is None) and (right_speed is None): 
                break
            # compensate left and right speeds if both servos are still running
            if (left_speed is not None) and (right_speed is not None):
                if direction == 1:
                    left_speed  = base_speed + left_comp
                    right_speed = (base_speed - left_comp) * -1
                else:
                    left_speed  = (base_speed + left_comp) * -1
                    right_speed = base_speed - left_comp
            # update left servo speed (if still running)
            if left_speed is not None:
                self.servo_left.set_speed(left_speed)
            # update right servo speed (if still running)
            if right_speed is not None:
                self.servo_right.set_speed(right_speed)
            time.sleep(0.02) # 50 Hz control loop
        print("TURN COMPLETED")
