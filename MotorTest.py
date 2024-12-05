import RPi.GPIO as GPIO
import time

pump1 = 26
pump2 = 16
pump3 = 20
pump4 = 21

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pump1, GPIO.OUT)
GPIO.setup(pump2, GPIO.OUT)
GPIO.setup(pump3, GPIO.OUT)
GPIO.setup(pump4, GPIO.OUT)

GPIO.output(pump1, False)
GPIO.output(pump2, False)
GPIO.output(pump3, False)
GPIO.output(pump4, False)

try:
    while True:
      for x in range(5):
            GPIO.output(pump1, True)
            time.sleep(0.1)
            GPIO.output(pump1, False)
            GPIO.output(pump2, True)
            time.sleep(0.1)
            GPIO.output(pump2, False)
	    GPIO.output(pump3, True)
	    time.sleep(0.1)
	    GPIO.output(pump3, False)
	    GPIO.output(pump4, True)
	    time.sleep(0.1)
	    GPIO.output(pump4, False)
			
      for x in range(4):
            GPIO.output(pump1, True)
            time.sleep(0.05)
            GPIO.output(pump1, False)
	    GPIO.output(pump2, True)
            time.sleep(0.05)
            GPIO.output(pump2, False)
            GPIO.output(pump3, True)
            time.sleep(0.05)
            GPIO.output(pump3, False)
            GPIO.output(pump4, True)
            time.sleep(0.05)
            GPIO.output(pump4, False)



except KeyboardInterrupt:
    GPIO.cleanup()
