from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.navigationdrawer import MDNavigationDrawer, MDNavigationLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen  
from kivymd.uix.toolbar import MDTopAppBar
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget
from kivy.uix.screenmanager import NoTransition
from kivy.clock import Clock
from kivymd.uix.scrollview import MDScrollView

from CommandsWdiget import CommandWidget
from RelayStatesWidget import RelayStatesWidget
from MqttSettingsWidget import MQTTSettingsWidget

from MQTTClient import MQTTClient

class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Add the MQTT layout to the main layout
        self.mqttSettingsWidget = MQTTSettingsWidget()
        self.main_layout.add_widget(self.mqttSettingsWidget)

        # Add the command widget
        self.commandWidget = CommandWidget(self.mqtt_client.addCommand)
        self.main_layout.add_widget(self.commandWidget)

        # Add the relay state widget
        self.relayStateWidget = RelayStatesWidget(self.toggle_hd)
        self.main_layout.add_widget(self.relayStateWidget)

        # Add the main layout to the screen
        self.add_widget(self.main_layout)

        self.connect_to_broker("")  # Placeholder for connection logic

    def connect_to_broker(self, instance):
        # Logic for connecting to the MQTT broker
        print("Connecting to the broker...")

    def toggle_hd(self):
        # Logic for toggling relay states
        print("Toggling relay state...")
    
    # @mainthread
    def update_status(self, status, color):
        self.connection_status = status
        self.status_label.text = status
        self.status_label.color = (0, 1, 0, 1) if color == "green" else (1, 0, 0, 1)


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mqtt_client = MQTTClient(self.on_connect)

    def on_connect(self, client, userdata, flags, rc):     
        self.mqttSettingsWidget.on_connect(client, userdata, flags, rc)

    def add_cb(self, topic_key, callback, call_on_main_thread=True):
        if False == call_on_main_thread:
            self.mqttTopicCallbacks[self.mqtt_client.SUB_TOPICS[topic_key]] = callback
            return
        self.mqttTopicCallbacks[self.mqtt_client.SUB_TOPICS[topic_key]] = lambda payload: Clock.schedule_once(lambda dt: callback(payload))

    def set_callbacks(self):
        self.mqttTopicCallbacks = {}

        sub_top = self.mqtt_client.SUB_TOPICS
        self.mqttTopicCallbacks[self.mqtt_client.SUB_TOPICS["LOCAL_TIME"]] = self.mqttSettingsWidget.update_local_time_hd
        self.add_cb("CMD_OPTIONS",  self.commandWidget.rebuild)
        # self.add_cb("SENSORS",  self.commandWidget.rebuild)
        self.add_cb("RELAYS", self.relayStateWidget.build_or_update)
        self.add_cb("CMD_LIST", self.commandWidget.add_command_list, False)
        self.mqtt_client.setTopicsCallback(self.mqttTopicCallbacks)

    def toggle_hd(self, relay, state):
        # remove old command if exists
        priority = "PTX" if relay == "RXX" else "PTO"

        current_command = f"Manua;{relay};{state};{priority};"
        self.mqtt_client.overrideCommand(current_command)
        print(f"Toggle {relay} {state}")
    
    def build(self):
      # Create the MDNavigationLayout (This handles both the navigation drawer and the screen manager)
        nav_layout = MDNavigationLayout()

        # Create the MDNavigationDrawer
        nav_drawer = MDNavigationDrawer(
            radius=(0, 16, 16, 0),  # Rounded corners for the drawer
            md_bg_color=(1, 1, 1, 1),  # White background for the drawer
            scrim_color=(0, 0, 0, 0.3)  # Slight gray background for inactive parts
        )

        # Create the BoxLayout for the drawer content
        drawer_content = BoxLayout(orientation="vertical", spacing=8, padding=8)

        # Add label in the drawer
        drawer_content.add_widget(MDLabel(
            text="Navigation",
            font_style="H6",
            size_hint_y=None,
            height="30dp"
        ))

        # Create the MDList for sidebar buttons
        drawer_list = BoxLayout(orientation="vertical", size_hint_y=None)
        drawer_list.height = "200dp"  # Set height of the list

        # Add sidebar buttons (OneLineIconListItems)
        button1 = OneLineIconListItem(text="MQTT")
        button1.add_widget(IconLeftWidget(icon="wifi"))
        button1.bind(on_release=self.on_mqtt_button_click)
        drawer_list.add_widget(button1)

        button2 = OneLineIconListItem(text="Commands")
        button2.add_widget(IconLeftWidget(icon="code-braces"))
        button2.bind(on_release=self.on_commands_button_click)
        drawer_list.add_widget(button2)

        button3 = OneLineIconListItem(text="Relay States")
        button3.add_widget(IconLeftWidget(icon="power"))
        button3.bind(on_release=self.on_relay_button_click)
        drawer_list.add_widget(button3)

        # Add the drawer content (list of buttons)
        nav_drawer.add_widget(drawer_content)
        drawer_content.add_widget(drawer_list)

        # Create the Screen Manager (Main content area)
        self.screen_manager = MDScreenManager(transition=NoTransition())

        # Add screens
        mqtt_screen = MDScreen(name="mqtt")
        self.mqttSettingsWidget = MQTTSettingsWidget()
        self.mqttSettingsWidget.add_cb(self.mqtt_client.connect_to_server)
        mqtt_screen.add_widget(self.mqttSettingsWidget)
        self.screen_manager.add_widget(mqtt_screen)

        commands_screen = MDScreen(name="commands")
        self.commandWidget = CommandWidget(self.mqtt_client.addCommand)
        commands_screen.add_widget(self.commandWidget)
        self.screen_manager.add_widget(commands_screen)

        relay_screen = MDScreen(name="relay")
        relay_scroll_view = MDScrollView()
        self.relayStateWidget = RelayStatesWidget(self.toggle_hd)
        relay_scroll_view.add_widget(self.relayStateWidget)
        relay_screen.add_widget(relay_scroll_view)
        self.screen_manager.add_widget(relay_screen)

        # Add the top app bar
        top_app_bar = MDTopAppBar(
            title="Irrigation System",
            left_action_items=[["menu", lambda x: nav_drawer.set_state("toggle")]]
        )

        # Combine everything into the main layout (navigation layout + top app bar + screen manager)
        layout = BoxLayout(orientation="vertical")
        layout.add_widget(top_app_bar)
        layout.add_widget(nav_layout)
        nav_layout.add_widget(self.screen_manager)
        nav_layout.add_widget(nav_drawer)

        self.set_callbacks()

        return layout

    def on_mqtt_button_click(self, instance):
        self.screen_manager.current = "mqtt"

    def on_commands_button_click(self, instance):
        self.screen_manager.current = "commands"

    def on_relay_button_click(self, instance):
        self.screen_manager.current = "relay"

if __name__ == "__main__":
    MainApp().run()

# class MQTTApp(MDApp):
#     connection_status = StringProperty("Not connected")
#     local_time = StringProperty("Waiting for time...")
    
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.mqtt_client = MQTTClient(self.on_connect)

#     def build(self):
#         main_layout = BoxLayout(orientation="vertical", padding=5, spacing=5)

#         # Grid layout for MQTT settings (2 columns, 3 rows)
#         mqtt_layout = GridLayout(cols=2, spacing=5, size_hint_x=0.5)

#         mqtt_layout.add_widget(Label(text="MQTT Server:", size_hint_y=None, height=30))
#         self.broker_input = TextInput(text="broker.emqx.io")
#         mqtt_layout.add_widget(self.broker_input)

#         mqtt_layout.add_widget(Label(text="Port:", size_hint_y=None, height=30))
#         self.port_input = TextInput(text="1883")
#         mqtt_layout.add_widget(self.port_input)

#         mqtt_layout.add_widget(Label(text="Status:", size_hint_y=None, height=30))
#         self.status_label = Label(text=self.connection_status, size_hint_y=None, height=30)
#         mqtt_layout.add_widget(self.status_label)

#         # Connect button
#         self.connect_button = Button(text="Connect")
#         self.connect_button.bind(on_press=self.connect_to_broker)
#         mqtt_layout.add_widget(self.connect_button)

#         # Local time label
#         self.local_time_label = Label(text=self.local_time, font_size=20, size_hint_y=None, height=30)
#         mqtt_layout.add_widget(self.local_time_label)

#         main_layout.add_widget(mqtt_layout)

#         # Command Widget (spans full width)
#         self.commandWidget = CommandWidget(self.mqtt_client.addCommand)
#         main_layout.add_widget(self.commandWidget)

#         # Relay States Widget (spans full width)
#         self.relayStateWidget = RelayStatesWidget(self.toggle_hd)
#         main_layout.add_widget(self.relayStateWidget)

#         self.connect_to_broker("")
#         return main_layout
    
#     def update_local_time_hd(self, new_time):
#         self.local_time_label.text = f"{new_time}"

#     def cmd_option_hd(self, payload):
#         # self.commandWidget.rebuild(payload)
#         Clock.schedule_once(lambda dt: self.commandWidget.rebuild(payload))
#         print("cmd_option_hd")

#     def cmd_option_sensors(self, payload):
#         print("cmd_option_sensors")

#     def cmd_list_hd(self, payload):
#         self.commandWidget.add_command_list(payload["cmdList"])
#         print(f"Command list {self.commandWidget.command_list}")

#     def sensors_hd(self, payload):
#         print("sensors_hd")
        
#     def relay_state_hd(self, payload):
#         print("relay_state_hd")
#         Clock.schedule_once(lambda dt: self.relayStateWidget.build_or_update(payload))

#     def toggle_hd(self, relay, state):
#         # remove old command if exists
#         priority = "PTX" if relay == "RXX" else "PTO"

#         current_command = f"Manua;{relay};{state};{priority};"
#         self.mqtt_client.overrideCommand(current_command)
#         print(f"Toggle {relay} {state}")

#     def connect_to_broker(self, instance):
#         broker = self.broker_input.text
#         try:
#             port = int(self.port_input.text)
#         except ValueError:
#             self.update_status("Invalid port number", "red")
#             return
        
#         if not self.mqtt_client.connect(broker, port):
#             self.update_status("Connection failed", "red")
#             return

#         self.mqttTopicCallbacks = {}
#         self.mqttTopicCallbacks[self.mqtt_client.SUB_TOPICS["LOCAL_TIME"]] = self.update_local_time_hd
#         self.mqttTopicCallbacks[self.mqtt_client.SUB_TOPICS["CMD_OPTIONS"]] = self.cmd_option_hd
#         self.mqttTopicCallbacks[self.mqtt_client.SUB_TOPICS["SENSORS"]] = self.sensors_hd
#         self.mqttTopicCallbacks[self.mqtt_client.SUB_TOPICS["RELAYS"]] = self.relay_state_hd
#         self.mqttTopicCallbacks[self.mqtt_client.SUB_TOPICS["CMD_LIST"]] = self.cmd_list_hd

#         self.mqtt_client.setTopicsCallback(self.mqttTopicCallbacks)

#     @mainthread
#     def update_status(self, status, color):
#         self.connection_status = status
#         self.status_label.text = status
#         self.status_label.color = (0, 1, 0, 1) if color == "green" else (1, 0, 0, 1)

#     def on_connect(self, client, userdata, flags, rc):
#         if rc == 0:
#             self.update_status("Connected", "green")
#         else:
#             self.update_status("Connection failed", "red")

# if __name__ == "__main__":
#     MQTTApp().run()