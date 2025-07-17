from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField

NO_GROUP_SELECTED = "Select Group"

KV = """
<RelayGroupsWidget>:
    orientation: 'vertical'
    padding: 10
    spacing: 10

    MDBoxLayout:
        size_hint_y: None
        height: self.minimum_height
        spacing: 10

        MDRaisedButton:
            text: "Set"
            on_release: root.on_set()

        MDRaisedButton:
            text: "Reload"
            on_release: root.on_reload()

        MDRaisedButton:
            text: "Reset to Default"
            on_release: root.on_reset()

    ScrollView:
        MDBoxLayout:
            id: relay_container
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            spacing: 10
"""

class RelayGroupsWidget(MDBoxLayout):
    relay_widgets = ObjectProperty({})
    group_options = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.relay_widgets = {}  # store: {relay_key: (label, menu)}

    def build_or_update(self, json_data):
        groups = json_data["RelayGroups"]
        relays = json_data["Relays"]

        self.group_options = [f"Group {g}" for g in groups]
        container = self.ids.relay_container

        for relay_key, group_val in relays.items():
            if relay_key not in self.relay_widgets:
                # Create UI for the first time
                row = MDBoxLayout(size_hint_y=None, height="48dp", spacing=10)

                relay_label = MDLabel(text=f"Relay {relay_key[1:]}", size_hint_x=0.3)

                # Dropdown setup
                # Create dropdown button
                # TODOsz update color
                dropdown_button = MDFlatButton(
                    text=f"Group {group_val}" if group_val else NO_GROUP_SELECTED,
                    size_hint_x=0.7,
                )

                # Dropdown menu setup
                menu_items = [
                    {
                        "text": group_text,
                        "on_release": lambda x=group_text, k=relay_key: self.set_group(k, x)
                    } for group_text in self.group_options
                ]
                menu = MDDropdownMenu(
                    caller=dropdown_button,
                    items=menu_items,
                    width_mult=4
                )
                dropdown_button.bind(on_release=lambda btn, m=menu: self.open_menu(btn, m))
                menu.caller = dropdown_button

                row.add_widget(relay_label)
                row.add_widget(dropdown_button)

                container.add_widget(row)
                self.relay_widgets[relay_key] = (relay_label, dropdown_button, menu)
            else:
                # Update existing dropdown text
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
            # Optionally: store updated value to internal state or emit event
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
        Builder.load_string(KV)
        widget = RelayGroupsWidget()
        sample_json = {
            "RelayGroups": ["A", "B", "C", "D", "E", "F", "G", "H"],
            "Relays": {"R01": "B", "R02": "", "R03": "", "R04": "A", "R05": "C", "R06": "", "R07": "", "R08": "D", "R09": "", "R10": "", "R11": "", "R12": "", "R13": "", "R14": "", "R15": "", "R16": "",
            },
        }
        widget.build_or_update(sample_json)
        return widget


if __name__ == "__main__":
    TestApp().run()
