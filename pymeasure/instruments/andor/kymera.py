#Purpose: Driver code to command Andor Kymera camera to take images. Methods added have error codes for debugging purposes.

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import sys
import os
sys.path.append(r"C:\Users\desha\Codes\andor_dlls\AndorSDK\Python\pyAndorSpectrograph\pyAndorSpectrograph")
sys.path.append(r"C:\Users\desha\Codes\andor_dlls\AndorSDK\Python\pyAndorSDK2\pyAndorSDK2")
from spectrograph import ATSpectrograph
from atmcd_errors import Error_Codes

class KYMERA: 
    def __init__(self):
        self.camera = ATSpectrograph()  #calls atmcd class from atmcd.py
        self.camera._load_library(r"C:\Users\desha\Codes\andor_dlls\AndorSDK\Python\pyAndorSpectrograph\pyAndorSpectrograph\libs\Windows\64") #add path to dll file
        serial_number = self.camera.GetSerialNumber()
        log.info(f"Camera initialized with serial number {serial_number}")
        self.camera.Initialize(serial_number)
    
    def set_grating(self, grating):
        """Sets the grating of the camera"""
        set_grating = self.camera.SetGrating(grating)
        self.check_for_errors(set_grating)
        log.info(f"Grating set to {grating}")
    
    def get_grating(self): 
        """Returns the grating of the camera"""
        grating = self.camera.GetGrating()
        self.check_for_errors(grating)
        return grating
    
    def wavelength(self): 
        """Returns the central wavelength of the spectrometer"""
        wavelength = self.camera.GetWavelength()
        self.check_for_errors(wavelength)
        return wavelength
    
    def set_shutter(self, shutter): 
        """Sets the shutter of the spectrometer
         0 - Closed
        1 - Open"""
        error = self.camera.SetShutter(shutter)
        self.check_for_errors(error)
    
    def is_shutter_open(self): 
        """Returns the status of the shutter"""
        shutter_status = self.camera.IsShutterPresent()
        self.check_for_errors(shutter_status)
        return shutter_status
    
    def reset_slit(self): 
        """Resets the slit of the spectrometer"""
        reset = self.camera.ResetSlit()
        self.check_for_errors(reset)

    def check_for_errors(self, error_code): 
        """Checks for errors on commands"""
        if error_code != Error_Codes.DRV_SUCCESS:
            log.error(f"Error code {error_code}")
            raise Exception(f"Error code: {error_code}")