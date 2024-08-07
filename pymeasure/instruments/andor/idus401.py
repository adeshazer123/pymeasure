#Purpose:Driver code to command Andor Idus camera to take images 

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from andor_dlls.AndorSDK.Python.pyAndorSDK2 import atmcd

class IDUS401(): 
    """Class to control Andor Indus Camera"""
    def __init__(self):
        self.camera = atmcd()  #calls atmcd class from atmcd.py
        self.camera._load_library(r"C:\Users\desha\Codes\andor_dlls\AndorSDK\Python\pyAndorSDK2\pyAndorSDK2\libs\Windows\64") #add path to dll file
        serial_number = self.camera.GetCameraSerialNumber() #must add serial number
        log.info(f"Camera initialized with serial number {serial_number}")
        self.camera.Initialize(serial_number)

    def set_exposure_time(self, exposure_time):
        exposure_time = 0.01 #placeholder
        self.camera.SetExposureTime(exposure_time)
        log.info(f"Exposure time set to {exposure_time}") 
        print(f"Exposure time set to {exposure_time}") #for debugging purposes
    
    def set_camera(self,acquisition_mode, read_mode, trigger_mode): 
        self.camera.SetAcquisitionMode(acquisition_mode) #1 = single scan mode
        self.camera.SetReadMode(read_mode) #4 = reads out Image data
        self.camera.SetTriggerMode(trigger_mode) #1 = External. See amcd class for more information

    def acquistion(self): 
        data = self.camera.acquire()
        return data #returns an np array of the image data
    
    def shutdown(self): 
        self.camera.ShutDown()
        log.info("Camera shutdown")