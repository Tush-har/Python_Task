# utils.py
import redis
import pickle

color_classes = {'red': ['box'], 'green': ['bottle']}
class CameraConfig:
    def __init__(self):
        self.camera_configs = {
            "cam1": "700005204641",
            
        }

        self.camera_settings = {
            "cam1": [384616,1.00,1080,1080,0,0,0.80]
        }

        self.camera_to_model_map = {
            "cam1": "./yolov8n.pt"
        }

        self.defect_accept_map = {
            "cam1": {"reject": ['box'], "accept": ['bottle']}
        }

    def get_camera_id(self, camera_name):
        return self.camera_configs.get(camera_name)

    def get_camera_settings(self, camera_name):
        return self.camera_settings.get(camera_name)

    def get_model_path(self, camera_name):
        return self.camera_to_model_map.get(camera_name)

    def update_defect_accept(self, camera_name, defect_list, accept_list):
        if camera_name in self.defect_accept_map:
            self.defect_accept_map[camera_name]["reject"].extend(defect_list)
            self.defect_accept_map[camera_name]["accept"].extend(accept_list)
        else:
            raise ValueError(f"Camera {camera_name} not found in defect/accept map.")

    def get_defect_accept(self, camera_name):
        return self.defect_accept_map.get(camera_name)
    










def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance
 
# @singleton
# class CacheHelper():
    def __init__(self):
        # self.redis_cache = redis.StrictRedis(host="164.52.194.78", port="8080", db=0, socket_timeout=1)
        # self.redis_cache = redis.StrictRedis(host='192.168.10.56', port=6379, db=0, socket_timeout=1)
        self.redis_cache = redis.StrictRedis(host='localhost', port=6379, db=0, socket_timeout=1)
        #s.REDIS_CLIENT_HOST
        print("REDIS CACHE UP!")
 
    def get_redis_pipeline(self):
        return self.redis_cache.pipeline()
   
    def set_json(self, dict_obj):
        try:
            k, v = list(dict_obj.items())[0]
            v = pickle.dumps(v)
            return self.redis_cache.set(k, v)
        except redis.ConnectionError:
            return None
 
    def get_json(self, key):
        try:
            temp = self.redis_cache.get(key)
            #print(temp)\
            if temp:
                temp= pickle.loads(temp)
            return temp
        except redis.ConnectionError:
            return None
        return None
 
    def execute_pipe_commands(self, commands):
        #TBD to increase efficiency can chain commands for getting cache in one go
        return None