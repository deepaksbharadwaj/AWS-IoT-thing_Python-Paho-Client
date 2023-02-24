#!python3
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import json
import datetime
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
import paho.mqtt.client as paho
import os
import socket
import ssl
import asyncio
import _threading_local

ENDPOINT = "a1r8gg4naq8zjm-ats.iot.ap-northeast-2.amazonaws.com"  # Seoul AWS IoT Endpoint
CLIENT_ID = "ESA_SOA_TestDevice02"
PATH_TO_CERTIFICATE = "certificates/ESA_SOA_TestDevice02/ESA_SOA_TestDevice02.certificate.pem"
PATH_TO_PRIVATE_KEY = "certificates/ESA_SOA_TestDevice02/ESA_SOA_TestDevice02.privkey.pem"
PATH_TO_AMAZON_ROOT_CA_1 = "certificates/ESA_SOA_TestDevice02/AmazonRootCA1.pem"

MESSAGE = "Hello ESA Team"
TOPIC_PUB = "test/testing"

TOPIC_SUB = "driver/bodyVital/details"
RANGE = 3
SEC = 60

received_count = 0

# Spin up resources
event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=ENDPOINT,
    cert_filepath=PATH_TO_CERTIFICATE,
    pri_key_filepath=PATH_TO_PRIVATE_KEY,
    client_bootstrap=client_bootstrap,
    ca_filepath=PATH_TO_AMAZON_ROOT_CA_1,
    client_id=CLIENT_ID,
    clean_session=False,
    keep_alive_secs=60
)


def on_message_received(topic, payload, **kwargs):
    # print("Received message from topic '{}': {}".format(topic, payload))
    topic_parsed = False
    if "/" in topic:
        parsed_topic = topic.split("/")
        if len(parsed_topic) == 3:
            # this topic has the format "topic/subtopic1/subtopic2"
            if (parsed_topic[0] == 'device') and (parsed_topic[2] == 'details'):
                if parsed_topic[1] == 'temp':
                    # device/temp/details: {"desiredTemp": 20, "currentTemp": 15}
                    print("Received temperature request: {}".format(payload))
                    topic_parsed = True
                if parsed_topic[1] == 'light':
                    # device/light/details: {"desiredLight": 100, "currentLight": 50}
                    print("Received light request: {}".format(payload))
                    topic_parsed = True
                if parsed_topic[1] == 'vehicle':
                    # device/vehicle/details: {"enginespeed":"90","tirepressure":"33","FuelType":"Petrol"}
                    print("Received vehicle info: {}".format(payload))
                    topic_parsed = True
            if (parsed_topic[0] == 'driver') and (parsed_topic[2] == 'details'):
                if parsed_topic[1] == 'bodyVital':
                    # driver/bodyVital/details: {"name":"Alex","heartrate":"122","SP-O2":"98","bodytempC":"36.5"}
                    print("Received Driver Body Vital Details: {}".format(payload))
                    topic_parsed = True
        if len(parsed_topic) == 2:
            # this topic has the format "topic/subtopic"
            print("Received Subscription request: {}".format(payload))
            topic_parsed = True
    if not topic_parsed:
        print("Unrecognized message topic.")


async def mqtt_Subscribe(topic, delay):
    loop = asyncio.get_running_loop()
    end_time = loop.time() + delay
    while True:
        # print("Blocking...", datetime.datetime.now())
        await asyncio.sleep(1)
        subscribe_future, packet_id = mqtt_connection.subscribe(
            topic=TOPIC_SUB,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=on_message_received
        )
        subscribe_result = subscribe_future.result()
        # print(subscribe_result)
        if loop.time() > end_time:
            print("Done.")
            break


# Make the connect() call
print("Connecting to AWS IoT Core ENDPOINT {} with client ID '{}'...".format(ENDPOINT, CLIENT_ID))
connect_future = mqtt_connection.connect()
# Future.result() waits until a result is available
connect_future.result()
print("Connected!")

# Publish message to server desired number of times.
print('Begin Publish')
for i in range(RANGE):
    data = "{} [{}]".format(MESSAGE, i + 1)
    message = {"message": data}
    mqtt_connection.publish(topic=TOPIC_PUB, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)
    print("Published: '" + json.dumps(message) + "' to the topic: " + TOPIC_PUB)
    t.sleep(0.1)
print('Publish End')
t.sleep(2)

# # Synchronous Subscribe to the desired topic from server
# subscribe_future, packet_id = mqtt_connection.subscribe(topic=TOPIC_SUB, qos=mqtt.QoS.AT_LEAST_ONCE,
#                                                         callback=on_message_received)
# subscribe_result = subscribe_future.result()
# print("Subscribed to topic '{}'...".format(str(subscribe_result['topic'])))
# print("Subscribed with {}".format(str(subscribe_result['qos'])))


# Asynchronous Subscribe to the desired topic from server
asyncio.run(mqtt_Subscribe(TOPIC_SUB, SEC))

disconnect_future = mqtt_connection.disconnect()
disconnect_future.result()

##############################################################################################
# init parameters : using AWS IoT SDK
# myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
# myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
# myAWSIoTMQTTClient.configureCredentials(PATH_TO_AMAZON_ROOT_CA_1, PATH_TO_PRIVATE_KEY, PATH_TO_CERTIFICATE)
#
# connect
# myAWSIoTMQTTClient.connect()
#
# publish
# print('Begin Publish')
# for i in range (RANGE):
#     data = "{} [{}]".format(MESSAGE, i+1)
#     message = {"message" : data}
#     myAWSIoTMQTTClient.publish(TOPIC, json.dumps(message), 1)
#     print("Published: '" + json.dumps(message) + "' to the topic: " + "'test/testing'")
#     t.sleep(0.1)
# print('Publish End')
#
# disconnect
# myAWSIoTMQTTClient.disconnect()
##############################################################################################