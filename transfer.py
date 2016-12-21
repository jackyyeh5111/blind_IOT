from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
#import RPi.GPIO as GPIO
import sys
import logging
import time
import getopt
import json

# Custom MQTT message callback
def customCallback(client, userdata, message):
	print("Received a new message: ")
	print("from topic: " + message.topic)
	print("message: " + message.payload)

	if message.payload.startswith("cancel register"):
		lastRegisterBusNumber = message.payload.split(",")[1].strip(" ")
		print lastRegisterBusNumber 
		myAWSIoTMQTTClient.publish(lastRegisterBusNumber, "off" , 1)

	else:
		busNumber = str(json.loads(message.payload)['busNumber'])
		myAWSIoTMQTTClient.publish(busNumber, "on" , 1)
		

	print("--------------\n\n")

useWebsocket = False
host = "ah146hwtrvzu8.iot.us-east-1.amazonaws.com"
rootCAPath = "certificate/root-certificate.txt"
certificatePath = "certificate/1cbb574dec-certificate.pem.crt"
privateKeyPath = "certificate/1cbb574dec-private.pem.key"

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
if useWebsocket:
	myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub", useWebsocket=True)
	myAWSIoTMQTTClient.configureEndpoint(host, 443)
	myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
	myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub")
	myAWSIoTMQTTClient.configureEndpoint(host, 8883)
	myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec


print ("------ Connect to PI_AWS_IOT ------")

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
myAWSIoTMQTTClient.subscribe("register", 1, customCallback)
time.sleep(2)

# Publish to the same topic in a loop forever
loopCount = 0
while True:
	pass
"""
while True:
	myAWSIoTMQTTClient.publish("256", "New Message " + str(loopCount), 1)
	loopCount += 1
	time.sleep(1)
"""