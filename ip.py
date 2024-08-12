import cv2
import requests
from kivy.graphics import Rectangle
import numpy as np
from ultralytics import YOLO


class ImageProcessor:
    def __init__(self, model_path=None):
        # Initialize resources (error handling, Gemini API details)
        self.image_width = None
        self.image_height = None
        self.error_message = None
        self.gemini_api_url = "AIzaSyBkpBDOBpY1XYTO3UPbvUQkSx6bShPyKf8"  # Replace with actual URL
        self.cap = cv2.VideoCapture(0)
        self.model = YOLO(model_path)
        self.classes = ['person', 'bicycle', 'car', 'motorbike', 'aeroplane',
                        'bus', 'train', 'truck', 'boat', 'traffic light',
                        'fire hydrant', 'stop sign', 'parking meter',
                        'bench', 'bird', 'cat', 'dog', 'horse', 'sheep',
                        'cow', 'elephant', 'bear', 'zebra', 'giraffe',
                        'backpack', 'umbrella', 'handbag', 'tie', 'suitcase',
                        'frisbee', 'skis', 'snowboard', 'sports ball',
                        'kite', 'baseball bat', 'baseball glove',
                        'skateboard', 'surfboard', 'tennis racket',
                        'bottle', 'wine glass', 'cup', 'fork', 'knife',
                        'spoon', 'bowl', 'banana', 'apple', 'sandwich',
                        'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
                        'donut', 'cake', 'chair', 'sofa', 'pottedplant',
                        'bed', 'diningtable', 'toilet', 'tvmonitor', 'laptop',
                        'mouse', 'remote', 'keyboard', 'cell phone', 'microwave',
                        'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock',
                        'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']


    def capture_image(self):
        # Capture an image from the camera
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if ret:
            self.image_width = frame.shape[1]
            self.image_height = frame.shape[0]
            return frame

        else:
            print("Error capturing image")
            return None


    def capture_and_detect(self):
        # Capture image from webcam
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        cv2.destroyAllWindows()

        if not ret:
            print("Error capturing image")
            return None

        # Perform object detection on the captured frame
        results = self.model(frame)
        bboxes = []
        for r in results:
            if r.boxes:
                for box in r.boxes:
                    x_min, y_min, x_max, y_max = box.xyxy[0].cpu()
                    bboxes.append([int(x_min.item()), int(y_min.item()), int(x_max.item()), int(y_max.item()),
                                   self.classes[int(box.cls[0])]])
            else:
                bboxes = None

        return bboxes


