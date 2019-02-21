'''

	* Project Name: 	Smart Street Lamp 
	* Author List: 	Edwin Clement , Joshua Noronha , Ruth Peter
	* Filename: 		main.py
    * Functions: 		__init__,setup_mock,send_status,mqtt_connection,on_message
  *
'''
import time
import requests
import random 
import json
import sys
import paho.mqtt.client as paho
from contextlib import contextmanager
from threading import Timer,Thread,Event


class StreetLamp:
    FAILURE = [
        "Camera Loss",
        "Led Fail",
        "Pollution Sensor Fail",
        "Dimmer Fail",
        "Power Sensor" ,
        "Pay Gateway Fail",
        "Chassis Fail",
        "Corrosion",
        "Wrong Installation",
        "Excess Voltage",
        "Physical Damage",
        "Extreme Temp."
    ]

    def __init__(self, config={}):
        print ("Initializing Street Lamp")
        if config:
            self.location = config['location']
            self.srno = config['srno']
        else:
            # mock
            location_arr = "mumbai delhi chennai bangalore noida pune thrissur".split()
            location_dict = {
                "mumbai" : (19.0760, 72.8777) ,
                "delhi" : (28.7041, 77.1025) ,
                "chennai" : (13.0827, 80.2707) ,
                "bangalore" : (12.9716, 77.5946) ,
                "noida" : (28.5355, 77.3910) ,
                "pune" : (18.5204, 73.8567) ,
                "thrissur" : (10.5276, 76.2144) ,
            }
            self.location = random.choice(location_arr)

            self.latitude = location_dict[self.location][0] + random.random()*0.001
            self.longitude =  location_dict[self.location][1] + random.random()*0.001
            self.srno = random.randint(1, 100)

        self.name = self.location + "_" +str(self.srno)

        # TODO Give the video url
        # self.setup_mock()
        self.camera_feed_url = ""

 
    def setup_mock(self):
        self.failure = []
        if random.randint(0,100) < 80:
            self.light_status = "ACTIVE"        
            self.led_power = random.randint(1,10)*50
        else:
            self.light_status = "INACTIVE"    
            self.led_power = 0
            self.failure.append(self.FAILURE[random.randint(0,len(self.FAILURE)-1)])    
        
        self.car_charge_power = random.randint(400,630)
        self.total_power = self.led_power + self.car_charge_power
        self.pollution = random.randint(170, 340)
        self.noise_level = random.randint(0,1)
       
       

    def randomize(self):
        if self.light_status == "ACTIVE":
            if random.randint(0,10000) < 9990:
                self.light_status = "ACTIVE"        
                self.led_power = random.randint(1,10)*50
                self.failure = []
            else:
                self.light_status = "INACTIVE"    
                self.led_power = 0
                self.failure = []
                self.failure.append(self.FAILURE[random.randint(0,len(self.FAILURE)-1)])    
            
        self.car_charge_power = random.randint(400,630)
        self.total_power = self.led_power + self.car_charge_power
        self.pollution = random.randint(170, 340)
        self.noise_level = random.randint(0,1)

    
    def send_status(self):
        self.randomize()
        _json= {
            "light_status" : self.light_status,
            "led_power" : self.led_power,
            "car_charge_power" :self.car_charge_power,
            "total_power" :self.total_power,
            "srno": self.srno,
            "pollution":self.pollution, 
            "noise_level":self.noise_level,      
            "latitude":self.latitude,
            "longitude":self.longitude,     
            "camera_feed_url": self.camera_feed_url,
            "id": self.name,
            "failure": self.failure
        }

        json_message = json.dumps(_json)
        return json_message

@contextmanager
def mqtt_connection(name, server, callback):
    client= paho.Client(name) #create client object 
    client.on_message=callback
    print("LOG::INFO: Connecting to",server)
    client.connect(server)
    print("LOG::INFO: Connected to",server)
    client.loop_start() #start loop to process received messages        

    yield client

    client.disconnect() #disconnect
    client.loop_stop() #stop loop


# config = {"location" : "",
#         "srno": 0}
# if(len(sys.argv) == 3):
#     config = {
#         "location" : sys.argv[1],
#         "srno": sys.argv[2]
#     }
# else:
#     config = {
#         "location" : "mumbai",
#         "srno": 2
#     }

# client_id = config["location"] +"_" + str(config["srno"])

# def on_message(client, userdata, message):
#     print("received message =",str(message.payload.decode("utf-8")))
# broker="0.0.0.0" 
# f = StreetLamp()
# with mqtt_connection(f.name, broker, on_message) as client:
#     print("subscribing ")
#     client.subscribe("house/bulb1")#subscribe
    
#     f = StreetLamp()
#     f.setup_mock()
#     while 1:
#         time.sleep(3)
#         client.publish("streetlamps/status_update",f.send_status()) #publish

class MockThreads(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event
        self.broker="0.0.0.0" 

        self.streetlamp = StreetLamp()

    def run(self):
        def on_message(client, userdata, message):
            print("received message =",str(message.payload.decode("utf-8")))
      
        with mqtt_connection(self.streetlamp.name, self.broker, on_message) as client:
            print("subscribing ")
            client.subscribe("house/bulb1")#subscribe
            
            self.streetlamp.setup_mock()
            while not self.stopped.wait(3):
                # print("sending status message")
                client.publish("streetlamps/status_update", self.streetlamp.send_status()) #publish

stopFlag = Event()
thread = MockThreads(stopFlag)
thread.start()

for k in range(32):
    stopFlag = Event()
    thread = MockThreads(stopFlag)
    thread.start()


# this will stop the timer
# stopFlag.set()