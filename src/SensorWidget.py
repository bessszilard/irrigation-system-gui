import json

from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen


class SensorWidget(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(10), spacing=dp(10), **kwargs)
        self.labels = {}
        self.scroll = ScrollView()
        self.content = MDBoxLayout(orientation="vertical", spacing=dp(5), size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter("height"))
        self.scroll.add_widget(self.content)
        self.add_widget(self.scroll)

    def update_data(self, data: dict):
        for key, value in data.items():
            if isinstance(value, list):
                for i, item in enumerate(value):
                    label_key = f"{key}_{i}"
                    self._add_or_update_row(label_key, item)
            else:
                self._add_or_update_row(key, value)

    def _add_or_update_row(self, key, value):
        name, unit = self._extract_name_and_unit(key)

        if key not in self.labels:
            row = MDBoxLayout(orientation="horizontal", spacing=dp(5), size_hint_y=None, height=dp(40))

            name_card = self._build_cell(name, 0.4)
            value_card = self._build_cell(self._format_value(value), 0.3)
            unit_card = self._build_cell(unit, 0.3)

            self.labels[key] = value_card.children[0]  # MDLabel inside the card

            row.add_widget(name_card)
            row.add_widget(value_card)
            row.add_widget(unit_card)
            self.content.add_widget(row)
        else:
            self.labels[key].text = self._format_value(value)

    def _build_cell(self, text, width_ratio):
        card = MDCard(
            padding=dp(5),
            radius=[0],
            style="filled",
            md_bg_color=(0.95, 0.95, 0.95, 1),
            size_hint_x=width_ratio,
        )
        label = MDLabel(text=text, halign="left", valign="middle")
        label.bind(size=label.setter("text_size"))
        card.add_widget(label)
        return card

    def _extract_name_and_unit(self, key: str):
        if "_" in key:
            parts = key.split("_", 1)
            return parts[0], parts[1]
        return key, ""

    def _format_value(self, value):
        if isinstance(value, float):
            return "null" if str(value) == "nan" else f"{value:.2f}"
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif value is None:
            return "null"
        return str(value)

# Test mode if run directly
if __name__ == "__main__":
    class TestSensorDataApp(MDApp):
        def build(self):
            self.theme_cls.primary_palette = "BlueGray"
            screen = MDScreen()
            sensor_data = {
                "externalTemp_C": 25.3,
                "humidity": 60.0,
                "pressure_Pa": 101325.0,
                "flowRate_LitMin": 1.5,
                "rainSensor": 1,
                "soilMoisture": [45.3, 50.2, float('nan')],
                "valid": True
            }
            widget = SensorDataWidget()
            widget.update_data(sensor_data)
            screen.add_widget(widget)
            return screen

    TestSensorDataApp().run()
