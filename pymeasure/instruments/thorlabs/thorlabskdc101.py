# Author: Amelie Deshazer 
# Date: 2024-07-03
# Purpose: The script will move the z direction of the stage

import logging 

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import clr 

clr.AddReference(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.DeviceManagerCLI")
clr.AddReference(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference(r"C:\Program Files\Thorlabs\Kinesis\ThorLabs.MotionControl.KCube.DCServoCLI.dll")

from Thorlabs.MotionControl.DeviceManagerCLI import * 
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.KCube.DCServoCLI import *
from System import Decimal
import time

print("reading the class...")

class KDC101():
    def __init__(self):
        DeviceManagerCLI.BuildDeviceList()
        serial_number = '' #must add serial number
        self.device = KCubePiezo.CreateKCubeDCServo(serial_number)

        self.device.Connect(serial_number)
        time.sleep(0.25)

        self.device.StartPolling(250)
        time.sleep(0.25)
        log.info("Device polling started")
        print("Device polling started") #for debugging purposes

        self.device.EnableDevice()
        time.sleep(0.25)
        log.info("Device enabled")
        print("Device enabled") #for debugging purposes 
        
        info_device = self.device.GetDeviceInfo()
        print(info_device.Description)
    
    def load_config(self):
        config = self.device.LoadMotorConfiguration(self.serial_number, DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)

        config.DeviceSettingsName = "825B" #update stage name
        log.info("Device settings loaded") 
        config.UpdateCurrentConfiguration()
        self.device.SetSettings(self.device.MotorDeviceSettings, True, False)

        
    def move_home(self):

        home = self.device.SetZero() 
        log.info("Device moved to home position")
        print("Device moved to home position") #for debugging purposes
        return home
    
    def move_relative(self, distance): 
        self.device.MoveTo(Decimal(distance))
        log.info(f"Device moved to {distance} mm")
        print(f"Device moved to {distance} mm") #for debugging purposes 
        time.sleep(1)

    def get_position(self): 
        self.device.GetPosition()
        log.info(f"Device is at {self.device.Position} mm")
    
    def disconnect(self): 
        self.device.StopPolling()
        self.device.Disconnet()
        log.info("Device has been disconnected")
        print("Device has been disconnected") #for debugging purposes