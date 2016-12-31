from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient, AWSIoTMQTTShadowClient
import RPi.GPIO as GPIO
import json
import time

GPIO.setmode(GPIO.BCM)

gpio_256 = 15  # 256 bus light connected to gpio 15
gpio_512 = 18  # 512 bus light connected to gpio 18

# setuo GPIO
GPIO.setup(gpio_256, GPIO.OUT)
GPIO.setup(gpio_512, GPIO.OUT)

GPIO.output(gpio_256, False)
GPIO.output(gpio_512, False)

class shadowCallbackContainer:
	def __init__(self, deviceShadowInstance, gpio):
		self.deviceShadowInstance = deviceShadowInstance
		self.gpio = gpio

	# Custom Shadow callback
	def customShadowCallback_Delta(self, payload, responseStatus, token):
		# payload is a JSON string ready to be parsed using json.loads(...)
		# in both Py2.x and Py3.x
		
		print("-------------------------")
		print(responseStatus)
		payloadDict = json.loads(payload)
		deltaMessage = json.dumps(payloadDict["state"]) # json to string
		print("Received a delta message:")
		
		light_command = str(payloadDict["state"]["light"])
		print("light: " + str(payloadDict["state"]["light"]))

		if light_command == "on" : 
			GPIO.output(self.gpio, True)
		elif light_command == "off":
			GPIO.output(self.gpio, False)
		
		print("Request to update the reported state...")
		newPayload = '{"state":{"reported":' + deltaMessage + '}}'
		self.deviceShadowInstance.shadowUpdate(newPayload, None, 5)
		print("-------------------------\n\n")


# authentication for aws iot
useWebsocket = False
host = "ah146hwtrvzu8.iot.us-east-1.amazonaws.com"
rootCAPath = "certificate/root-certificate.txt"
certificatePath = "certificate/1cbb574dec-certificate.pem.crt"
privateKeyPath = "certificate/1cbb574dec-private.pem.key"

# Init AWSIoTMQTTShadowClient
myAWSIoTMQTTShadowClient = None
if useWebsocket:
	myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient("shadowDeltaListener", useWebsocket=True)
	myAWSIoTMQTTShadowClient.configureEndpoint(host, 443)
	myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath)
else:
	myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient("shadowDeltaListener")
	myAWSIoTMQTTShadowClient.configureEndpoint(host, 8883)
	myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTShadowClient configuration
myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5)  # 5 sec


print ("------ Connect to PI_AWS_IOT ------")
# Connect to AWS IoT
myAWSIoTMQTTShadowClient.connect()

# Create a deviceShadow with persistent subscription
PI_AWS_256 = myAWSIoTMQTTShadowClient.createShadowHandlerWithName("PI_AWS_256", True)
PI_AWS_512 = myAWSIoTMQTTShadowClient.createShadowHandlerWithName("PI_AWS_512", True)

# initial shadowCallbackContainer
shadowCallbackContainer_PI_AWS_256 = shadowCallbackContainer(PI_AWS_256, gpio_256)
shadowCallbackContainer_PI_AWS_512 = shadowCallbackContainer(PI_AWS_512, gpio_512)

# Listen on deltas
PI_AWS_256.shadowRegisterDeltaCallback(shadowCallbackContainer_PI_AWS_256.customShadowCallback_Delta)
PI_AWS_512.shadowRegisterDeltaCallback(shadowCallbackContainer_PI_AWS_512.customShadowCallback_Delta)


# Publish to the same topic in a loop forever
while True:
	pass
