import sys
import os
import json
import requests
from kivy.uix.floatlayout import FloatLayout
import speech_recognition as sr
import cv2
import numpy as np
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty, ObjectProperty
from plyer import tts
from pywin.framework.editor import frame
from settings import AccessibilitySettings
from ip import ImageProcessor
from object_highlight import HighlightedObject
import google.generativeai as genai
from PIL import Image as Im
from kivy.core.audio import SoundLoader
from gtts import gTTS

# Configure generative AI
gemini_api_key = "AIzaSyBkpBDOBpY1XYTO3UPbvUQkSx6bShPyKf8"
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-1.5-flash')


class SettingsPopup(Popup):
    font_size_input = ObjectProperty(None)
    text_color_input = ObjectProperty(None)
    background_color_input = ObjectProperty(None)
    verbosity_level_input = ObjectProperty(None)
    language_input = ObjectProperty(None)
    theme_input = ObjectProperty(None)
    Capture_image_details_Choice = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SettingsPopup, self).__init__(**kwargs)
        self.title = "Settings"
        self.size_hint = (0.8, 0.8)
        self.settings = App.get_running_app().accessibility_settings
        # self.font_size_input = TextInput(text=str(self.settings.font_size))
        # self.add_widget(self.font_size_input)

        # Grid layout for settings options
        grid = GridLayout(cols=2, padding=10, spacing=10)

        # Font Size
        grid.add_widget(Label(text="Font Size:"))
        self.font_size_input = TextInput(text=str(self.settings.font_size))
        grid.add_widget(self.font_size_input)

        # Text Color (assuming RGB input)
        grid.add_widget(Label(text="Text Color (R,G,B):"))
        self.text_color_input = TextInput(text=str(self.settings.text_color))
        grid.add_widget(self.text_color_input)

        # Background Color (assuming RGB input)
        grid.add_widget(Label(text="Background Color (R,G,B):"))
        self.background_color_input = TextInput(text=str(self.settings.background_color))
        grid.add_widget(self.background_color_input)

        # Verbosity Level
        grid.add_widget(Label(text="Verbosity Level:"))
        self.verbosity_level_input = TextInput(text=str(self.settings.verbosity_level))
        grid.add_widget(self.verbosity_level_input)

        # Language
        grid.add_widget(Label(text="Language:"))
        self.language_input = TextInput(text=str(self.settings.language))
        grid.add_widget(self.language_input)

        # Theme
        grid.add_widget(Label(text="Theme:"))
        self.theme_input = TextInput(text=str(self.settings.theme))
        grid.add_widget(self.theme_input)
        # capture image
        grid.add_widget(Label(text="Capture image details Choice:"))
        self.Capture_image_details_Choice = TextInput(text=str(self.settings.Capture_image_details_Choice))
        grid.add_widget(self.Capture_image_details_Choice)

        # Save button
        save_button = Button(text="Save")
        save_button.bind(on_press=self.save_settings)
        grid.add_widget(save_button)

        self.content = grid

    def save_settings(self, instance):
        try:
            self.settings.font_size = int(self.font_size_input.text)
            # Parse text color input (assuming comma-separated values)
            self.settings.text_color = self.text_color_input.text
            # Parse background color input (assuming comma-separated values)
            self.settings.background_color = self.background_color_input.text
            self.settings.verbosity_level = self.verbosity_level_input.text
            self.settings.language = self.language_input.text
            self.settings.theme = self.theme_input.text
            self.settings.Capture_image_details_Choice = self.Capture_image_details_Choice.text

            self.settings.save_settings('app_settings.json')
            self.dismiss()
        except ValueError:
            print("Invalid input. Please enter valid values.")


class MyUI(BoxLayout):
    answer_label = ObjectProperty(None)
    text_to_speak = StringProperty("")
    settings_button = Button(text="Settings")

    def __init__(self, **kwargs):
        super(MyUI, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.settings = App.get_running_app().accessibility_settings

        # Header with app title
        header = BoxLayout(size_hint_y=0.1, padding=10)
        app_title = Label(text="Object Detection App", font_size=20)
        header.add_widget(app_title)
        self.add_widget(header)

        # Main content area
        self.content = BoxLayout(orientation="horizontal", size_hint_y=5)
        self.add_widget(self.content)

        # Answer label
        self.answer_label = Label()
        self.add_widget(self.answer_label)

        # Footer with buttons for actions

        footer = BoxLayout(orientation='vertical', size_hint_x=0.2, padding=10)
        background_image = Image(
            source='images/WhatsApp Image 2024-07-26 at 22.00.52_2cdcc8e2.jpg',
            allow_stretch=True, keep_ratio=False)
        float_layout = FloatLayout()

        settings_button = Button(size_hint=(None, None), size=(50, 50),
                                 background_normal='images/Settings.png',
                                 background_down='images/Settings.png')
        settings_button.bind(on_press=self.open_settings_popup)
        footer.add_widget(settings_button)

        capture_button = Button(size_hint=(None, None), size=(50, 50),
                                background_normal='images/Screenshot1.png',
                                background_down='images/Screenshot1.png')
        capture_button.bind(on_press=self.capture_and_ask)
        footer.add_widget(capture_button)
        self.add_widget(footer)

        self.voice_resume_button = Button(size_hint=(None, None), size=(50, 50),
                                          background_normal='images/Resume Button.png',
                                          background_down='images/Resume Button.png')
        self.voice_resume_button.bind(on_press=self.resume_voice)

        self.voice_stop_button = Button(size_hint=(None, None), size=(50, 50),
                                        background_normal='images/Mute Unmute.png',
                                        background_down='images/Mute Unmute.png')
        self.voice_stop_button.bind(on_press=self.stop_voice)

        self.voice_pause_button = Button(size_hint=(None, None), size=(50, 50),
                                         background_normal='images/Pause Button.png',
                                         background_down='images/Pause Button.png')
        self.voice_pause_button.bind(on_press=self.pause_voice)

        self.voice_replay_button = Button(size_hint=(None, None), size=(50, 50),
                                          background_normal='images/Replay.png',
                                          background_down='images/Replay.png')
        self.voice_replay_button.bind(on_press=self.replay_voice)

        self.buttons_layout = BoxLayout(orientation='horizontal')
        self.add_widget(self.buttons_layout)
        # Speak command button

        self.voice_command_button = Button(size_hint=(None, None), size=(50, 50),
                                           background_normal='images/Radio Studio.png',
                                           background_down='images/Radio Studio.png')
        self.voice_command_button.bind(on_press=self.listen_for_command)
        self.buttons_layout.add_widget(self.voice_command_button)

        # self.voice_command_button = Button(text="Speak Command")
        # self.voice_command_button.bind(on_press=self.listen_for_command)
        # self.buttons_layout.add_widget(self.voice_command_button)

        # Initializing the ImageProcessor
        self.model_path = "yolov9t.pt"
        self.image_processor = ImageProcessor(self.model_path)
        self.gemini_model = Gemini_Detection()
        self.icon_keywords = {
            "start detection": "capture_and_ask",
            "open settings": "open_settings_popup"
        }

    def open_settings_popup(self, instance = None):
        popup = SettingsPopup()
        popup.open()


    def listen_for_command(self, instance):
        recognizer = sr.Recognizer()
        with sr.Microphone(device_index=0) as source:
            self.TTS("Listening",'en')
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)
        try:

            command = recognizer.recognize_google(audio)
            self.process_voice_command(command)
        except sr.UnknownValueError:
            self.TTS("Could not understand audio", 'en')
        except sr.RequestError as e:
            self.TTS(f"Could not request results from Google Speech Recognition service; {e}", 'en')

    def process_voice_command(self, command):
        action = self.recognize_and_trigger_action(command, self.icon_keywords)
        if action:
            getattr(self, action)()
        else:
            response = self.gemini_model.question(command)
            try:
                os.remove('output.mp3')  # Remove the music file if it exists
            except FileNotFoundError:
                pass  # Ignore if the file doesn't exist
            self.buttons_layout.remove_widget(self.voice_command_button)
            self.buttons_layout.add_widget(self.voice_stop_button)
            self.buttons_layout.add_widget(self.voice_pause_button)
            self.TTS(response, self.settings.language)

    def recognize_and_trigger_action(self, command, icon_keywords):
        command = command.lower()
        for keyword, action in icon_keywords.items():
            if keyword in command:
                return action

    def TTS(self, text, language):
        speech = gTTS(text=text, lang=language)
        speech.save('output.mp3')
        self.sound = SoundLoader.load('output.mp3')
        self.sound.play()

    def pause_voice(self, instance):
        self.posetion = self.sound.get_pos()
        self.sound.stop()
        self.buttons_layout.remove_widget(self.voice_pause_button)
        self.buttons_layout.add_widget(self.voice_resume_button)
        self.buttons_layout.add_widget(self.voice_replay_button)

    def stop_voice(self, instance):
        self.sound.stop()
        self.buttons_layout.clear_widgets()
        self.buttons_layout.add_widget(self.voice_command_button)

    def replay_voice(self, instance):
        self.sound.play()
        self.sound.seek(0)
        self.buttons_layout.remove_widget(self.voice_replay_button)
        self.buttons_layout.remove_widget(self.voice_resume_button)
        self.buttons_layout.add_widget(self.voice_pause_button)

    def resume_voice(self, instance):
        self.sound.seek(self.posetion)
        self.sound.play()
        self.buttons_layout.remove_widget(self.voice_replay_button)
        self.buttons_layout.remove_widget(self.voice_resume_button)
        self.buttons_layout.add_widget(self.voice_pause_button)


    def capture_and_ask(self, instance= None):
        self.content.clear_widgets()
        # Capture image and detect object
        detected_objects = self.image_processor.capture_and_detect()
        if not detected_objects:
            self.TTS("No object detected", 'en')
        else:
            self.update_object_highlight(detected_objects)
            if self.settings.Capture_image_details_Choice == "capture_and_detect":

                labels = []
                for obj in detected_objects:
                    label = obj[4]
                    labels.append(label)
                self.questionanswerer = QuestionAnswerer(labels)
                self.TTS(self.questionanswerer.answer_question(), 'en')
            else:
                self.TTS(self.gemini_out, 'en')
            self.buttons_layout.remove_widget(self.voice_command_button)
            self.buttons_layout.add_widget(self.voice_stop_button)
            self.buttons_layout.add_widget(self.voice_pause_button)
    
    
    
    def update_object_highlight(self, obj_data):
        image = self.image_processor.capture_image()
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_gemini = Im.fromarray(rgb_image)
        self.highlight_element = HighlightedObject(obj_data)
        self.gemini_out = self.gemini_model.question(image_gemini)
        img = self.highlight_element.display_image(image)
        self.content.add_widget(img)


class Gemini_Detection:
    def __init__(self):
        self.chat = model.start_chat(history=[])

    def question(self, message):
        response = self.chat.send_message(message)
        return response.text


class QuestionAnswerer:
    def __init__(self, detected_objects):
        self.objects = detected_objects

    def answer_question(self):
        answer = "I see the following objects: "
        for object_name in self.objects:
            answer += f" {object_name}"
        return answer


class MyApp(App):
    def build(self):
        self.accessibility_settings = AccessibilitySettings()
        return MyUI()


if __name__ == "__main__":
    MyApp().run()
