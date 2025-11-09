from kivy.clock import mainthread
from kivy.properties import StringProperty
from kivy.uix.gridlayout import GridLayout
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField

DEFAULT_SERVER = "test.mosquitto.org"
DEFAULT_PORT_STR = "1883"
DEFAULT_DEVICE_ID = "jdm7"
# DEFAULT_DEVICE_ID = "th2w"
# DEFAULT_DEVICE_ID = "10a0"


class MQTTSettingsWidget(MDCard):
    connection_status = StringProperty("Disconnected")
    local_time = StringProperty("--:--")

    def add_cb(self, connect_to_server, set_mqtt_callbacks):
        self.connect = connect_to_server
        self.set_mqtt_callbacks = set_mqtt_callbacks

    def update_local_time_hd(self, new_time):
        self.local_time_label.text = (
            f"{new_time['LocalTime']} Uptime: {new_time['UpTime']} sec"
        )

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = 10
        self.spacing = 10
        self.orientation = "vertical"

        mqtt_layout = GridLayout(cols=2, spacing=5)

        mqtt_layout.add_widget(MDLabel(text="MQTT Server:", size_hint_y=None, height=30))
        self.broker_input = MDTextField(text=DEFAULT_SERVER)
        mqtt_layout.add_widget(self.broker_input)

        mqtt_layout.add_widget(MDLabel(text="Port:", size_hint_y=None, height=30))
        self.port_input = MDTextField(text=DEFAULT_PORT_STR)
        mqtt_layout.add_widget(self.port_input)

        mqtt_layout.add_widget(MDLabel(text="Device Id:", size_hint_y=None, height=30))
        self.device_id_input = MDTextField(text=DEFAULT_DEVICE_ID)
        mqtt_layout.add_widget(self.device_id_input)

        mqtt_layout.add_widget(MDLabel(text="Status:", size_hint_y=None, height=30))
        self.status_label = MDLabel(text=self.connection_status, size_hint_y=None, height=30)
        mqtt_layout.add_widget(self.status_label)

        self.connect_button = MDRaisedButton(text="Connect")
        self.connect_button.bind(on_press=self.connect_to_broker)
        mqtt_layout.add_widget(self.connect_button)

        self.local_time_label = MDLabel(text=self.local_time, font_size=20, size_hint_y=None, height=30)
        mqtt_layout.add_widget(self.local_time_label)

        self.add_widget(mqtt_layout)

    def connect_to_broker(self, instance):
        # Placeholder function to handle MQTT connection
        print(f"Connecting to broker... {self.broker_input.text} {self.port_input.text}")
        self.connect(
            self.broker_input.text, int(self.port_input.text), self.device_id_input.text
        )
        self.set_mqtt_callbacks()

class MqttSettingsApp(MDApp):
    def build(self):
        layout = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        self.MQTTSettingsWidget = MQTTSettingsWidget()
        layout.add_widget(self.MQTTSettingsWidget)
        return layout

if __name__ == "__main__":
    MqttSettingsApp().run()
