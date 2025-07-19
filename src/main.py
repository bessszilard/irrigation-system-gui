from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import NoTransition
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import IconLeftWidget, OneLineIconListItem
from kivymd.uix.navigationdrawer import MDNavigationDrawer, MDNavigationLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar

from CommandWidget import CommandWidget
from MQTTClient import MQTTClient
from MqttSettingsWidget import MQTTSettingsWidget
from RelayGroupsWidget import RelayGroupsWidget
from RelayStatesWidget import RelayStatesWidget
from SensorWidget import SensorWidget


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
        self.add_cb("CMD_OPTIONS", self.commandWidget.rebuild_cmd_options)
        self.add_cb("RELAYS", self.relayStateWidget.build_or_update)
        self.add_cb("RELAY_GROUPS", self.relayGroupsWidget.build_or_update)
        self.add_cb("CMD_LIST", self.commandWidget.rebuild_cmd_list, False)
        self.add_cb("CMD_RESPONSE", lambda payload: print(payload))
        self.add_cb("SENSORS", self.sensorsStateWidget.update_data)
        self.mqtt_client.setTopicsCallback(self.mqttTopicCallbacks)

    def toggle_hd(self, relay, state):
        # remove old command if exists
        priority = "PTX" if relay == "RXX" else "PTO"

        current_command = f"%Manua;{priority};{relay};{state}#"
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

        # TODOsz do I need this?
        # # Add label in the drawer
        # drawer_content.add_widget(MDLabel(
        #     text="Navigation",
        #     font_style="H6",
        #     size_hint_y=None,
        #     height="30dp"
        # ))

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

        button4 = OneLineIconListItem(text="Relay groups")
        button4.add_widget(IconLeftWidget(icon="group"))
        button4.bind(on_release=self.on_relay_groups_button_click)
        drawer_list.add_widget(button4)

        button5 = OneLineIconListItem(text="Sensors")
        button5.add_widget(IconLeftWidget(icon="thermometer"))
        button5.bind(on_release=self.on_sensor_button_click)
        drawer_list.add_widget(button5)

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
        self.commandWidget = CommandWidget(self.mqtt_client.commandManager)
        commands_screen.add_widget(self.commandWidget)
        self.screen_manager.add_widget(commands_screen)

        relay_states_sc = MDScreen(name="relay")
        relay_states_scroll_view = MDScrollView()
        self.relayStateWidget = RelayStatesWidget(self.toggle_hd)
        relay_states_scroll_view.add_widget(self.relayStateWidget)
        relay_states_sc.add_widget(relay_states_scroll_view)
        self.screen_manager.add_widget(relay_states_sc)

        relay_groups_sc = MDScreen(name="relay_groups")
        relay_groups_scroll_view = MDScrollView()
        self.relayGroupsWidget = RelayGroupsWidget(self.mqtt_client.set_relay_groups)
        relay_groups_scroll_view.add_widget(self.relayGroupsWidget)
        relay_groups_sc.add_widget(relay_groups_scroll_view)
        self.screen_manager.add_widget(relay_groups_sc)

        sensors_screen = MDScreen(name="sensors")
        sensors_scroll_view = MDScrollView()
        self.sensorsStateWidget = SensorWidget()
        sensors_scroll_view.add_widget(self.sensorsStateWidget)
        sensors_screen.add_widget(sensors_scroll_view)
        self.screen_manager.add_widget(sensors_screen)

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

    def on_sensor_button_click(self, instance):
        self.screen_manager.current = "sensors"

    def on_relay_groups_button_click(self, instance):
        self.screen_manager.current = "relay_groups"


if __name__ == "__main__":
    MainApp().run()
