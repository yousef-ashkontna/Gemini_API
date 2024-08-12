from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
import cv2
from kivy.graphics.texture import Texture


class HighlightedObject(BoxLayout):
    """
    Visual overlay element representing a highlighted object.
    """

    def __init__(self, bboxes, **kwargs):
        super(HighlightedObject, self).__init__(**kwargs)
        self.bboxes = bboxes

    def display_image(self, image):
        img = Image(source='', allow_stretch=True)
        for bbox in self.bboxes:
            image = cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 3)
        image = self.cv2_to_kivy_texture(image)
        img.texture = image
        return img

    def cv2_to_kivy_texture(self, opencv_image):
        flipped_image = cv2.flip(opencv_image, 0)
        # Flip the channels (BGR -> RGB for Kivy)
        rgb_image = cv2.cvtColor(flipped_image, cv2.COLOR_BGR2RGB)
        # Create a Kivy texture from the NumPy array
        height, width, channels = rgb_image.shape
        texture = Texture.create(size=(width, height))
        texture.blit_buffer(rgb_image.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
        return texture

