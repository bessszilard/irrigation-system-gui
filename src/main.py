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


class MQTTApp(App):
    connection_status = StringProperty("Not connected")
    local_time = StringProperty("Waiting for time...")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mqtt_client = MQTTClient(self.on_connect)

    def build(self):
        layout = GridLayout(cols=2, padding=10, spacing=10)

        layout.add_widget(Label(text="MQTT Server:"))
        self.broker_input = TextInput(text="broker.emqx.io")
        layout.add_widget(self.broker_input)

        layout.add_widget(Label(text="Port:"))
        self.port_input = TextInput(text="1883")
        layout.add_widget(self.port_input)

        self.status_label = Label(text=self.connection_status)
        layout.add_widget(self.status_label)

        self.connect_button = Button(text="Connect")
        self.connect_button.bind(on_press=self.connect_to_broker)
        layout.add_widget(self.connect_button)

        self.local_time_label = Label(text=self.local_time, font_size=20)
        layout.add_widget(self.local_time_label)

        layout.add_widget(Label())  # Empty label to move to next row

        self.commandWidget = CommandWidget(self.mqtt_client.addCommand)
        layout.add_widget(self.commandWidget)

        self.connect_to_broker("")

        return layout
    
    def update_local_time_hd(self, new_time):
        self.local_time_label.text = f"{new_time}"

    def cmd_option_hd(self, payload):
        # self.commandWidget.rebuild(payload)
        Clock.schedule_once(lambda dt: self.commandWidget.rebuild(payload))
        print(payload)

    def cmd_option_sensors(self, payload):
        print(payload)

    def sensors_hd(self, payload):
        print(payload)

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
