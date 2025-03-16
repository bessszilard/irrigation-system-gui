from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.boxlayout import BoxLayout
import json

class ColoredLabel(Label):
    def __init__(self, text, state, **kwargs):
        super().__init__(text=text, **kwargs)
        self.state = state
        self.size_hint_y = None
        self.height = 40
        self.update_background()
    
    def update_background(self):
        with self.canvas.before:
            self.canvas.before.clear()
            # Blue for Opened, Gray for Closed
            Color(0.29, 0.56, 0.89, 1) if self.state == "Opened" else Color(0.63, 0.63, 0.63, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def update_state(self, new_state):
        self.state = new_state
        self.update_background()
        self.text = new_state

class AutoCheckbox(BoxLayout):
    def __init__(self, relay, callback, **kwargs):
        super().__init__(orientation="horizontal", size_hint_x=0.3, **kwargs)
        self.relay = relay
        self.callback = callback

        self.add_widget(Label(text="Auto"))
        self.checkbox = CheckBox()
        self.checkbox.bind(active=self.on_checkbox_toggle)
        self.add_widget(self.checkbox)

    def on_checkbox_toggle(self, instance, value):
        """Calls the provided callback when checkbox state changes."""
        self.callback(self.relay, value)


class RelayStatesWidget(GridLayout):
    def __init__(self, toggle_handler=None , **kwargs):
        super().__init__(**kwargs)
        self.__label_map = {}
        self.__buttons = {}
        self.__checkboxes = {}
        self.__toggle_handler = toggle_handler
        self.__built_already = False
        self.__auto_handler = None
        self.__is_relay_opened = {}

        
    def toggle(self, relay):
        if relay != "RXX":
            state = self.__label_map[f"{relay}_state"].state
        else:
            state = self.__label_map[f"R01_state"].state # check the first relay
        if state == "Closed":
            state = "Opened"
        else:
            state = "Closed"

        print(f"toggled {relay} to {state}")
        if self.__toggle_handler:
            self.__toggle_handler(relay, state)

    def auto_mode_changed(self, relay, state):
        """Handles checkbox toggle: enables/disables the button and calls handler"""
        if relay == "RXX":
            for button in self.__buttons.values():
                button.disabled = state
        else:
            self.__buttons[f"{relay}_toggle"].disabled = state
        print(f"Auto mode for {relay}: {'Enabled' if state else 'Disabled'}")
        
        if self.__auto_handler:
            self.__auto_handler(relay, state)

    def build_or_update(self, relay_data):
        if False == self.__built_already:
            self.cols = len(next(iter(relay_data.values()))) + 3  # Number of attributes +3 for relay name and toggle button, and the checkbox
            self.size_hint_y = None
            self.bind(minimum_height=self.setter('height'))
            self.row_default_height = 40  # Fixed row height
            self.padding = [10, 10]
            self.spacing = 5
            self.height = (len(relay_data) + 1) * self.row_default_height  # Set height dynamically
            
            # Header Row
            self.__label_map["Relay_header"] = Label(text="Relay", size_hint_y=None, height=self.row_default_height)
            self.__label_map["State"]        = Label(text="State", size_hint_y=None, height=self.row_default_height)
            self.__label_map["Command"]      = Label(text="Command", size_hint_y=None, height=self.row_default_height)
            self.__label_map["Priority"]     = Label(text="Priority", size_hint_y=None, height=self.row_default_height)
            self.add_widget(self.__label_map["Relay_header"])
            self.add_widget(self.__label_map["State"])
            self.add_widget(self.__label_map["Command"])
            self.add_widget(self.__label_map["Priority"])

            relay = "RXX" # all
            self.__buttons[f"{relay}_toggle"] = Button(text="Toggle all")
            self.__buttons[f"{relay}_toggle"].bind(on_press=lambda instance, r=relay: self.toggle(r))
            self.add_widget(self.__buttons[f"{relay}_toggle"])

            auto_checkbox = AutoCheckbox(relay, self.auto_mode_changed)
            self.add_widget(auto_checkbox)

            self.__built_already = True
        
        # Add relay data
        for relay, attributes in relay_data.items():
            if f'{relay}_name' not in self.__label_map.keys(): # add new item
                self.__label_map[f"{relay}_name"] = Label(text=relay, size_hint_y=None, height=self.row_default_height)
                self.__label_map[f"{relay}_state"] = ColoredLabel(text=attributes.get("state", ""), state=attributes.get("state", ""), size_hint_y=None, height=self.row_default_height)
                self.__label_map[f"{relay}_cmd"] = Label(text=attributes.get("cmd", ""), size_hint_y=None, height=self.row_default_height)
                self.__label_map[f"{relay}_priority"] = Label(text=attributes.get("priority", ""), size_hint_y=None, height=self.row_default_height)
                self.add_widget(self.__label_map[f"{relay}_name"])
                self.add_widget(self.__label_map[f"{relay}_state"])
                self.add_widget(self.__label_map[f"{relay}_cmd"])
                self.add_widget(self.__label_map[f"{relay}_priority"])

                self.__buttons[f"{relay}_toggle"] = Button(text="Toggle")
                self.__buttons[f"{relay}_toggle"].bind(on_press=lambda instance, r=relay: self.toggle(r))
                # self.__buttons[f"{relay}_toggle"].bind(on_press=partial(self.toggle, relay, attributes.get("state", "")))
                
                self.add_widget(self.__buttons[f"{relay}_toggle"])

                auto_checkbox = AutoCheckbox(relay, self.auto_mode_changed)
                self.add_widget(auto_checkbox)

            else: # just update
                self.__label_map[f"{relay}_state"].update_state(attributes.get("state", ""))
                self.__label_map[f"{relay}_cmd"].text = attributes.get("cmd", "")
                self.__label_map[f"{relay}_priority"].text = attributes.get("priority", "")


class RelayApp(App):
    def build(self):
        relay_data = """{
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
        """
        scroll_view = ScrollView(size_hint=(1, 1))  # Allow scrolling
        grid = RelayStatesWidget(size_hint_y=None)
        relay_data = json.loads(relay_data)
        grid.build_or_update(relay_data)
        scroll_view.add_widget(grid)
        grid.build_or_update(relay_data)

        return scroll_view

if __name__ == "__main__":
    RelayApp().run()
