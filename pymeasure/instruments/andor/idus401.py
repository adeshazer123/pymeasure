#Purpose: Driver code to command Andor Idus camera to take images. Methods added have error codes for debugging purposes. 
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from andor_dlls.AndorSDK.Python.pyAndorSDK2.pyAndorSDK2.atmcd import atmcd
from andor_dlls.AndorSDK.Python.pyAndorSDK2.pyAndorSDK2.atmcd_errors import Error_Codes

class IDUS401(): 
    """Class to control Andor Indus Camera"""
    def __init__(self):
        self.camera = atmcd()  #calls atmcd class from atmcd.py
        self.camera._load_library(r"C:\Users\desha\Codes\andor_dlls\AndorSDK\Python\pyAndorSDK2\pyAndorSDK2\libs\Windows\64") #add path to dll file
        self.camera.SetTemperature = -100
        log.info(f" Available cameras: {self.camera.GetAvailableCameras()}")
        serial_number = self.camera.GetCameraSerialNumber()
        log.info(f"Camera initialized with serial number {serial_number}")
        self.camera.Initialize(serial_number)
    
    def set_camera(self, index):
        """Sets the current camera and initialize based on the index list"""
        self.camera.SetCurrentCamera(index)
        serial_number = self.camera.GetCameraSerialNumber(index)
        log.info(f"Camera set to {serial_number}")
        error_code = self.camera.Initialize(serial_number)
        self.check_for_errors(error_code)
        log.info("Camera initialized")
    
    def set_temperature(self, temperature): 
        """Sets the temperature of the camera in Celsius"""
        error_code = self.camera.CoolerON()
        self.check_for_errors(error_code)
        log.info("Cooler is on")

        temperature_range = self.camera.GetTemperatureRange() 
        if temperature_range[0] <= temperature <= temperature_range[1]:
            error_code = self.camera.SetTemperature(temperature)
            self.check_for_errors(error_code)
            log.info(f"Temperature set to {temperature}")

    def get_temperature(self):
        """Returns the temperature of the camera in Celsius"""
        temperature = self.camera.GetTemperature()
        self.check_for_errors(temperature)
        return temperature
    
    def set_cooler_mode(self, cooler_mode):
        """Sets cooler mode based on shutdown status.
        0 -> Returns to ambient temperature at shutdown 
        1 -> Maintains temperature at shutdown"""
        error_code = self.camera.SetCoolerMode(cooler_mode)
        self.check_for_errors(error_code)
    
    def cooler_off(self): 
        """Cooler is turned off"""
        error_code = self.camera.CoolerOFF()
        self.check_for_errors(error_code)
        log.info("Cooler is off")

    def set_exposure_time(self, exposure_time):
        """Sets the exposure time of the camera in seconds"""
        exposure_time = 0.01 #placeholder
        error_code = self.camera.SetExposureTime(exposure_time)
        self.check_for_errors(error_code)
        log.ifo(f"Exposure time set to {exposure_time}") 
    
    def set_camera(self,acquisition_mode): 
        """Sets the cameras mode. 
        1 -> Single scan
        2 -> Accumulate
        3 -> Kinetics
        4 -> Fast Kinetics
        5 -> Run till abort"""
        error_code = self.camera.SetAcquisitionMode(acquisition_mode)
        self.check_for_errors(error_code)
    
    def set_read_mode(self, read_mode):
        """Sets the read mode of the camera 
        0 -> Full Vertical Binning
        1 -> Multi-Track
        2 -> Random-Track
        3 -> Single-Track
        4 -> Image"""
        error_code = self.camera.SetReadMode(read_mode)
        self.check_for_errors(error_code)

    def set_trigger_mode(self, trigger_mode): 
        """Sets the trigger mode of the camera
        0 -> internal
        1 -> External
        6 -> External Start
        7 -> External Exposure (Bulb)
        9 -> External FVB EM (only valid for EM Newton models in FVB mode)   
        10 -> Software Trigger
        12 -> External Charge Shifting"""
        error_code = self.camera.SetTriggerMode(trigger_mode)
        self.check_for_errors(error_code)

    
    def acquistion(self): 
        """Acquires the image data in an np array"""
        data = self.camera.acquire()
        self.check_for_errors(data)
        return data
    
    def shutdown(self): 
        """Shuts down the camera"""
        error_code = self.camera.ShutDown()
        self.check_for_errors(error_code)
        log.info("Camera shutdown")

    def check_for_errors(self, error_code): 
        """Checks for errors on commands"""
        if error_code != Error_Codes.DRV_SUCCESS:
            log.error(f"Error code {error_code}")
            raise Exception(f"Error code: {error_code}")