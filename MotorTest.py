import RPi.GPIO as GPIO
import time

pump1 = 16
pump2 = 18
pump3 = 
pump4 = 

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
			
      
      GPIO.output(pump1,False)
      GPIO.output(pump2,False)
	  GPIO.output(pump3,False)
	  GPIO.output(pump4,False)

      for x in range(4):
            GPIO.output(pump1, True)
            time.sleep(0.05)
            GPIO.output(pump1, False)
            time.sleep(0.05)
      GPIO.output(pump1,True)

      for x in range(4):
            GPIO.output(pump2, True)
            time.sleep(0.05)
            GPIO.output(pump2, False)
            time.sleep(0.05)
      GPIO.output(pump2,True)
	  
	  for x in range(4):
            GPIO.output(pump3, True)
            time.sleep(0.05)
            GPIO.output(pump3, False)
            time.sleep(0.05)
      GPIO.output(pump3,True)
	  
	  for x in range(4):
            GPIO.output(pump4, True)
            time.sleep(0.05)
            GPIO.output(pump4, False)
            time.sleep(0.05)
      GPIO.output(pump4,True)


	  GPIO.output(pump1,False)
      GPIO.output(pump2,False)
	  GPIO.output(pump3,False)
	  GPIO.output(pump4,False)


except KeyboardInterrupt:
    GPIO.cleanup()