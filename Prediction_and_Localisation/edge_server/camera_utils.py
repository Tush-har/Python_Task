import neoapi
import cv2
#ankit
class CameraHandler:
    def __init__(self, camera_id):
        self.camera_id = camera_id
        self.camera = neoapi.Cam()

    def connect(self):
        self.camera.Connect(self.camera_id)
        return self.camera.IsConnected()

    def set_features(self, settings):
        if self.connect():
            fs = neoapi.FeatureStack()
            feature_names = ["ExposureTime", "Gain", "Width", "Height", "OffsetX", "OffsetY", "Gamma"]
            for feature_name, value in zip(feature_names, settings):
                fs.Add(feature_name, value)
            self.camera.WriteFeatureStack(fs)

    def capture_image(self):
        if self.connect():
            image = self.camera.GetImage()
            if not image.IsEmpty():
                image = image.GetNPArray()
                image = cv2.cvtColor(image, cv2.COLOR_BAYER_RG2RGB)

                return image
        return None