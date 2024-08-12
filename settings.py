from kivy.uix.button import Button
import json
from kivy.uix.textinput import TextInput

default_settings = {
    "font_size": 14,
    "text_color": [0, 0, 0],
    "background_color": [255, 255, 255],
    "theme": "light",
    "sound_volume": 0.8,
    "language": "en"
}

settings_filename = "app_settings.json"
with open(settings_filename, "w") as json_file:
    json.dump(default_settings, json_file, indent=4)

class AccessibilitySettings:
    def __init__(self):
        self.font_size = 17
        self.text_color = (0, 0, 0, 0)  # Black
        self.background_color = (255, 255, 255, 255)  # White
        self.verbosity_level = "basic"  # Options: "basic", "detailed"
        self.tts_voice = None  # Stores the chosen TTS voice object (implementation specific)
        self.tts_playback_speed = 1.0  # Normal speed
        self.language = "en"
        self.theme = "light"
        self.Capture_image_details_Choice="Gemini_detections"
    def load_settings(self, filename):
        try:
            with open(filename, 'r') as file:
                settings_data = json.load(file)
                self.font_size = settings_data.get('font_size', self.font_size)
                self.text_color = tuple(settings_data.get('text_color', self.text_color))
                self.background_color = tuple(settings_data.get('background_color', self.background_color))
                self.verbosity_level = settings_data.get('verbosity_level', self.verbosity_level)
                self.language = settings_data.get('language', self.language)
                self.theme = settings_data.get('theme', self.theme)
                self.Capture_image_details_Choice = settings_data.get('Capture image details Choice', self.Capture_image_details_Choice)
                print(f"Loaded settings from {filename}")
        except FileNotFoundError:
            print(f"Settings file '{filename}' not found. Using default settings.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON file '{filename}': {e}")

    def save_settings(self, filename):
        settings_data = {
            'font_size': self.font_size,
            'text_color': list(self.text_color),
            'background_color': list(self.background_color),
            'verbosity_level': self.verbosity_level,
            'language': self.language,
            'theme': self.theme,
            'Capture image details Choice':self.Capture_image_details_Choice,
        }
        try:
            with open(filename, 'w') as file:
                json.dump(settings_data, file, indent=4)
            print(f"Settings saved to {filename}")
        except IOError as e:
            print(f"Error saving settings to {filename}: {e}")

    def update_ui(self, ui_element):
        # Example usage for UI updates (replace with your actual UI class)
        ui_element.font_size = self.font_size
        ui_element.color = self.text_color


ui_element = Button(text="Click me")
ui_element = TextInput(text="Enter text here")
settings = AccessibilitySettings()
settings.font_size = 20
settings.text_color = (0.2, 0.4, 0.6, 1)
settings.update_ui(ui_element)
settings.save_settings('app_settings.json')
settings.load_settings('app_settings.json')
