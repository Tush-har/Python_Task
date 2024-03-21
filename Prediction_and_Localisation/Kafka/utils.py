import redis
import pickle
from pymongo import MongoClient

color_classes = {'red': ['tooth_damage'], 'green': ['tooth_good']}
MONGO_DB = "acym"
MONGO_COLLECTION_PARTS = "parts"
MONGO_COLLECTIONS = {MONGO_COLLECTION_PARTS: "parts"}


def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

@singleton
class CacheHelper():
    def __init__(self):
        # self.redis_cache = redis.StrictRedis(host="164.52.194.78", port="8080", db=0, socket_timeout=1)
        #self.redis_cache = redis.StrictRedis(host='13.235.133.102', port=5051, db=0, socket_timeout=1)
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




@singleton
class MongoHelper:
    client = None
    def __init__(self):
        if not self.client:
            # self.client = MongoClient(host=s.DEV_MACHINE_HOST, port=s.DEV_MACHINE_MONGO_PORT)
            self.client = MongoClient(host='localhost', port=27017)

        self.db = self.client[MONGO_DB]

    def getDatabase(self):
        return self.db

    def getCollection(self, cname, create=False, codec_options=None):
        _DB = MONGO_DB
        DB = self.client[_DB]
        if cname in MONGO_COLLECTIONS:
            if codec_options:
                return DB.get_collection(MONGO_COLLECTIONS[cname], codec_options=codec_options)
            return DB[MONGO_COLLECTIONS[cname]]
        else:
            return DB[cname]