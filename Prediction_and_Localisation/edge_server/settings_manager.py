# A simple settings manager, could be expanded to read settings from a file
class SettingsManager:
    def __init__(self, settings):
        self.settings = settings

    def get_camera_settings(self, camera_name):
        return self.settings.get(camera_name, [])
