import os
import requests
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from settings import AccessibilitySettings
from ui import MyUI
from ip import ImageProcessor
import google.generativeai as genai

# Configure generative AI
gemini_api_key = "AIzaSyBkpBDOBpY1XYTO3UPbvUQkSx6bShPyKf8"
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-1.5-flash')


class MainApp(App):
    accessibility_settings = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)
        self.model_path = "yolov9t.pt"
        self.ip = ImageProcessor(self.model_path)
        self.accessibility_settings = AccessibilitySettings()

    def build(self):
        self.ui = MyUI()
        self.ui.settings = self.accessibility_settings
        return self.ui


if __name__ == "__main__":
    MainApp().run()
