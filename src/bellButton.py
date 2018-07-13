# this will be a custom button that
# will trigger events when it is pressed
# and released
import RPi.GPIO as GPIO
import time
import threading
class BellButton(threading.Thread):

    global when_pressed
    global when_released

    pressed = False
    released = True

    def get_pressed(self):
	return self.pressed
    # end of get_pressed
    def set_pressed(self, value):
	if self.pressed != value:
	    self.pressed = value
	    if self.pressed == True:
	    	self.when_pressed()
	    # end if
	# end if
    # end of set_pressed

    def get_released(self):
	return self.released
    # end of get_realeased
    def set_released(self, value):
	if self.released != value:
	    self.released = value
	    if self.released == True:
	    	self.when_released()
	    # end if
	# end if
    # end of set_released

    def __init__(self, BCM_PIN_NUMBER):

	# call the super
	super(BellButton, self).__init__()

	# now daemonize this thing! (devil horns!)
	self.daemon = True

	# initiate the IO with the pin number
	self.pin = BCM_PIN_NUMBER

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	self.killed = False
	self.start()
    # end of __init__

    def kill(self):
	self.killed = True
    # end of kill()

    def run(self):
	while not self.killed:
	    # check and see if the button
	    input_state = GPIO.input(self.pin)
	    #print("input_state= " + str(input_state))
	    if input_state == True:
		self.set_pressed(True)
		self.set_released(False)
	    else:
		self.set_pressed(False)
		self.set_released(True)
	    # end if

	    time.sleep(0.25)

	    # end while
    # end run
# end button
