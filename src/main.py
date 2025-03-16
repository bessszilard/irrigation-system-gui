from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.properties import StringProperty
from kivy.clock import mainthread
from kivy.clock import Clock
from MQTTClient import MQTTClient

from CommandsWdiget import CommandWidget
from RelayStatesWidget import RelayStatesWidget
from kivy.uix.boxlayout import BoxLayout

class MQTTApp(App):
    connection_status = StringProperty("Not connected")
    local_time = StringProperty("Waiting for time...")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mqtt_client = MQTTClient(self.on_connect)

    def build(self):
        main_layout = BoxLayout(orientation="vertical", padding=5, spacing=5)

        # Grid layout for MQTT settings (2 columns, 3 rows)
        mqtt_layout = GridLayout(cols=2, spacing=5, size_hint_x=0.5)

        mqtt_layout.add_widget(Label(text="MQTT Server:", size_hint_y=None, height=30))
        self.broker_input = TextInput(text="broker.emqx.io")
        mqtt_layout.add_widget(self.broker_input)

        mqtt_layout.add_widget(Label(text="Port:", size_hint_y=None, height=30))
        self.port_input = TextInput(text="1883")
        mqtt_layout.add_widget(self.port_input)

        mqtt_layout.add_widget(Label(text="Status:", size_hint_y=None, height=30))
        self.status_label = Label(text=self.connection_status, size_hint_y=None, height=30)
        mqtt_layout.add_widget(self.status_label)

        # Connect button
        self.connect_button = Button(text="Connect")
        self.connect_button.bind(on_press=self.connect_to_broker)
        mqtt_layout.add_widget(self.connect_button)

        # Local time label
        self.local_time_label = Label(text=self.local_time, font_size=20, size_hint_y=None, height=30)
        mqtt_layout.add_widget(self.local_time_label)

        main_layout.add_widget(mqtt_layout)

        # Command Widget (spans full width)
        self.commandWidget = CommandWidget(self.mqtt_client.addCommand)
        main_layout.add_widget(self.commandWidget)

        # Relay States Widget (spans full width)
        self.relayStateWidget = RelayStatesWidget(self.toggle_hd)
        main_layout.add_widget(self.relayStateWidget)

        self.connect_to_broker("")
        return main_layout
    
    def update_local_time_hd(self, new_time):
        self.local_time_label.text = f"{new_time}"

    def cmd_option_hd(self, payload):
        # self.commandWidget.rebuild(payload)
        Clock.schedule_once(lambda dt: self.commandWidget.rebuild(payload))
        print("cmd_option_hd")

    def cmd_option_sensors(self, payload):
        print("cmd_option_sensors")

    def cmd_list_hd(self, payload):
        self.commandWidget.add_command_list(payload["cmdList"])
        print(f"Command list {self.commandWidget.command_list}")

    def sensors_hd(self, payload):
        print("sensors_hd")
        
    def relay_state_hd(self, payload):
        print("relay_state_hd")
        Clock.schedule_once(lambda dt: self.relayStateWidget.build_or_update(payload))

    def toggle_hd(self, relay, state):
        # remove old command if exists
        priority = "PTX" if relay == "RXX" else "PTO"

        current_command = f"Manua;{relay};{state};{priority};"
        self.mqtt_client.overrideCommand(current_command)
        print(f"Toggle {relay} {state}")

    def connect_to_broker(self, instance):
        broker = self.broker_input.text
        try:
            port = int(self.port_input.text)
        except ValueError:
            self.update_status("Invalid port number", "red")
            return
        
        if not self.mqtt_client.connect(broker, port):
            self.update_status("Connection failed", "red")
            return

        self.mqttTopicCallbacks = {}
        self.mqttTopicCallbacks[self.mqtt_client.SUB_TOPICS["LOCAL_TIME"]] = self.update_local_time_hd
        self.mqttTopicCallbacks[self.mqtt_client.SUB_TOPICS["CMD_OPTIONS"]] = self.cmd_option_hd
        self.mqttTopicCallbacks[self.mqtt_client.SUB_TOPICS["SENSORS"]] = self.sensors_hd
        self.mqttTopicCallbacks[self.mqtt_client.SUB_TOPICS["RELAYS"]] = self.relay_state_hd
        self.mqttTopicCallbacks[self.mqtt_client.SUB_TOPICS["CMD_LIST"]] = self.cmd_list_hd

        self.mqtt_client.setTopicsCallback(self.mqttTopicCallbacks)

    @mainthread
    def update_status(self, status, color):
        self.connection_status = status
        self.status_label.text = status
        self.status_label.color = (0, 1, 0, 1) if color == "green" else (1, 0, 0, 1)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.update_status("Connected", "green")
        else:
            self.update_status("Connection failed", "red")

if __name__ == "__main__":
    MQTTApp().run()
