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
    servo_pin : int
        Servo GPIO pin number on the Raspberry PI
    encoder_addr : int
        Encoder I2C address
    direction : int
        Forward spin direction of wheel (1 = left wheel, -1 = right wheel)
    kp : float
        Proportional (P) gain coefficient
    ki : float
        Integral (I) gain coefficient
    kd : float
        Derivative (D) gain coefficient
    rate_hz : int
        Update rate in Hz
    """

    # GENERAL PARAMETERS

    WHEEL_DIAMETER_IN = 2.64    # Wheel diameter in inches
    LEFT_SLOW_FACTOR = 0.9      # Factor to match max left speed to max right speed
    # FW_SLOW_FACTOR = 0.9        # Factor to match max forward speed to max reverse speed
    # NOTE: Servos move different speeds when turning forward vs turning backward

    # SERVO PARAMETERS
    LEFT_PULSE_REVERSE  = 1000    # 1000 [ms] full speed reverses
    LEFT_PULSE_NEUTRAL  = 1500    # 1500 [ms] stop (1491.5)
    LEFT_PULSE_FORWARD  = 2000    # 2000 [ms] full speed forward
    RIGHT_PULSE_REVERSE = 1000    # 1000 [ms] full speed reverse
    RIGHT_PULSE_NEUTRAL = 1500    # 1500 [ms] stop
    RIGHT_PULSE_FORWARD = 2000    # 2000 [ms] full speed forward

    # PID PARAMETERS
    DIR_KP = 0.05
    DIR_KI = 0.00
    DIR_KD = 0.00


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
        self.dir_pid = PID(self.DIR_KP, self.DIR_KI, self.DIR_KD, -0.2, 0.2)


    # UTILITY METHODS

    def _distance_to_ticks(self, distance_in: int):
        """Calculate encoder ticks needed to travel specified distance"""
        circumference = math.pi * self.WHEEL_DIAMETER_IN    # circumference = pi * diameter
        rotations = distance_in / circumference             # rotations = distance / circumference
        encoder_ticks = rotations * Encoder.TICKS_PER_REV   # ticks = rotations * (ticks/rotations)
        return encoder_ticks
    

    # MOVEMENT METHODS

    def _set_speed(self, left: float, right: float):
        """Set left and right servo speeds. Auto compensate for slight motor differences."""
        # TODO add left/right difference compensation
        self.servo_right.set_speed(right)
        self.servo_left.set_speed(left)

    def _startup_servos(self):
        self.servo_right.startup()
        self.servo_left.startup()

    def _stop(self):
        """Set both servo's speed to zero and then wait 0.5 seconds for it to take effect"""
        self.servo_right.stop()
        self.servo_left.stop()
        time.sleep(1)

    def _shutdown_servos(self):
        self.servo_right.shutdown()
        self.servo_left.shutdown()
        time.sleep(1)

    def _ramp_up(self, end_speed: int, steps: int = 20):
        for i in range(0, steps + 1):
            speed = (i/steps) * end_speed
            self._set_speed(speed, speed)
            time.sleep(0.05)

    def _get_position(self) -> tuple[int, int]:
        return (self.encoder_left.get_position(), self.encoder_right.get_position())


    # PUBLIC METHODS

    def move_forward(self, distance_in: int):
        """Move forward specified distance in inches"""
        self._startup_servos()
<<<<<<< Updated upstream
        self.dir_pid.reset()
        target_ticks = self._distance_to_ticks(distance_in)
        # servo speed variables
        left_speed = 1
        right_speed = 1
        # control loop
        while True:
            # determine left and right wheel position difference
            left_ticks, right_ticks = self._get_position()
            tick_diff = left_ticks - right_ticks
            # compute left servo speed compensation
            left_comp = self.dir_pid.update(target=0, current=tick_diff)
            # stop either servo if they have reached the target position
            if abs(left_ticks - target_ticks) <= 1:
                self.servo_left.shutdown() # left servo reached target
                left_speed = None
            if abs(right_ticks - target_ticks) <= 1:
                self.servo_right.shutdown() # right servo reached target
                right_speed = None
            # break condition
            if (left_speed is None) and (right_speed is None): 
                break
            # compensate left and right speeds if both servos are still running
            if (left_speed is not None) and (right_speed is not None):
                left_speed = left_speed + left_comp
                right_speed = right_speed - left_comp
            # update left servo speed (if still running)
            if left_speed is not None:
                self.servo_left.set_speed(left_speed)
            # update right servo speed (if still running)
            if right_speed is not None:
                self.servo_left.set_speed(right_speed)
            time.sleep(0.05) # 20 Hz control loop
        time.sleep(1) # allow time for servo threads to join main thread

        # ---------------------------- TEST CODE ----------------------------
        # self._start_servos()
        # ticks = distance_in # TESTING ONLY
        # # self._ramp_up(1)
        # self._set_speed(0.5, 0.5)
        # time.sleep(5)
        # self._shutdown()
        # -------------------------------------------------------------------

    def turn(self, angle_deg: float):
        """Turn robot by specified angle in degrees."""
        # TODO: implement turning logic
        pass
=======
        ticks = distance_in # TESTING ONLY
        self._ramp_up(1)
        # self._set_speed(0.5, 0.5)
        time.sleep(5)
        self._shutdown_servos()
        time.sleep(1)
        # Set target position for both wheels (same absolute value)
>>>>>>> Stashed changes
