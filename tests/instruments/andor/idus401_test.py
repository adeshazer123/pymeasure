# Test code for Andor iDus camera 

import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.andor.idus401 import IDUS401


def test_set_camera():
    with expected_protocol(
        IDUS401,
        [("SetCurrentCamera", 1),
         ("GetCameraSerialNumber", 12345),
         ("Initialize", None),
         ],
    ) as inst:
        inst.set_camera(1)


def test_set_temperature():
    with expected_protocol(
        IDUS401,
        [("CoolerON", None),
         ("GetTemperatureRange", (-100, 100)),
         ("SetTemperature", -50),
         ],
    ) as inst:
        inst.set_temperature(-50)

def test_set_exposure_time():
    with expected_protocol(
        IDUS401,
        [("SetExposureTime", 0.5),
         ],
    ) as inst:
        inst.set_exposure_time(0.5)