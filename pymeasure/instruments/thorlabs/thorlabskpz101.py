# Author: Amelie Deshazer 
# Date: 2024-07-03
# Purpose: This script will control the piezoelectric stage to move the reference arm. 

import logging 

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import clr 
import System

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


class KPZ101():
    def __init__(self):
        DeviceManagerCLI.BuildDeviceList()
        serial_number = '29252556' #must add serial number
        self.device = KCubePiezo.CreateKCubePiezo(serial_number)

        self.device.Connect(serial_number)

        info_device = self.device.GetDeviceInfo()
        log.info(info_device.Description)


        self.device.StartPolling(250)
        time.sleep(0.25)
        log.info("Device polling started")

        self.device.EnableDevice()
        time.sleep(0.25)
        log.info("Device enabled") 

        device_config = self.device.GetPiezoConfiguration(serial_number)
        log.info("Device configuration is %s" % device_config)

        device_settings = self.device.PiezoDeviceSettings
        
    def move_home(self):
        self.device.SetZero() 
        log.info("Device moved to home position")
    
    def max_voltage(self): 
        max_voltage = self.device.GetMaxOutputVoltage()
        return max_voltage
    
    def get_voltage(self): 
        voltage = self.device.GetOutputVoltage()
        return voltage
    
    def set_voltage(self,voltage):
        voltage = Decimal(voltage)
    
        min_volt = System.Decimal(0)
        max_volt = self.max_voltage()
        if voltage != min_volt and voltage <= max_volt:
            self.device.SetOutputVoltage(voltage)
            time.sleep(1.0)
            log.info("Voltage set to %s" % voltage)

        else: 
            log.error(f"Voltage must be between 0 and {max_volt}")
    
    def disconnect(self): 
        self.device.StopPolling()
        self.device.Disconnect()
        log.info("Device has been disconnected")






