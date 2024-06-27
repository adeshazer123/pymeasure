# Author: Amelie Deshazer 
# Data: 6/18/24 
# Purpose: Communicate with the ThorLabs CS165MU/M color camera. Three classes are defined in this script to control image acquisition, image processing, and camera paramters. 
# Saves image as a tif file in a specified directory. 


try:
    # if on Windows, use the provided setup script to add the DLLs folder to the PATH
    from windows_setup import configure_path
    configure_path()
except ImportError:
    configure_path = None


import os
import queue
import logging
from ctypes import c_longlong

from exceptiongroup import format_exception
from pymeasure.instruments import Instrument
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK, TLCameraError, _create_c_failure_message
from thorlabs_tsi_sdk.tl_camera_enums import SENSOR_TYPE
from thorlabs_tsi_sdk.tl_mono_to_color_processor import MonoToColorProcessorSDK
from PIL import Image
import numpy as np 
# import tkinter as tk
_logger = logging.getLogger('thorlabs_tsi_sdk.tl_camera')

class CS165MUM():

    def __init__(self, camera_connection = None):
        self.camera = camera_connection
        print("Camera connected")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_type is not None:
            _logger.debug("".join(format_exception(exception_type, exception_value, exception_traceback)))
        self.dispose()
        return True if exception_type is None else False

    def set_parameters(self):
        with Image_Parameters(self.name) as image_processes:
            image_processes.get_exposure_time_us()
            image_processes.set_exposure_time_us()
            print("Parameters set")
    def save_image(self): 
        with Image_Parameters() as image_save:
            image_save.save_image(image_acquisition.last_image, "saved_image.tif")
        print("Image saved")

class Image_Parameters():
    def __init__(self, camera):
        self._camera = camera 
        @property
        def get_exposure_time_us(self): 
            try: 
                exposure_time_us = c_longlong()
                exposure = self._camera.get_exposure_time_us(self._camera, exposure_time_us)
                if exposure != 0:
                    print("Exposure time set to {exposure_time_us} microseconds".format(exposure_time_us=exposure_time_us.value))
                    return int(exposure_time_us.value)
            except Exception as error:
                print("Error: {error}".format(error=error))
                raise error
            
        @get_exposure_time_us.setter
        def set_exposure_time_us(self, exposure_time_us):
            try: 
                value = c_longlong(exposure_time_us)
                exposure_time_us = self._camera.set_exposure_time_us(self,value)
                if exposure_time_us != 0:
                    print("Exposure time set to {exposure_time_us} microseconds".format(exposure_time_us=exposure_time_us))
            except Exception as error:
                print("Could not set exposure time" + str(error))
    
    
        def save_image(image_data, file_path):
            if isinstance(image_data, np.ndarray):
                Image.fromarray(image_data)
                print("Convert into PIL image")
            else: 
                image = image_data
                print("Image is already a PIL image")
            image.save(file_path, format = 'TIF')
            print(f"Image saved to {file_path}")

# class ImageAcquisitionThread():

#     def __init__(self, camera):
#         # type: (TLCamera) -> ImageAcquisitionThread
#         super(ImageAcquisitionThread, self).__init__()
#         self._camera = camera
#         self._previous_timestamp = 0 
        
#         #Checks if whether can incorporate color processing
#         if self._camera.camera_get_sensor != SENSOR_TYPE.BAYER:
#             # Cannot support color
#             self._camera = False
#         else:
#             self._mono_to_color_sdk = MonoToColorProcessorSDK()
#             self._image_width = self._camera.image_width_pixels
#             self._image_height = self._camera.image_height_pixels
#             self._mono_to_color_processor = self._mono_to_color_sdk.create_mono_to_color_processor(
#                 SENSOR_TYPE.BAYER,
#                 self._camera.color_filter_array_phase,
#                 self._camera.get_color_correction_matrix(),
#                 self._camera.get_default_white_balance_matrix(),
#                 self._camera.bit_depth
#             )
#             self._is_color = True
            
#         self._bit_depth = camera.bit_depth
#         self._camera.image_poll_timeout_ms = 0  # Do not want to block for long periods of time
#         # self._camera.exposure_time_us = 1000 # initializes the exposure time in seconds
#         # self._image_queue = queue.Queue(maxsize=2)

#     def get_output_queue(self): 
#         return self._image_queue

#     def _get_color_image(self, frame):
#         # type: (Frame) -> Image
#         # verify the image size
#         width = frame.image_buffer.shape[1]
#         height = frame.image_buffer.shape[0]
#         if (width != self._image_width) or (height != self._image_height):
#             self._image_width = width
#             self._image_height = height
#             print("Image dimension change detected, image acquisition thread was updated")
#         # color the image. transform_to_48 will scale to 16 bits per channel
#         color_image_data = self._mono_to_color_processor.transform_to_48(frame.image_buffer,
#                                                                          self._image_width,
#                                                                          self._image_height)
#         color_image_data = color_image_data.reshape(self._image_height, self._image_width, 3)
#         print("color_image_data =", color_image_data)
#         # return PIL Image object
#         return Image.fromarray(color_image_data, mode='RGB')

#     def _get_image(self, frame):
#         # type: (Frame) -> Image
#         # no coloring, just scale down image to 8 bpp and place into PIL Image object
#         scaled_image = frame.image_buffer >> (self._bit_depth - 8)
#         return Image.fromarray(scaled_image)
    

#     def run(self):
#         while not self._stop_event.is_set():
#             try:
#                 frame = self._camera.get_pending_frame_or_null()
#                 if frame is not None:
#                     if self._is_color:
#                         pil_image = self._get_color_image(frame)
#                     else:
#                         pil_image = self._get_image(frame)
#                     self._image_queue.put_nowait(pil_image)
#             except queue.Full:
#                 # No point in keeping this image around when the queue is full, let's skip to the next one
#                 pass
#             except Exception as error:
#                 print("Encountered error: {error}, image acquisition will stop.".format(error=error))
#                 break
#         print("Image acquisition has stopped")
#         if self._is_color:
#             self._mono_to_color_processor.dispose()
#             self._mono_to_color_sdk.dispose()


#     def dispose(self):
#         # type: (type(None)) -> None
#         """
#         Cleans up the TLCameraSDK instance - make sure to call this when you are done with the TLCameraSDK instance.
#         If using the *with* statement, dispose is called automatically upon exit.

#         """
#         try:
#             if self._disposed:
#                 return
#             error_code = self._sdk.tl_camera_close_sdk()
#             if error_code != 0:
#                 raise TLCameraError(_create_c_failure_message(self._sdk, "tl_camera_close_sdk", error_code))
#             TLCameraSDK._is_sdk_open = False
#             self._disposed = True
#             self._current_camera_connect_callback = None
#             self._current_camera_disconnect_callback = None
#         except Exception as exception:
#             print("Camera SDK destruction failed; " + str(exception))
#             raise exception


if "__main__" == __name__:
    with TLCameraSDK() as sdk:
        camera_list = sdk.discover_available_cameras() 
        if camera_list != 0: 
            print("Camera detected")
        else: 
            print("No camera detected")
    
        with sdk.open_camera(camera_list[0]) as camera_connection:
            camera_connection.frames_per_trigger_zero_for_unlimited = 0  # start camera in continuous mode
            camera_connection.arm(2)
            camera_connection.issue_software_trigger()

        with CS165MUM(camera_connection) as set_exposure: 
            print(set_exposure.name)
            exposure = set_exposure.set_parameters()
            camera_connection.issue_software_trigger()

        # with ImageAcquisitionThread(camera_connection) as image_acquisition: 
        #     print("Image acquisition started")
        #     print("Image acquisition finished")

        # with Image_Parameters(camera_connection) as image_save:
        #     image_save.save_image(image_acquisition.last_image, "saved_image.tif")
        
        camera_connection.disarm() 
        print("Camera disarmed")


# class CS165MUM():
#     # def __init__(self):
#     #     with TLCameraSDK() as sdk:
#     #         camera_list = sdk.discover_available_cameras() 
#     #         if camera_list != 0: 
#     #             print("Camera detected")
#     #         else: 
#     #             print("No camera detected")
#     #def number_of_cameras(self):
#         #     return len(camera_list)
        
#         # def open_camera(self): 
#         #     camera = self.open_camera(camera_list[i_name])
#         #     print("camera printed")
#         #     return camera 
        
#         # def set_up_parameters(self):
#         #     with Image_Parameters(self.camera) as image_processing:
#         #         print("Setting up parameters")
#         #         image_processing.get_exposure_time_us()
#         #         image_processing.set_exposure_time_us()
#         #         print("Parameters set")

#         # def initialize_camera(self, camera):
#         #     self.open_camera(camera)
#         #     camera.frames_per_trigger_zero_for_unlimited = 0
#         #     camera.arm(2)
#         #     camera.issue_software_trigger()
        
#         # def image_acquire(self):
#         #     with ImageAcquisitionThread(self.camera) as image_acquisition:
#         #         print("Starting image acquisition")
#         #         print("Image acquisition finished")
            
#         #     with Image_Parameters() as image_save:
#         #         image_save.save_image(image_acquisition.last_image, "saved_image.tif")
        
        
#         self.camera.disarm()
#         print("Camera disarmed")



            
#  # print("Camera {i} opened".format(i=i))

#             # Open all detected cameras
#         # for i in range(len(camera_list)):        







# class Initiate_Camera(): 
#     def discover_cameras(self):
#         with TLCameraSDK() as sdk: 
#             camera_avilable = sdk.discover_available_cameras()

#             if camera_avilable:
#                 print("Camera detected")
#             else: 
#                 print("No camera detected") 
            
#     #Lines 35-58 define get and set exposure times before image acquisition. 
#     @property
#     def exposure_time_us(self): 
#         try:
#             with TLCamera() as sdk: 
#                 exposure_time_us = c_longlong()
#                 exposure_time_us = sdk._camera.get_exposure_time_us(self._camera, exposure_time_us)
#                 if exposure_time_us != 0:
#                     print("Exposure time set to {exposure_time_us} microseconds".format(exposure_time_us=exposure_time_us.value))
#                     return int(exposure_time_us.value) 
                 
#         except Exception as error: 
#             print("Error: {error}".format(error=error))
#             raise error
        
#     @exposure_time_us.setter
#     def exposure_time_us(self, exposure_time_us): 
#         try: 
#             with TLCamera() as sdk:
#                 value = c_longlong(exposure_time_us)
#                 exposure_time_us = sdk._camera.set_exposure_time_us(self, value) 
#             if exposure_time_us != 0: 
#                 print("Exposure time set to {exposure_time_us} microseconds".format(exposure_time_us=exposure_time_us))
#         except Exception as error: 
#             print("Could not set exposure time" + str(error))

#     def software_trigger(self): 
#         try:
#             with TLCamera() as sdk:
#                 value = sdk._camera.software_trigger()
#                 if value != 0:
#                     print("Camera triggered")

#         except Exception as error:
#             print("Could not trigger camera" + str(error))

# Set up direcrory path for the camera 


# class LiveViewCanvas(tk.Canvas):

#     def __init__(self, parent, image_queue):
#         # type: (typing.Any, queue.Queue) -> LiveViewCanvas
#         self.image_queue = image_queue
#         self._image_width = 0
#         self._image_height = 0
#         tk.Canvas.__init__(self, parent)
#         self.pack()
#         self._get_image()

#     def _get_image(self):
#         try:
#             image = self.image_queue.get_nowait()
#             self._image = ImageTk.PhotoImage(master=self, image=image)
#             if (self._image.width() != self._image_width) or (self._image.height() != self._image_height):
#                 # resize the canvas to match the new image size
#                 self._image_width = self._image.width()
#                 self._image_height = self._image.height()
#                 self.config(width=self._image_width, height=self._image_height)
#             self.create_image(0, 0, image=self._image, anchor='nw')
#         except queue.Empty:
#             pass
#         self.after(10, self._get_image)


    
    # def save_image(self, image): 
    #     image.save(os.path.join(OUTPUT_DIRECTORY, FILE_NAME))
    #     print("Image saved")
        

    

                


        

    # class CS165MU():
    #    def __init__(self, parent, image_queue, image_acquisition_thread,):
    #     # type: (typing.Any, queue.Queue, ImageAcquisitionThread) -> None
    #     self.image_queue = image_queue
    #     self.image_acquisition_thread = image_acquisition_thread
    #     self._image_width = 0
    #     self._image_height = 0
    #     # Instrument.__init__(self, parent)
    #     self.pack()
    #     self._get_image()





        # Add code method for setting exposure time 
        # Do we need code for 


    