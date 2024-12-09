import RPi.GPIO as GPIO
import time

pump1 = 26
pump2 = 16
pump3 = 19
pump4 = 21

ON = False
OFF = True

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(pump1, GPIO.OUT)
GPIO.setup(pump2, GPIO.OUT)
GPIO.setup(pump3, GPIO.OUT)
GPIO.setup(pump4, GPIO.OUT)

GPIO.output(pump1, OFF)
GPIO.output(pump2, OFF)
GPIO.output(pump3, OFF)
GPIO.output(pump4, OFF)

try:
    while True:
            GPIO.output(pump1, ON)
            time.sleep(1)
            GPIO.output(pump1, OFF)
            GPIO.output(pump2, ON)
            time.sleep(1)
            GPIO.output(pump2, OFF)
            GPIO.output(pump3, ON)
            time.sleep(1)
            GPIO.output(pump3, OFF)
            GPIO.output(pump4, ON)
            time.sleep(1)
            GPIO.output(pump4, OFF)
			



except KeyboardInterrupt:
    GPIO.cleanup()
