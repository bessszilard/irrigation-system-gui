from kivy.properties import ObjectProperty
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen

NO_GROUP_SELECTED = "Select Group"


class RelayGroupsWidget(MDBoxLayout):
    relay_widgets = ObjectProperty({})
    group_options = []

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=10, padding=10, **kwargs)
        self.relay_widgets = {}

        # Top control buttons
        top_buttons = MDBoxLayout(size_hint_y=None, height="48dp", spacing=10)

        set_btn = MDRaisedButton(text="Set", on_release=lambda x: self.on_set())
        reload_btn = MDRaisedButton(
            text="Reload", on_release=lambda x: self.on_reload()
        )
        reset_btn = MDRaisedButton(
            text="Reset to Default", on_release=lambda x: self.on_reset()
        )

        top_buttons.add_widget(set_btn)
        top_buttons.add_widget(reload_btn)
        top_buttons.add_widget(reset_btn)
        self.add_widget(top_buttons)

        # Scroll container for relay rows
        self.scroll = ScrollView()
        self.container = MDBoxLayout(
            orientation="vertical", size_hint_y=None, spacing=10
        )
        self.container.bind(minimum_height=self.container.setter("height"))

        self.scroll.add_widget(self.container)
        self.add_widget(self.scroll)

    def build_or_update(self, json_data):
        groups = json_data["RelayGroups"]
        relays = json_data["Relays"]

        self.group_options = [f"Group {g}" for g in groups]

        for relay_key, group_val in relays.items():
            if relay_key not in self.relay_widgets:
                # New UI row
                row = MDBoxLayout(size_hint_y=None, height="48dp", spacing=10)

                relay_label = MDLabel(text=f"Relay {relay_key[1:]}", size_hint_x=0.3)

                dropdown_button = MDFlatButton(
                    text=f"Group {group_val}" if group_val else NO_GROUP_SELECTED,
                    size_hint_x=0.7,
                )

                menu_items = [
                    {
                        "text": group_text,
                        "on_release": lambda x=group_text, k=relay_key: self.set_group(
                            k, x
                        ),
                    }
                    for group_text in self.group_options
                ]
                menu = MDDropdownMenu(
                    caller=dropdown_button, items=menu_items, width_mult=4
                )
                dropdown_button.bind(
                    on_release=lambda btn, m=menu: self.open_menu(btn, m)
                )

                row.add_widget(relay_label)
                row.add_widget(dropdown_button)

                self.container.add_widget(row)
                self.relay_widgets[relay_key] = (relay_label, dropdown_button, menu)
            else:
                # Update existing dropdown
                label, dropdown_button, _ = self.relay_widgets[relay_key]
                dropdown_button.text = (
                    f"Group {group_val}" if group_val else NO_GROUP_SELECTED
                )

    def open_menu(self, caller_button, menu):
        menu.caller = caller_button
        menu.open()

    def set_group(self, relay_key, group_text):
        if relay_key in self.relay_widgets:
            _, dropdown_button, _ = self.relay_widgets[relay_key]
            dropdown_button.text = group_text
            print(f"Relay {relay_key} set to {group_text}")

    def on_set(self):
        print("Set clicked")
        set_group_str = ""
        for relay_key in self.relay_widgets:
            _, dropdown_button, _ = self.relay_widgets[relay_key]
            if dropdown_button.text != NO_GROUP_SELECTED:
                group_text = dropdown_button.text.replace("Group ", "")
                print(f"{relay_key} -> {group_text}")
                set_group_str += f"RG{group_text}:{relay_key};"
        print(set_group_str)

    def on_reload(self):
        print("Reload clicked")

    def on_reset(self):
        for relay_key in self.relay_widgets:
            _, dropdown_button, _ = self.relay_widgets[relay_key]
            dropdown_button.text = NO_GROUP_SELECTED

        print("Reset to Default clicked")


class TestApp(MDApp):

    def build(self):
        widget = RelayGroupsWidget()
        sample_json = {
            "RelayGroups": ["A", "B", "C", "D", "E", "F", "G", "H"],
            "Relays": {
                "R01": "B",
                "R02": "",
                "R03": "",
                "R04": "A",
                "R05": "C",
                "R06": "",
                "R07": "",
                "R08": "D",
                "R09": "",
                "R10": "",
                "R11": "",
                "R12": "",
                "R13": "",
                "R14": "",
                "R15": "",
                "R16": "",
            },
        }
        widget.build_or_update(sample_json)
        return widget


if __name__ == "__main__":
    TestApp().run()
