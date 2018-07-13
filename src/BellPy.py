'''
Created on Jan 11, 2018

@author: CPANICI
'''
import paho.mqtt.client as mqtt
import json
from pygame import mixer
import pprint
import datetime
from bellButton import BellButton

class BellPy:
    
    global client
    
    def __init__(self, config):
        
        pprint.pprint(config)
        self.mqtt_ip = config['mqtt_server']
        self.topic = config['device_name'] + "_IN"
        self.publish_topic = config['device_name'] + "_OUT"
        self.error_topic = config['device_name'] + "_ERR"
        self.default_ding = config['default_ding']
        self.default_dong = config['default_dong']
	self.default_error = config['default_error']
	self.defailt_error = config['default_error']
        self.doorbell_pin = config['doorbell_pin']
        
        # {'PAID': {'file':'/home/pi/chaching.wav', 'sound':sound_obj}}
        self.loaded_sounds = {}
        self.mqtt_connected = False
        self.mute_dong = False
        self.silenced = False
        
        mixer.pre_init(44100, -16, 1, 2048)
        mixer.init()
        
        # pre-init the default sounds
        self.load_sound("ding", self.default_ding)
        self.load_sound("dong", self.default_dong)
	self.load_sound("error", self.default_error)        
        # sets the default sounds initially
        # this should get replaced by the updated
        # files from the mqtt server
        self.ding = self.default_ding
        self.dong = self.default_dong
	self.error = self.default_error
        
    # end __init__()
    
    def on_connect(self, client, userdata, flags, rc):
        
        # print out that we connected to the server
        print("connected to server %s with result code: %s" % (self.mqtt_ip, str(rc)))
        
        # once it is connected we will subscribe to the device topic
        client.subscribe(self.topic)
        
        self.mqtt_connected = True
    # end of on_connect
    
    def on_message(self, client, userdata, msg):
        
        print(msg.topic+" "+str(msg.payload))
        
        # convert the message over to an object
        message_obj = json.loads(msg.payload.lower())
        pprint.pprint(message_obj)
        self.process_message(message_obj)
    # end of on_message()
    
    def process_message(self, msg_payload):
        
        # command, paramater
        command = msg_payload['command']
        parameter = msg_payload['parameter']
        
        if(command == 'sound_file'):
            # parameter should be a dictionary of sound files with
            # {'<EVENT>':'<SOUND_FILE_PATH'}
            
            # loop through thse events in the parameter
            for event in parameter.keys():
                sound_file_path = parameter[event]
                if(sound_file_path.__contains__(".wav")):
                    print("EVENT = %s" % event)
                    print("Registering event %s with sound %s" % (event, parameter[event]))
                    self.load_sound(event, parameter[event])
                elif(sound_file_path == 'false'):
                    if self.loaded_sounds.keys().__contains__(event):
                        print("removing event from loaded sounds <%s>" % event)
                        self.loaded_sounds.pop(event)
                    else:
                        # ignor it
                        pass
                    # end if
                # end if
            # end for
            print("--------active sounds loaded -------")
            print(self.loaded_sounds)
        elif(command == 'play'):            
            # the parameter will have to be the
            # event
            event = parameter
            self.play_sound(event)
        elif(command == 'test_press'):
            self.doorbell_pressed(True, command)
        elif(command == 'test_release'):
            self.doorbell_released(True, command)
        else:
            pass
        # end if
    # end of process_message
    
    def play_sound(self, event_string):
        print("loaded sounds")
        print(self.loaded_sounds)
        if self.loaded_sounds.keys().__contains__(event_string):
            # get the sound object
            sound_file = self.loaded_sounds[event_string]['file_path']
            print("PLAYING SOUND <%s> @ <%s>" % (event_string, sound_file))
            sound = self.loaded_sounds[event_string]['sound']
            sound.play()
        else:
            print("ERROR: event not registered <%s>" % event_string)
    # end play_sound
    
    def publish_message(self, message):
        if self.mqtt_connected == True:
            message_str = json.dumps(message)
            self.client.publish(self.publish_topic, message_str, 0, False)
        # end if
    # end of publish_message

    def publish_error(self, err_message):
	if self.mqtt_connected == True:
	    message_str = json.dumps(message)
	    self.client.publish(self.error_topic, message_str, 0, False)
	# end if
    # end of publish_error

    def get_time(self):
	time = datetime.datetime.now()
	return time.strftime("%Y-%m-%d %H:%M:%S")
    # end of get_time()
    
    def doorbell_pressed(self, test=False, test_string=''):
        print("Doorbell pressed.")
        if self.silenced == False:
            # play the ding sound file
	    if mixer.get_busy() == True:
		mixer.stop()
	    # end if
            self.play_sound("ding")
        # end if
        
	    # time format = string
	    # format = 2018-01-13 08:48:00
        if(test==False):
            message = {"timestamp":self.get_time(), "status":"HIGH"}
        else:
            message = {"timestamp":self.get_time(), "status":test_string}
        # end if
        
        self.publish_message(message)
    # end of doorbell_pressed
    
    def doorbell_released(self, test=False, test_string=''):
        print("Doorbell released.")  
        if (self.mute_dong == False) and (self.silenced == False):
            # play the dong sound file
            self.play_sound("dong")
        # end if
        if(test == False):
            message = {"timestamp":self.get_time(), "status":"LOW"}
        else:
            message = {"timestamp":self.get_time(), "status":test_string}
        # end if
        
        self.publish_message(message)
    # end of doorbell_released
    
    # future silence button
    def silence_pressed(self):
        print("Doorbell silence button pressed.")
        self.silenced = True
        message = {"timestamp":self.get_time(), "status":"SILENCED"}
        self.publish_message(message)
    # end of silence_pressed()
    
    def silence_released(self):
        print("Doorbell silence button released")
        message = {"timestamp":self.get_time(), "status":"ENABLED"}
        self.silenced = False
        self.publish_message(message)
    # end of silence_released
        
    def load_sound(self, event_string, sound_file_path):
        if self.loaded_sounds.keys().__contains__(event_string) == False:
            # adds a new event type to 
            try:
                sound = mixer.Sound(sound_file_path)
                self.loaded_sounds[event_string] = {'file_path':sound_file_path, 'sound':sound}
            except Exception as ex:
		err_msg = "ERROR: could not load sound <%s>: %s" % (sound_file_path, ex)
                print(err_msg)
		self.publish_error(err_msg)
            # end try
        elif self.loaded_sounds.keys().__contains__(event_string) and self.loaded_sounds[event_string]['file_path'] != sound_file_path:
            # update the file path and reload
            # the sounds object
            try:
                sound = mixer.Sound(sound_file_path) 
                self.loaded_sounds[event_string]['file_path'] = sound_file_path
                self.loaded_sounds[event_string]['sound'] = sound
            except Exception as ex:
		err_msg = "ERROR: could not load sound <%s>: %s" % (sound_file_path, ex)
                print(err_msg)
		self.publish_error(err_msg)
            # end try
        else:
	    # this should mean that it found the event registered and the 
	    # same filename is in the registration.
            pass
        # end if
    # end of pre_init_sound

    def start(self):
                
        # set up the mqtt client object
        self.client = mqtt.Client()
        
        # set up the button object
	print("instantiating button...")
        db_button = BellButton(self.doorbell_pin)
        
        # set up the event handlers for the button
	print("setting up button events...")
        db_button.when_pressed = self.doorbell_pressed
        db_button.when_released = self.doorbell_released
        
        # set up the event handlers for the mqtt client
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        # connect the mqtt client
        self.client.connect(self.mqtt_ip, 1883, 60)
        
        # loop forever - I hope this handles both mqtt and
        # button event(s)
	try:
            self.client.loop_forever()
	except Exception as ex:
	    # play the error file if it gets out of the loop
	    # most likely - an error happened
	    print("playing error at the end of the main loop (BellPy.py)")
	    self.play_sound("error")
	    raise
	# end try
    # end of start
# end of BellPy
