import os
import json
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import (
    StringProperty,
    NumericProperty,
    BooleanProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget

DATA_FILE = "journal.json"

KV = """
#:import dp kivy.metrics.dp
#:import rgba kivy.utils.get_color_from_hex

<BreathingWidget>:
    canvas.before:
        Color:
            rgba: rgba("#f0f4f8")  # light bg
        Rectangle:
            size: self.size
            pos: self.pos
    canvas:
        Color:
            rgba: rgba("#4da6ff")  # bright blue
        Ellipse:
            size: self.radius * 2, self.radius * 2
            pos: self.center_x - self.radius, self.center_y - self.radius

<TableRow>:
    orientation: "horizontal"
    size_hint_y: None
    height: dp(40)
    padding: dp(10), 0
    canvas.before:
        Color:
            rgba: (rgba("#e6f0ff") if self.index % 2 else rgba("#ffffff"))
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [10,]
    Label:
        text: root.timestamp
        text_size: self.size
        halign: "left"
        valign: "middle"
        color: rgba("#333333")
        font_size: dp(14)
    Label:
        text: root.mood
        text_size: self.size
        halign: "center"
        valign: "middle"
        color: rgba("#333333")
        font_size: dp(14)
    Label:
        text: root.text_entry
        text_size: self.size
        halign: "left"
        valign: "middle"
        color: rgba("#333333")
        font_size: dp(14)

<JournalScreen>:
    name: "journal"
    BoxLayout:
        orientation: "vertical"
        padding: dp(24)
        spacing: dp(16)
        canvas.before:
            Color:
                rgba: rgba("#f0f4f8")
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [16,]
        Label:
            text: "One Line Journal:"
            size_hint_y: None
            height: self.texture_size[1]
            color: rgba("#444444")
            font_size: dp(18)
            bold: True
        TextInput:
            id: entry_input
            hint_text: "Wie war dein Tag in einem Satz?"
            multiline: False
            size_hint_y: None
            padding: dp(14)
            spacing: dp(12)
            height: dp(90)
            background_normal: ''
            background_color: rgba("#ffffff")
            foreground_color: rgba("#222222")
            cursor_color: rgba("#4da6ff")
            font_size: dp(15)
        Label:
            text: "Stimmung:"
            size_hint_y: None
            height: self.texture_size[1]
            color: rgba("#444444")
            font_size: dp(18)
            bold: True
        Spinner:
            id: mood_select
            text: "gut"
            values: ["gut", "mittel", "schlecht"]
            size_hint_y: None
            height: dp(44)
            background_color: rgba("#ffffff")
            color: rgba("#222222")
            font_size: dp(16)
            canvas.before:
                Color:
                    rgba: rgba("#cbd6e2")
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [10,]
        Button:
            text: "Eintrag speichern"
            size_hint_y: None
            height: dp(48)
            background_normal: ''
            background_color: rgba("#4da6ff")
            color: rgba("#ffffff")
            font_size: dp(16)
            bold: True
            on_release: root.save_entry()
            canvas.before:
                Color:
                    rgba: self.background_color if not self.state == 'down' else rgba("#3a8de0")
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [14,]

<BreathingScreen>:
    name: "breathing"
    FloatLayout:
        canvas.before:
            Color:
                rgba: rgba("#f0f4f8")
            Rectangle:
                size: self.size
                pos: self.pos
        BreathingWidget:
            id: breathe
            size_hint: None, None
            size: min(self.parent.width, self.parent.height) * 0.7, min(self.parent.width, self.parent.height) * 0.7
            pos_hint: {"center_x": 0.5, "center_y": 0.45}
        Label:
            id: phase_lbl
            text: "Atme ein"
            font_size: "26sp"
            bold: True
            color: rgba("#4da6ff")
            size_hint: None, None
            size: self.texture_size
            pos_hint: {"center_x": 0.5, "top": 0.95}

<TableScreen>:
    name: "table"
    BoxLayout:
        orientation: "vertical"
        padding: dp(24)
        spacing: dp(12)
        canvas.before:
            Color:
                rgba: rgba("#f0f4f8")
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [16,]
        Label:
            text: "Journal Entries"
            font_size: dp(24)
            size_hint_y: None
            height: self.texture_size[1] + dp(12)
            color: rgba("#444444")
            bold: True
        BoxLayout:
            size_hint_y: None
            height: dp(40)
            padding: dp(10), 0
            canvas.before:
                Color:
                    rgba: rgba("#cbd6e2")
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [10,]
            Label:
                text: "Timestamp"
                color: rgba("#222222")
                bold: True
                font_size: dp(16)
            Label:
                text: "Mood"
                color: rgba("#222222")
                bold: True
                font_size: dp(16)
            Label:
                text: "Text"
                color: rgba("#222222")
                bold: True
                font_size: dp(16)
        RecycleView:
            id: rv
            scroll_type: ['bars', 'content']
            bar_width: dp(6)
            viewclass: "TableRow"
            RecycleBoxLayout:
                default_size: None, dp(80)
                default_size_hint: 1, None
                size_hint_y: None
                orientation: "vertical"
                height: self.minimum_height

<MainLayout>:
    orientation: "vertical"
    ScreenManager:
        id: sm
        JournalScreen:
            id: journal_scr
        BreathingScreen:
            id: breathe_scr
        TableScreen:
            id: table_scr
    BoxLayout:
        size_hint_y: None
        height: dp(60)
        spacing: dp(10)
        padding: dp(10)
        canvas.before:
            Color:
                rgba: rgba("#dbe9f4")
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [20,]
        Button:
            text: "Journal"
            font_size: dp(18)
            background_normal: ''
            background_color: rgba("#4da6ff") if sm.current == "journal" else rgba("#ffffff")
            color: rgba("#ffffff") if sm.current == "journal" else rgba("#4da6ff")
            on_release: sm.current = "journal"
            radius: [14,]
        Button:
            text: "Atmen"
            font_size: dp(18)
            background_normal: ''
            background_color: rgba("#4da6ff") if sm.current == "breathing" else rgba("#ffffff")
            color: rgba("#ffffff") if sm.current == "breathing" else rgba("#4da6ff")
            on_release: sm.current = "breathing"
            radius: [14,]
        Button:
            text: "Einträge"
            font_size: dp(18)
            background_normal: ''
            background_color: rgba("#4da6ff") if sm.current == "table" else rgba("#ffffff")
            color: rgba("#ffffff") if sm.current == "table" else rgba("#4da6ff")
            on_release:
                app.root.ids.table_scr.load_data()
                sm.current = "table"
            radius: [14,]
"""


class BreathingWidget(Widget):
    radius = NumericProperty(50)
    _growing = BooleanProperty(True)
    _min_radius = NumericProperty(30)
    _max_radius = NumericProperty(300)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self._update, 1 / 60)

    def _update(self, dt):
        if self._growing:
            self.radius += 1
            if self.radius >= self._max_radius:
                self._growing = False
                self._set_phase("Atme aus")
        else:
            self.radius -= 1
            if self.radius <= self._min_radius:
                self._growing = True
                self._set_phase("Atme ein")
                
    def _set_phase(self, text):
        scr = self.parent.parent
        if scr and scr.ids.get("phase_lbl"):
            scr.ids.get("phase_lbl").text = text

class TableRow(BoxLayout):
    timestamp = StringProperty("")
    mood = StringProperty("")
    text_entry = StringProperty("")
    index = NumericProperty(0)


class JournalScreen(Screen):
    def save_entry(self):
        text = self.ids["entry_input"].text.strip()
        mood = self.ids["mood_select"].text
        if not text:
            return

        entry = {
            "text": text,
            "mood": mood,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }

        data = []
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except Exception:
                    data = []

        data.append(entry)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.ids["entry_input"].text = ""
        self.ids["mood_select"].text = "gut"


class TableScreen(Screen):
    def load_data(self):
        rv = self.ids["rv"]
        rv.data = []

        if not os.path.exists(DATA_FILE):
            return

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                entries = json.load(f)
            except Exception:
                entries = []

        rv.data = [
            {
                "timestamp": e.get("timestamp", ""),
                "mood": e.get("mood", ""),
                "text_entry": e.get("text", ""),
                "index": i,
            }
            for i, e in enumerate(entries)
        ]


class BreathingScreen(Screen):
    pass


class MainLayout(BoxLayout):
    pass


class MindfulnessApp(App):
    def build(self):
        Builder.load_string(KV)
        return MainLayout()


if __name__ == "__main__":
    MindfulnessApp().run()
