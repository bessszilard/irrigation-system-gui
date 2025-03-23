from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from kivy.clock import mainthread

class MQTTSettingsWidget(MDCard):
    connection_status = StringProperty("Disconnected")
    local_time = StringProperty("--:--")

    def update_local_time_hd(self, new_time):
        self.local_time_label.text = f"{new_time}"

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
        self.size_hint_x = 0.5
        self.padding = 10
        self.spacing = 10
        self.orientation = "vertical"
        
        mqtt_layout = GridLayout(cols=2, spacing=5)
        
        mqtt_layout.add_widget(MDLabel(text="MQTT Server:", size_hint_y=None, height=30))
        self.broker_input = MDTextField(text="broker.emqx.io")
        mqtt_layout.add_widget(self.broker_input)

        mqtt_layout.add_widget(MDLabel(text="Port:", size_hint_y=None, height=30))
        self.port_input = MDTextField(text="1883")
        mqtt_layout.add_widget(self.port_input)

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
        print("Connecting to broker...")


class MqttSettingsApp(MDApp):
    def build(self):
        layout = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        self.MQTTSettingsWidget = MQTTSettingsWidget()
        layout.add_widget(self.MQTTSettingsWidget)
        return layout

if __name__ == "__main__":
    MqttSettingsApp().run()