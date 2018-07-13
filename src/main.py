'''
Created on Jan 11, 2018

@author: CPANICI
'''
from BellPy import BellPy

if __name__ == '__main__':

    # physical pin for doorbell is 16 (I think) - mapps to pin 23 in gpiozero
    # physical pin for silence is 18 (future)
    
    config = {        
            'mqtt_server':'10.0.1.14',
            'device_name':'DB01',
            'default_ding':'/home/pi/sounds/ding.wav',
            'default_dong':'/home/pi/sounds/dong.wav',
	    'default_error':'/home/pi/sounds/spark.wav',
            'doorbell_pin':24,
            'silence_pin':18
        }
    # instantiate the class
    bell = BellPy(config)

    # start the service
    bell.start()
# end main
