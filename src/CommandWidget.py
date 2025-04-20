import json

from kivy.clock import mainthread
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField

bulk_actions_list = [
    ("Save", "SAVE_ALL_CMDS"),
    ("Reset", "RESET_CMDS_TO_DEFAULT"),
    ("Load", "LOAD_ALL_CMDS"),
]

class CommandWidget(MDBoxLayout):

    def __init__(self, command_manager=None, **kwargs):
        super().__init__(
            orientation="vertical", spacing=dp(10), padding=dp(10), **kwargs
        )
        self.command_manager = command_manager
        self.command_data = {}
        self.menus = {}
        self.menu_buttons = {}

        # Add containers for both sections
        self.bulk_actions_layout = MDBoxLayout(
            orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(50)
        )
        self.options_container = MDBoxLayout(
            orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(50)
        )
        self.commands_list_container = MDBoxLayout(
            orientation="vertical", spacing=dp(5), size_hint_y=None
        )
        self.commands_list_container.bind(
            minimum_height=self.commands_list_container.setter("height")
        )

        command_list_scroll = ScrollView()
        command_list_scroll.add_widget(self.commands_list_container)
        command_list_scroll.size_hint_y = 1

        for label, command in bulk_actions_list:
            btn = MDRaisedButton(
                text=label, size_hint=(None, None), size=(dp(100), dp(40))
            )
            btn.bind(on_release=lambda instance, cmd=command: self.command_manager(cmd))
            self.bulk_actions_layout.add_widget(btn)

        self.add_widget(self.bulk_actions_layout)  # placeholder for command selectors
        self.add_widget(self.options_container)  # placeholder for command selectors
        self.add_widget(command_list_scroll)

    @mainthread
    def rebuild_cmd_options(self, command_options_data):
        if command_options_data is None:
            return

        self.command_options_data = command_options_data

        # Add label
        label = MDLabel(text="Command:", size_hint=(None, None), size=(dp(100), dp(40)))
        self.options_container.add_widget(label)

        for key, values in self.command_options_data.items():
            button = MDRaisedButton(
                text=values[0], size_hint=(None, None), size=(dp(100), dp(40))
            )
            self.menu_buttons[key] = button

            menu = MDDropdownMenu(
                caller=button,
                items=[
                    {
                        "viewclass": "OneLineListItem",
                        "text": v,
                        "on_release": lambda x=v, k=key: self.set_menu_value(k, x),
                    }
                    for v in values
                ],
                width_mult=4,
            )
            self.menus[key] = menu
            button.bind(on_release=lambda *args, m=menu: m.open())
            self.options_container.add_widget(button)

        # Add text input
        self.text_input = MDTextField(
            hint_text="Enter some text here",
            size_hint=(None, None),
            size=(dp(180), dp(40)),
        )
        self.options_container.add_widget(self.text_input)

        # Add send button
        self.add_command_btn = MDRaisedButton(
            text="Add", size_hint=(None, None), size=(dp(100), dp(40))
        )
        self.add_command_btn.bind(on_release=self.add_command)
        self.options_container.add_widget(self.add_command_btn)

    @mainthread
    def rebuild_cmd_list(self, command_list_data):
        print(f"rebuilding command list based on {command_list_data}")

        self.commands_list_container.clear_widgets()

        if not command_list_data or "cmdList" not in command_list_data:
            return

        for cmd in command_list_data["cmdList"]:
            row = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(10),
                size_hint_y=None,
                height=dp(40),
            )

            label = MDLabel(
                text=cmd, halign="left", size_hint_x=0.9, theme_text_color="Primary"
            )

            remove_btn = MDIconButton(
                icon="close",
                theme_text_color="Custom",
                text_color=(1, 0, 0, 1),  # Red color
                size_hint_x=0.1,
                on_release=lambda instance, c=cmd: self.remove_command(c),
            )

            row.add_widget(label)
            row.add_widget(remove_btn)

            self.commands_list_container.add_widget(row)

    def set_menu_value(self, key, value):
        self.menu_buttons[key].text = value
        self.menus[key].dismiss()

    def save_commands(self):
        if self.command_manager:
            self.command_manager("SAVE_ALL_CMDS")

    def reset_to_default_commands(self):
        if self.command_manager:
            self.command_manager("RESET_CMDS_TO_DEFAULT")

    def load_commands(self):
        if self.command_manager:
            self.command_manager("LOAD_CMDS")

    def add_command(self, instance):
        selected_values = {key: btn.text for key, btn in self.menu_buttons.items()}
        selected_values['description'] = self.text_input.text
        print("Selected Command:", selected_values)

        cmd = ""
        for value in selected_values.values():
            cmd += f"{value};"
        print("Sent Command: ", cmd)
        if self.command_manager:
            self.command_manager("ADD_CMD", cmd)

    def remove_command(self, cmd):
        print(f"Removing command: {cmd}")
        if self.command_manager:
            self.command_manager("REMOVE_CMD", cmd)


# Sample JSON data
command_options = """
    {"CommandType": ["Manua", "ATemp", "AHumi", "ATime", "AFlow", "AMost"], 
     "RelayIds": ["R01", "R02", "R03", "R04", "R05", "R06", "R07", "R08", "R09", "R10", "R11", "R12", "R13", "R14", "R15", "R16", "RXX"], 
     "RelayState": ["Opened", "Closed"], 
     "CmdPriority": ["PLW", "P00", "P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08", "P09", "PHI"]}
"""

command_list = """
    {"cmdList": ["Manua;RXX;Closed;P00;F", "Manua;R03;Opened;PTO;", "Manua;R02;Closed;PTO;", "Manua;RXX;Closed;PTX;", "ATime;R09;Closed;P07;;"]}
"""


class CommandApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "BlueGray"
        screen = MDScreen()
        layout = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(10))
        command_options_data = json.loads(command_options)
        command_list_data = json.loads(command_list)
        self.commandWidget = CommandWidget()
        self.commandWidget.rebuild_cmd_options(command_options_data)
        self.commandWidget.rebuild_cmd_list(command_list_data)
        layout.add_widget(self.commandWidget)
        screen.add_widget(layout)
        return screen


if __name__ == "__main__":
    CommandApp().run()
