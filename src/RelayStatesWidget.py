from kivymd.app import MDApp
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.boxlayout import MDBoxLayout
import json

class ColoredLabel(MDLabel):
    def __init__(self, text, state, **kwargs):
        super().__init__(text=text, **kwargs)
        self.state = state
        self.size_hint_y = None
        self.height = 40
        self.theme_text_color = "Custom"
        self.update_background()
    
    def update_background(self):
        if self.state == "Opened":
            self.text_color = (0.29, 0.56, 0.89, 1)
        else:
            self.text_color = (0.63, 0.63, 0.63, 1)
    
    def update_state(self, new_state):
        self.state = new_state
        self.update_background()
        self.text = new_state

class AutoCheckbox(MDBoxLayout):
    def __init__(self, relay, callback, **kwargs):
        super().__init__(orientation="horizontal", size_hint_x=0.5, **kwargs)
        self.relay = relay
        self.callback = callback
        
        self.add_widget(MDLabel(text="Auto"))
        self.checkbox = MDCheckbox()
        self.checkbox.bind(active=self.on_checkbox_toggle)
        self.add_widget(self.checkbox)

    def on_checkbox_toggle(self, instance, value):
        self.callback(self.relay, value)

class RelayStatesWidget(MDGridLayout):
    def __init__(self, toggle_handler=None, **kwargs):
        super().__init__(**kwargs)
        self.__label_map = {}
        self.__buttons = {}
        self.__checkboxes = {}
        self.__toggle_handler = toggle_handler
        self.__built_already = False
        self.__auto_handler = None

    def toggle(self, relay):
        state = self.__label_map[f"{relay}_state"].state if relay != "RXX" else self.__label_map["R01_state"].state
        state = "Opened" if state == "Closed" else "Closed"
        print(f"Toggled {relay} to {state}")
        if self.__toggle_handler:
            self.__toggle_handler(relay, state)

    def auto_mode_changed(self, relay, state):
        if relay == "RXX":
            for button in self.__buttons.values():
                button.disabled = state
        else:
            self.__buttons[f"{relay}_toggle"].disabled = state
        print(f"Auto mode for {relay}: {'Enabled' if state else 'Disabled'}")
        if self.__auto_handler:
            self.__auto_handler(relay, state)

    def build_or_update(self, relay_data):
        if not self.__built_already:
            self.cols = len(next(iter(relay_data.values()))) + 3
            self.size_hint_y = None
            self.row_default_height = 40
            self.padding = [10, 10]
            self.spacing = 5
            self.height = (len(relay_data) + 1) * self.row_default_height
            
            self.__label_map["Relay_header"] = MDLabel(text="Relay", size_hint_y=None, height=self.row_default_height)
            self.__label_map["State"] = MDLabel(text="State", size_hint_y=None, height=self.row_default_height)
            self.__label_map["Command"] = MDLabel(text="Command", size_hint_y=None, height=self.row_default_height)
            self.__label_map["Priority"] = MDLabel(text="Priority", size_hint_y=None, height=self.row_default_height)
            self.add_widget(self.__label_map["Relay_header"])
            self.add_widget(self.__label_map["State"])
            self.add_widget(self.__label_map["Command"])
            self.add_widget(self.__label_map["Priority"])

            relay = "RXX"
            self.__buttons[f"{relay}_toggle"] = MDRaisedButton(text="Toggle all")
            self.__buttons[f"{relay}_toggle"].bind(on_press=lambda instance, r=relay: self.toggle(r))
            self.add_widget(self.__buttons[f"{relay}_toggle"])
            self.add_widget(AutoCheckbox(relay, self.auto_mode_changed))
            self.__built_already = True
        
        for relay, attributes in relay_data.items():
            if f'{relay}_name' not in self.__label_map:
                self.__label_map[f"{relay}_name"] = MDLabel(text=relay, size_hint_y=None, height=self.row_default_height)
                self.__label_map[f"{relay}_state"] = ColoredLabel(text=attributes.get("state", ""), state=attributes.get("state", ""), size_hint_y=None, height=self.row_default_height)
                self.__label_map[f"{relay}_cmd"] = MDLabel(text=attributes.get("cmd", ""), size_hint_y=None, height=self.row_default_height)
                self.__label_map[f"{relay}_priority"] = MDLabel(text=attributes.get("priority", ""), size_hint_y=None, height=self.row_default_height)
                self.add_widget(self.__label_map[f"{relay}_name"])
                self.add_widget(self.__label_map[f"{relay}_state"])
                self.add_widget(self.__label_map[f"{relay}_cmd"])
                self.add_widget(self.__label_map[f"{relay}_priority"])

                self.__buttons[f"{relay}_toggle"] = MDRaisedButton(text="Toggle")
                self.__buttons[f"{relay}_toggle"].bind(on_press=lambda instance, r=relay: self.toggle(r))
                self.add_widget(self.__buttons[f"{relay}_toggle"])
                self.add_widget(AutoCheckbox(relay, self.auto_mode_changed))
            else:
                self.__label_map[f"{relay}_state"].update_state(attributes.get("state", ""))
                self.__label_map[f"{relay}_cmd"].text = attributes.get("cmd", "")
                self.__label_map[f"{relay}_priority"].text = attributes.get("priority", "")

class RelayApp(MDApp):
    def build(self):
        relay_data = json.loads("""{
        "R01": { "state": "Opened", "cmd": "Manua;RXX;Closed;P00;F", "priority": "P00"},
        "R02": { "state": "Closed", "cmd": "Manua;RXX;Closed;P00;F", "priority": "P00"},
        "R03": { "state": "Opened", "cmd": "Manua;RXX;Closed;P00;F", "priority": "P00"},
        "R04": { "state": "Closed", "cmd": "Manua;RXX;Closed;P00;F", "priority": "P00"},
        "R05": { "state": "Opened", "cmd": "Manua;RXX;Closed;P00;F", "priority": "P00" },
        "R06": { "state": "Closed", "cmd": "Manua;RXX;Closed;P00;F", "priority": "P00" },
        "R07": { "state": "Closed", "cmd": "Manua;RXX;Closed;P00;F", "priority": "P00" },
        "R08": { "state": "Closed", "cmd": "Manua;RXX;Closed;P00;F", "priority": "P00" },
        "R09": { "state": "Closed", "cmd": "Manua;RXX;Closed;P00;F", "priority": "P00" },
        "R10": { "state": "Closed", "cmd": "Manua;RXX;Closed;P00;F", "priority": "P00" },
        "R11": { "state": "Closed", "cmd": "Manua;RXX;Closed;P00;F", "priority": "P00" },
        "R12": { "state": "Closed", "cmd": "Manua;RXX;Closed;P00;F", "priority": "P00" },
        "R13": { "state": "Closed", "cmd": "Manua;RXX;Closed;P00;F", "priority": "P00" },
        "R14": { "state": "Closed", "cmd": "Manua;RXX;Closed;P00;F", "priority": "P00" },
        "R15": { "state": "Closed", "cmd": "Manua;RXX;Closed;P00;F", "priority": "P00" },
        "R16": { "state": "Closed", "cmd": "Manua;RXX;Closed;P00;F", "priority": "P00" }}
        """)
        scroll_view = MDScrollView()
        grid = RelayStatesWidget(size_hint_y=None)
        grid.build_or_update(relay_data)
        scroll_view.add_widget(grid)
        return scroll_view

        return scroll_view

if __name__ == "__main__":
    RelayApp().run()
