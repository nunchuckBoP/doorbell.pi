import RPi.GPIO as gpio
import time

PIN_NUMBER = 24

gpio.setmode(gpio.BCM)
gpio.setup(PIN_NUMBER, gpio.IN)

while True:

	status = gpio.input(PIN_NUMBER)
	print("status=%s" % status)
	time.sleep(0.25)
# end while
