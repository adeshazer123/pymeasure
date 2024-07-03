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

import logging
import time
import queue
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK, Frame
from thorlabs_tsi_sdk.tl_camera_enums import SENSOR_TYPE
from thorlabs_tsi_sdk.tl_mono_to_color_processor import MonoToColorProcessorSDK
from PIL import Image

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class CS165MUM():
    def __init__(self, i_camera):
        self.sdk = TLCameraSDK()
        #self.close = TLCamera()
        camera_serial_number = self.sdk.discover_available_cameras()
        if camera_serial_number != 0:
            print("Camera Detected")
            log.info(camera_serial_number)
        else:
            print("No camera detected")

        self.camera = self.sdk.open_camera(camera_serial_number[i_camera])
        self.camera.frames_per_trigger_zero_for_unlimited = 0     

    def set_exposure_time_us(self, exposure_time_us):
        """Sets the exposure time in microseconds."""
        min_exposure, max_exposure = self.camera.exposure_time_range_us # fix to truncated range
        if not min_exposure <= exposure_time_us <= max_exposure:
            raise ValueError(f"Exposure time must be between {min_exposure} and {max_exposure} microseconds.")

        self.camera.exposure_time_us = exposure_time_us
        time.sleep(0.5)
        print(f"Exposure time set to {self.camera.exposure_time_us} microseconds.")
        
    def get_exposure_time_us(self):
        """Gets the exposure time in microseconds."""
        exposure_time = self.camera.exposure_time_us
        print(f"Current exposure time is {exposure_time} microseconds.")
        return exposure_time
 
            
    def initialize_camera(self):
        self.camera.arm(2)
        self.camera.issue_software_trigger()
                  

    def image_acquire(self):
        acquisition_thread = ImageAcquisitionThread(self.camera)
        acquisition_thread.run()
        print("Image acquisition finished")
        return acquisition_thread.run()


    def save_image(self, image_data, file_path):
        image_data.save(file_path, format = 'TIFF')
        print(f"Image saved to {file_path}")
    
        
    
    def dispose(self):
        self.camera.disarm()
        log.info("Camera disarmed")
        self.camera.dispose() #After called, the camera object is no longer valid and should not be used.
        logging.info("Camera disposed.")
        
    

class ImageAcquisitionThread():

    def __init__(self, camera):
        super().__init__()
        self._camera = camera
        self._previous_timestamp = 0
        self.image_data = None #added this line

        # setup color processing if necessary
        if self._camera.camera_sensor_type != SENSOR_TYPE.BAYER:
            # Sensor type is not compatible with the color processing library
            self._is_color = False
        else:
            self._mono_to_color_sdk = MonoToColorProcessorSDK()
            self._image_width = self._camera.image_width_pixels
            self._image_height = self._camera.image_height_pixels
            self._mono_to_color_processor = self._mono_to_color_sdk.create_mono_to_color_processor(
                SENSOR_TYPE.BAYER,
                self._camera.color_filter_array_phase,
                self._camera.get_color_correction_matrix(),
                self._camera.get_default_white_balance_matrix(),
                self._camera.bit_depth
            )
            self._is_color = True

        self._bit_depth = camera.bit_depth
        self._camera.image_poll_timeout_ms = 0  # Do not want to block for long periods of time

    def get_output_queue(self):
        # type: (type[None]) -> queue.Queue
        return self._image_queue

    def _get_color_image(self, frame):
        # type: (Frame) -> Image
        # verify the image size
        width = frame.image_buffer.shape[1]
        height = frame.image_buffer.shape[0]
        if (width != self._image_width) or (height != self._image_height):
            self._image_width = width
            self._image_height = height
            print("Image dimension change detected, image acquisition thread was updated")
        # color the image. transform_to_24 will scale to 8 bits per channel
        color_image_data = self._mono_to_color_processor.transform_to_24(frame.image_buffer,
                                                                         self._image_width,
                                                                         self._image_height)
        color_image_data = color_image_data.reshape(self._image_height, self._image_width, 3)
        print("color_image_data =", color_image_data)

        # return PIL Image object
        return Image.fromarray(color_image_data, mode='RGB')

    def _get_image(self, frame):
        # type: (Frame) -> Image
        # no coloring, just scale down image to 8 bpp and place into PIL Image object
        scaled_image = frame.image_buffer >> (self._bit_depth - 8)
        return Image.fromarray(scaled_image)

    def run(self):
        frame = self._camera.get_pending_frame_or_null()
        if frame is not None:
            if self._is_color:
                pil_image = self._get_color_image(frame)
                self.image_data = pil_image
                print("color image")
            else:
                pil_image = self._get_image(frame)
                print("not color image")

        self._mono_to_color_processor.dispose()
        self._mono_to_color_sdk.dispose()
        print("Disposed")  
        return self.image_data
         
    