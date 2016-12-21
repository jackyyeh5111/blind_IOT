from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import RPi.GPIO as GPIO
import sys
import logging
import time
import getopt

#tracer = logging.getLogger('elasticsearch.trace')
#tracer.setLevel(logging.INFO)
#tracer.addHandler(logging.FileHandler('/tmp/es_trace.log'))

"""
# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.INFO)
#logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)
"""

GPIO.setmode(GPIO.BCM)
# setuo GPIO
GPIO.setup(15, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)

GPIO.output(15, False)
GPIO.output(18, False)


# Custom MQTT message callback
def customCallback(client, userdata, message):
	print("Received a new message: ")
	print("from topic: " + message.topic)
	print("message: " + message.payload)

	command = message.payload

	if message.topic == "256":
		if command == "on":
			GPIO.output(15, True)
		elif command == "off":
			GPIO.output(15, False)

	elif message.topic == "512":
		if command == "on":
			GPIO.output(18, True)
		elif command == "off":
			GPIO.output(18, False)

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
	myAWSIoTMQTTClient = AWSIoTMQTTClient("busLight")
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
#myAWSIoTMQTTClient.subscribe("register", 1, customCallback)
myAWSIoTMQTTClient.subscribe("256", 1, customCallback)
myAWSIoTMQTTClient.subscribe("512", 1, customCallback)
time.sleep(2)

# Publish to the same topic in a loop forever
loopCount = 0
while True:
	pass


"""
while True:
	myAWSIoTMQTTClient.publish("test", "New Message " + str(loopCount), 1)
	loopCount += 1
	time.sleep(1)
"""