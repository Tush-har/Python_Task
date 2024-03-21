from process_manager import ProcessManager
from ultralytics import YOLO
import torch
import multiprocessing
from camera_utils import CameraHandler
from settings_manager import SettingsManager
from utils import CameraConfig
import datetime
import cv2
import json
import numpy as np
import base64
from PIL import Image
from PIL import Image, ImageDraw ,ImageFont
import io
from utils import color_classes
from PIL import Image, ImageDraw ,ImageFont
import time



def draw_bounding_boxes(main_res, image, color_classes):
    image_pil = Image.fromarray(image)
    draw = ImageDraw.Draw(image_pil)
    try:
        font = ImageFont.truetype("arial.ttf", 55)
    except IOError:
        font = ImageFont.load_default()
    # Create a reverse mapping from class name to color
    class_to_color = {cls: color for color, classes in color_classes.items() for cls in classes}
    # Iterate over the objects and draw their bounding boxes and labels
    for obj in main_res:
        box = obj['box']
        class_name = obj['name']
        # Set the color based on the class name, default to green if not specified
        color = class_to_color.get(class_name, "blue")
        draw.rectangle([box['x1'], box['y1'], box['x2'], box['y2']], outline=color, width=4)
        label = f"{class_name}"
        text_position = (box['x1'], box['y1'] - 50)
        draw.text(text_position, label, fill=color, font=font)


    image_array = np.array(image_pil)
    return  image_array




def json_serializer(v):
    return json.dumps(v).encode('utf-8')

class DefectDetectionSystem:
    def __init__(self, camera_configs, camera_settings, camera_to_model_map):

        self.camera_configs = camera_configs
        self.camera_settings = camera_settings
        self.camera_to_model_map = camera_to_model_map
        self.process_manager = ProcessManager(SettingsManager(self.camera_settings))
        self.processes = []

        self.initialize_camera_processes()


    def start_camera_processes(self):
        for process in self.processes:
            if not process.is_alive():
                process.start()
        print("All camera processes started.")


    def join_camera_processes(self):
        for process in self.processes:
            process.join()


    def initialize_camera_processes(self):
        for camera_id, camera_serial in self.camera_configs.items():
            settings = self.camera_settings.get(camera_id, [])
            model_path = self.camera_to_model_map.get(camera_id, None)
            if model_path is None:
                raise ValueError(f"No model path provided for camera {camera_id}")
        
            process = multiprocessing.Process(target=self.camera_process, args=(camera_serial, settings, model_path))
            self.processes.append(process)


    def camera_process(self, camera_serial, settings, model_path):
        camera_handler = CameraHandler(camera_serial)
        model = self.model_loader(model_path)
        while True:
            # Continuously capture and process images
            captured_image = camera_handler.capture_image()
            if captured_image is not None :
                predictions_classes, main_res = self.model_infer(model, captured_image)
                final_image =  draw_bounding_boxes(main_res,captured_image,color_classes)
                resized_image = cv2.resize(final_image,(640,640))
                cv2.imshow("Image",resized_image)
                cv2.waitKey(1)
            time.sleep(0.1)


    def model_loader(self, model_path):
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        model = YOLO(model_path,device)
        return model

    def model_infer(self, model, image_path):
        res = model(image_path) 
        if res[0]:
            # Assuming that res[0].to_json() returns a JSON string, we need to parse it to a Python dict
            predictions = json.loads(res[0].tojson())  # Convert JSON string to a dict
            predictions_classes = [r['name'] for r in predictions]
        else:
            predictions_classes = []
            predictions = {}
        return predictions_classes, predictions


# Example usage
if __name__ == "__main__":
    data_queue = multiprocessing.Queue()
    camera_config = CameraConfig()

    # You can access camera configurations like this:
    camera_configs = camera_config.camera_configs
    camera_settings = camera_config.camera_settings
    camera_to_model_map = camera_config.camera_to_model_map
    system = DefectDetectionSystem(camera_configs, camera_settings, camera_to_model_map)
    system.start_camera_processes()





