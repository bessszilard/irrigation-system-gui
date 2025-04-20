import json

import paho.mqtt.client as mqtt

# Define MQTT topics

MQTT_TOPICS_JSON_PATH = "../config/MqttTopics.json"
class MQTTClient:
    def __init__(self, on_connect_callback):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.on_connect_callback = on_connect_callback
        self.subscribed_topics = set()
        with open(MQTT_TOPICS_JSON_PATH) as f:
            data = json.load(f)
            self.SUB_TOPICS = data["Subscribe"]
            self.PUB_TOPICS = data["Publish"]

    def setTopicsCallback(self, callback):
        self.__callbacks = callback

    def requestForAllInfo(self):
        self.client.publish(self.PUB_TOPICS["GET_ALL_INFO"], "")

    def connect_to_server(self, broker, port):
        try:
            self.client.connect(broker, port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def subscribe(self, topic):
        if topic in self.subscribed_topics:
            return
        self.subscribed_topics.add(topic)
        self.client.subscribe(topic)
        print(f"Subscribed to {topic}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected successfully to MQTT broker")
            for topic in self.SUB_TOPICS.values():
                self.subscribe(topic)

            self.on_connect_callback(client, userdata, flags, rc)

            self.requestForAllInfo()
        else:
            print(f"Connection failed with code {rc}")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode('utf-8')

        if topic not in self.__callbacks.keys():
            print(f"Topic {topic} not handled")
            return

        try:
            parsedPayload = json.loads(payload)
            if not parsedPayload:
                print(f"Pares payload is none")
            self.__callbacks[topic](parsedPayload)

        except json.JSONDecodeError as e:
            # Catch JSON decoding errors specifically
            print(f"JSONDecodeError: Failed to parse payload. Error: {e}")
            print(f"Payload: {payload}")
        except Exception as e:
            # General exception for any other errors
            print(f"Failed to parse {payload}. Error: {e}")
    # publish
    def commandManager(self, action_topic, command=""):
        if action_topic not in self.PUB_TOPICS.keys():
            print(f"Invalid command action: {self.PUB_TOPICS}")
            return
        self.client.publish(self.PUB_TOPICS[action_topic], command)
        print(f"{self.PUB_TOPICS[action_topic]} published {command}")

    def overrideCommand(self, command):
        self.client.publish(self.PUB_TOPICS["OVERRIDE_CMD"], command)
        print(f'{self.PUB_TOPICS["OVERRIDE_CMD"]} published {command}')
