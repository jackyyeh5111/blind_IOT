from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient, AWSIoTMQTTShadowClient
import time
import json

# Custom Shadow callback
def customShadowCallback_Update(payload, responseStatus, token):
	# payload is a JSON string ready to be parsed using json.loads(...)
	# in both Py2.x and Py3.x
	if responseStatus == "timeout":
		print("Update request " + token + " time out!")
	if responseStatus == "accepted":
		payloadDict = json.loads(payload)
		print("----------------------")
		print("Update request with token: " + token + " accepted!")
		print("light: " + str(payloadDict["state"]["desired"]["light"]))
		print("----------------------\n\n")
	if responseStatus == "rejected":
		print("Update request " + token + " rejected!")

def customShadowCallback_Delete(payload, responseStatus, token):
	if responseStatus == "timeout":
		print("Delete request " + token + " time out!")
	if responseStatus == "accepted":
		print("~~~~~~~~~~~~~~~~~~~~~~~")
		print("Delete request with token: " + token + " accepted!")
		print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")
	if responseStatus == "rejected":
		print("Delete request " + token + " rejected!")



# Custom MQTT message callback
def customCallback(client, userdata, message):
	print("Received a new message: ")
	print("from topic: " + message.topic)
	print("message: " + message.payload)

	if message.payload.startswith("cancel register"):
		lastRegisterBusNumber = message.payload.split(",")[1].strip(" ")
		print("lastRegisterBusNumber: " + lastRegisterBusNumber)

		JSONPayload = '{"state":{"desired":{"light":' + '"off"' + '}}}'
		if lastRegisterBusNumber == "256":
			PI_AWS_256.shadowUpdate(JSONPayload, customShadowCallback_Update, 5)
		elif lastRegisterBusNumber == "512":
			PI_AWS_512.shadowUpdate(JSONPayload, customShadowCallback_Update, 5)

	else:
		# transfer message based on its busNumber
		busNumber = str(json.loads(message.payload)['busNumber'])
		JSONPayload = '{"state":{"desired":{"light":' + '"on"' + '}}}'
		
		if busNumber == "256":
			PI_AWS_256.shadowUpdate(JSONPayload, customShadowCallback_Update, 5)
		elif busNumber == "512":
			PI_AWS_512.shadowUpdate(JSONPayload, customShadowCallback_Update, 5)
		
	print("--------------\n\n")

# authentication for aws iot
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

# Init AWSIoTMQTTShadowClient
myAWSIoTMQTTShadowClient = None
if useWebsocket:
	myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient("shadowUpdater", useWebsocket=True)
	myAWSIoTMQTTShadowClient.configureEndpoint(host, 443)
	myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath)
else:
	myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient("shadowUpdater")
	myAWSIoTMQTTShadowClient.configureEndpoint(host, 8883)
	myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# AWSIoTMQTTShadowClient configuration
myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5)  # 5 sec


print ("------ Connect to PI_AWS_IOT ------")

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
myAWSIoTMQTTClient.subscribe("register", 1, customCallback)
time.sleep(1)


# Connect shadow client to AWS IoT
myAWSIoTMQTTShadowClient.connect()

# Create a deviceShadow with persistent subscription
global PI_AWS_256
global PI_AWS_512
PI_AWS_256 = myAWSIoTMQTTShadowClient.createShadowHandlerWithName("PI_AWS_256", True)
PI_AWS_512 = myAWSIoTMQTTShadowClient.createShadowHandlerWithName("PI_AWS_512", True)

# Delete shadow JSON doc
PI_AWS_256.shadowDelete(customShadowCallback_Delete, 5)
PI_AWS_512.shadowDelete(customShadowCallback_Delete, 5)

print ("------ Ready to recieve message from users------")

while True:
	pass
