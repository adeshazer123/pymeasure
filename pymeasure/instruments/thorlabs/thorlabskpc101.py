# Author: Amelie Deshazer 
# Date: 2024-07-03
# Purpose: This script will control the piezoelectric stage to move the reference arm. 

import logging 

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import clr 

clr.AddReference(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.DeviceManagerCLI")
clr.AddReference(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.GenericPiezoCLI.dll")
clr.AddReference(r"C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.KCube.PiezoCLI.dll")

from Thorlabs.MotionControl.DeviceManagerCLI import * 
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.GenericPiezoCLI import *
from Thorlabs.MotionControl.KCube.PiezoCLI import *
from System import Decimal
import time

print("reading the class...")
class KPZ101():
    def __init__(self):
        DeviceManagerCLI.BuildDeviceList()
        serial_number = '' #must add serial number
        self.device = KCubePiezo.CreateKCubePiezo(serial_number)

        self.device.Connect(serial_number)

        info_device = self.device.GetDeviceInfo()
        print(info_device.Description)


        self.device.StartPolling(250)
        time.sleep(0.25)
        log.info("Device polling started")
        print("Device polling started") #for debugging purposes

        self.device.EnableDevice()
        time.sleep(0.25)
        log.info("Device enabled")
        print("Device enabled") #for debugging purposes 

        device_config = self.device.GetPiezoConfiguration()
        print("Device configuration is %s" % device_config) #for debugging purposes
        log.print("Device configuration is %s" % device_config)

        device_settings = self.device.PiezoDeviceSettings()
        
    def move_home(self):
        self.device.SetZero() 
        log.info("Device moved to home position")
        print("Device moved to home position") #for debugging purposes
    
    def max_voltage(self): 
        max_voltage = self.device.GetVoltageOutputMax()
        return max_voltage
    
    def set_voltage(self,voltage):
        #self.device.SetVoltageOutput(voltage)
        # checks bounds of voltage parameter
        if voltage != Decimal(0) & voltage <= self.max_voltage():
            self.device.SetVoltageOutput(voltage)
            time.sleep(1.0)
            log.info("Voltage set to %s" % voltage)
            print("Voltage set to %s" % voltage) #for debugging purposes

        else: 
            print(f"Voltage must be between 0 and {self.max_voltage()}")
            log.error(f"Voltage must be between 0 and {self.max_voltage()}")
    
    def disconnect(self): 
        self.device.StopPolling()
        self.device.Disconnet()
        log.info("Device has been disconnected")
        print("Device has been disconnected") #for debugging purposes






