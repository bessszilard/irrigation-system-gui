import json
import os

from kivy.clock import mainthread
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField

bulk_actions_list = [
    ("Save", "SAVE_ALL_CMDS", True),
    ("Reset", "RESET_CMDS_TO_DEFAULT", True),
    ("Load", "LOAD_ALL_CMDS", True),
    ("Import", "IMPORT_FROM_FILE", False),
    ("Export", "EXPORT_CMD", False),
]

START_CHAR = "startChar"
END_CHAR = "endChar"

class CommandWidget(MDBoxLayout):

    def __init__(self, mqtt_command_manager=None, **kwargs):
        super().__init__(
            orientation="vertical", spacing=dp(10), padding=dp(10), **kwargs
        )
        self.mqtt_command_manager = mqtt_command_manager
        self.command_data = {}
        self.menus = {}
        self.menu_buttons = {}
        self.command_list_data = None

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

        for label, action, use_mqtt in bulk_actions_list:
            btn = MDRaisedButton(
                text=label, size_hint=(None, None), size=(dp(100), dp(40))
            )
            if use_mqtt:
                btn.bind(
                    on_release=lambda instance, action=action: self.mqtt_command_manager(
                        action
                    )
                )
            else:
                btn.bind(
                    on_release=lambda instance, action=action: self.file_cmd_manager(
                        action
                    )
                )

            self.bulk_actions_layout.add_widget(btn)

        self.add_widget(self.bulk_actions_layout)  # placeholder for command selectors
        self.add_widget(self.options_container)  # placeholder for command selectors
        self.add_widget(command_list_scroll)

        self.manager_open = False
        self.file_manager = MDFileManager(
            select_path=self.load_json,
            exit_manager=self.close_file_manager,
            preview=True,
            search='all'  # allow files
        )
        self.file_manager.ext = [".json"]

    def file_cmd_manager(self, action):
        if action == "IMPORT_FROM_FILE":
            data = self.open_file_manager()
            pass
        elif action == "EXPORT_TO_FILE":
            self.export_json()
            pass

    @mainthread
    def rebuild_cmd_options(self, command_options_data):
        if command_options_data is None:
            return

        self.command_options_data = command_options_data

        # Add label
        label = MDLabel(text="Command:", size_hint=(None, None), size=(dp(100), dp(40)))
        self.options_container.add_widget(label)

        for key, values in self.command_options_data.items():
            if key in [START_CHAR, END_CHAR]:
                continue
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

        self.command_list_data = command_list_data

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
        if self.mqtt_command_manager:
            self.mqtt_command_manager("SAVE_ALL_CMDS")

    def reset_to_default_commands(self):
        if self.mqtt_command_manager:
            self.mqtt_command_manager("RESET_CMDS_TO_DEFAULT")

    def load_commands(self):
        if self.mqtt_command_manager:
            self.mqtt_command_manager("LOAD_CMDS")

    def add_command(self, instance):
        selected_values = {key: btn.text for key, btn in self.menu_buttons.items()}
        selected_values['description'] = self.text_input.text
        print("Selected Command:", selected_values)

        cmd = self.command_options_data[START_CHAR]
        cmd += ";".join(selected_values.values())
        cmd += self.command_options_data[END_CHAR]
        print("Sent Command: ", cmd)

        if self.mqtt_command_manager:
            self.mqtt_command_manager("ADD_CMD", cmd)

    def remove_command(self, cmd):
        print(f"Removing command: {cmd}")
        if self.mqtt_command_manager:
            self.mqtt_command_manager("REMOVE_CMD", cmd)

    def open_file_manager(self, *args):
        self.file_manager.show(os.path.expanduser("~"))  # or any folder
        self.manager_open = True

    def close_file_manager(self, *args):
        self.file_manager.close()
        self.manager_open = False

    def load_json(self, path):
        self.close_file_manager()
        if not path.lower().endswith(".json"):
            print("Invalid file selected:", path)
            return
        try:
            with open(path, "r") as f:
                data = json.load(f)
                print(f"Imported JSON content: {os.path.basename(path)} {data}")
        except Exception as e:
            print("Error:", e)

        if "cmdList" not in data:
            print("missing cmdList element")
            return

        cmd_list_compressed = ""
        for cmd in data["cmdList"]:
            cmd_list_compressed += cmd + "\n"

        print(f"Compressed cmd list: {cmd_list_compressed}")

    def export_json(self, *args):
        self.file_manager = MDFileManager(
            select_path=self.save_json_to_folder,
            exit_manager=self.close_file_manager,
            preview=False,
            search="dirs",  # ⬅ only allow selecting folders
        )
        self.file_manager.show(os.path.expanduser("~"))
        self.manager_open = True

    def save_json_to_folder(self, folder_path):
        self.close_file_manager()

        if self.command_list_data is None:
            print("Command list is empty")
            return

        export_path = os.path.join(folder_path, "exported_file.json")

        try:
            with open(export_path, "w") as f:
                json.dump(self.command_list_data, f, indent=4)
            print("Data exported to:", export_path)
        except Exception as e:
            print("Export error:", e)


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
