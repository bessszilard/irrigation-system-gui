import paho.mqtt.client as mqtt
import json

# Define MQTT topics
MQTT_SENSORS = "sjirs/sensors"
MQTT_RELAYS = "sjirs/relays"
MQTT_LOCAL_TIME = "sjirs/localTime"
MQTT_CMD_LIST = "sjirs/cmd/list"
MQTT_CMD_RESPONSE = "sjirs/cmd/response"

class MQTTClient:
    def __init__(self, on_connect_callback, on_update_local_time):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.on_connect_callback = on_connect_callback
        self.on_update_local_time = on_update_local_time

    def connect(self, broker, port):
        try:
            self.client.connect(broker, port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected successfully to MQTT broker")
            self.on_connect_callback(client, userdata, flags, rc)
            
            # Subscribe to topics
            self.client.subscribe(MQTT_SENSORS)
            self.client.subscribe(MQTT_RELAYS)
            self.client.subscribe(MQTT_LOCAL_TIME)
            self.client.subscribe(MQTT_CMD_LIST)
            self.client.subscribe(MQTT_CMD_RESPONSE)
        else:
            print(f"Connection failed with code {rc}")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        
        if topic == MQTT_SENSORS:
            self.handle_sensors(payload)
        elif topic == MQTT_RELAYS:
            self.handle_relays(payload)
        elif topic == MQTT_LOCAL_TIME:
            self.handle_local_time(payload)
        elif topic == MQTT_CMD_LIST:
            self.handle_cmd_list(payload)
        elif topic == MQTT_CMD_RESPONSE:
            self.handle_cmd_response(payload)
        else:
            print(f"Received message on unknown topic {topic}: {payload}")

    def handle_sensors(self, payload):
        print(f"Sensor Data Received: {payload}")
        # Process sensor data here
    
    def handle_relays(self, payload):
        print(f"Relay Status Received: {payload}")
        # Process relay status here
    
    def handle_local_time(self, payload):
        print(f"Local Time Received: {payload}")
        data = json.loads(payload)
        self.on_update_local_time(data["LocalTime"])
    
    def handle_cmd_list(self, payload):
        print(f"Command List Received: {payload}")
        # Process command list here
    
    def handle_cmd_response(self, payload):
        print(f"Command Response Received: {payload}")

        # Process command response here