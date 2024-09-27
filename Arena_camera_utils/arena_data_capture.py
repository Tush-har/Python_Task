from arena_api.system import system
from arena_api.buffer import *

import time
from datetime import datetime
from arena_api import enums as _enums
from arena_api.enums import PixelFormat
from arena_api.__future__.save import Writer
from arena_api.system import system
from arena_api.buffer import BufferFactory
from arena_api._device import Device



import ctypes
import numpy as np
import cv2
import time

import cv2 as cv
import sys
import logging
import os


TAB1 = "  "
TAB2 = "    "

logger = logging.getLogger("my_logger")
logging.basicConfig(filename="capture.log",filemode="w")
logger.setLevel(logging.DEBUG)


folder_path = './data_'+str(datetime.now().strftime('%H_%M_%S'))

if not os.path.exists(folder_path):
    os.makedirs(folder_path)


class LucidConnection:
    
    def __init__(self):
        self.device_infos = None
        self.selected_index = None
        self.device = None
        
   
    def get(self,device_id):
        self.serial_number = device_id
        self.camera_found = False
        self.device_infos = None
        self.selected_index = None

        self.device_infos = system.device_infos
        for i in range(len(self.device_infos)):
            if self.serial_number == self.device_infos[i]['serial']:
                self.selected_index = i
                self.camera_found = True
                break

        if self.camera_found == True:
            selected_model = self.device_infos[self.selected_index]['model']
            print(f"Create device: {selected_model}...")
            self.device = system.create_device(device_infos=self.device_infos[self.selected_index])[0]
            print("Press S to capture current_frame!")
            print("Press q to exit!")

            logger.info(f"Connected device  : {self.serial_number}")
            
        else:
            logger.exception(f"Device id {self.serial_number} cannot be found")
    
        return self.device
    


class display:

    def __init__(self,cam):
        self.cam = cam
    # to display
    def setup(self,device):

        self.nodemap = device.nodemap
        self.nodes = self.nodemap.get_node(['Width', 'Height', 'PixelFormat','ExposureAuto', 'ExposureTime'])

        self.nodes['Width'].value = 1000
        self.nodes['Height'].value = 720
        self.nodes['PixelFormat'].value = 'RGB8'

        self.num_channels = 3

        # Stream nodemap
        tl_stream_nodemap = device.tl_stream_nodemap

        tl_stream_nodemap["StreamBufferHandlingMode"].value = "NewestOnly"
        tl_stream_nodemap['StreamAutoNegotiatePacketSize'].value = True
        tl_stream_nodemap['StreamPacketResendEnable'].value = True

        return self.num_channels

    def infer(self):
      
        num_channels = self.setup(self.cam)

        with self.cam.start_stream():
            while True:
               
                buffer = self.cam.get_buffer()
              
                item = BufferFactory.copy(buffer)
                self.cam.requeue_buffer(buffer)

                buffer_bytes_per_pixel = int(len(item.data)/(item.width * item.height))
              
                array = (ctypes.c_ubyte * num_channels * item.width * item.height).from_address(ctypes.addressof(item.pbytes))
               
                npndarray = np.ndarray(buffer=array, dtype=np.uint8, shape=(item.height, item.width, buffer_bytes_per_pixel))

                cv2.imshow('Lucid', npndarray)
               
                save_key = 's'
                quit_window = 'q'
                
                # save frames
                key = cv2.waitKey(1) & 0xFF
                if key == ord(save_key):
                    
                    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]  # Up to milliseconds
                    file_name = f"{current_time}.png"
                
                    file_path = os.path.join(folder_path, file_name)
                    cv2.imwrite(file_path, npndarray, [cv2.IMWRITE_PNG_COMPRESSION, 0]) # 0 compression
                    print(f"Image saved to {file_path}")
                    logger.debug(f"Image saved to {file_path}")
                
                # quit
                if key == ord(quit_window):
                    BufferFactory.destroy(item)
                    self.cam.stop_stream()
                    cv2.destroyAllWindows()
                    logger.debug("Quit key pressed")
                
                BufferFactory.destroy(item)

                key = cv2.waitKey(1)
                if key == 27:
                    break
                
            self.cam.stop_stream()
            cv2.destroyAllWindows()
            
        system.destroy_device()
        
        print(f'{TAB1}Destroyed all created devices')






print("Enter camera id! ")
id = input()

cam2 = LucidConnection().get(id)
d1 = display(cam2).infer()



