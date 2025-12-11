#!/usr/bin/env python3
from picamera2 import Picamera2
import numpy as np
import time


def start():
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
    picam2.start()

    time.sleep(0.5)
    baseline = np.mean(picam2.capture_array())
    print("waiting for flash")
    while True:
        brightness = np.mean(picam2.capture_array())
        if brightness > baseline + 30:
            break
        time.sleep(0.05)

    print("flash detected")
    picam2.stop()
