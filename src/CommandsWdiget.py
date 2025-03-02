from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
import json

class CommandWidget(BoxLayout):
    def __init__(self, send_command_cb=None, **kwargs):
        super().__init__(orientation='horizontal', **kwargs)
        self.send_command_cb = send_command_cb # default None

    def rebuild(self, command_data):
        if command_data == None:
            return

        self.command_data = command_data
        self.spinners = {}

        label = Label(text="Command: ", size_hint=(None, None), size=(120, 44))
        self.add_widget(label)
        
        # Create dropdowns for each key in command_data
        for key, values in self.command_data.items():
            spinner = Spinner(
                text=values[0],
                values=values,
                size_hint=(None, None),
                size=(100, 40)
            )
            self.spinners[key] = spinner
            self.add_widget(spinner)
        
        # Add send button
        self.text_input = TextInput(
                    hint_text="Enter some text here", 
                    size_hint=(None, None),
                    multiline=False,
                    size=(180, 40))
        self.add_widget(self.text_input)

        # Add send button
        self.send_button = Button(
            text="Send",
            size_hint=(None, None),
            size=(100, 40)
        )

        self.send_button.bind(on_press=self.send_command)
        self.add_widget(self.send_button)
    
    def send_command(self, instance):
        selected_values = {key: spinner.text for key, spinner in self.spinners.items()}
        selected_values['description'] = self.text_input.text
        print("Selected Command:", selected_values)  # Replace with actual send logic
        
        cmd = ""
        for value in selected_values.values():
            cmd += f"{value};"
        print("Sent Command: ", cmd)  # Replace with actual send logic
        if self.send_command_cb:
            self.send_command_cb(cmd)

# Sample JSON data
command_json = """
    {"CommandType": ["Manua", "ATemp", "AHumi", "ATime", "AFlow", "AMost"], 
     "RelayIds": ["R01", "R02", "R03", "R04", "R05", "R06", "R07", "R08", "R09", "R10", "R11", "R12", "R13", "R14", "R15", "R16", "RXX"], 
     "RelayState": ["Opened", "Closed"], 
     "CmdPriority": ["PLW", "P00", "P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08", "P09", "PHI"]}
"""

class CommandApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        command_data = json.loads(command_json)
        self.commandWidget = CommandWidget()
        self.commandWidget.rebuild(command_data)
        layout.add_widget(self.commandWidget)
        return layout

if __name__ == "__main__":
    CommandApp().run()
