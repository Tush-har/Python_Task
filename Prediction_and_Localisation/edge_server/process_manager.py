from multiprocessing import Process
from camera_utils import CameraHandler
from settings_manager import SettingsManager




class ProcessManager:
    def __init__(self, camera_settings):
        self.camera_settings = camera_settings

    def create_processes(self, camera_ids):
        processes = []
        for camera_id in camera_ids:
            camera_handler = CameraHandler(camera_id)
            camera_settings = self.camera_settings.get_camera_settings(camera_id)
            camera_handler.set_features(camera_settings)
            p = Process(target=camera_handler.capture_image)
            processes.append(p)
        return processes

    def start_all(self, processes):
        for p in processes:
            p.start()

    def join_all(self, processes):
        for p in processes:
            p.join()