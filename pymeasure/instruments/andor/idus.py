#Driver code to command Andor Idus camera to take images 

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


from andor_dlls import *

class AndorIdus(): 
    def __init__(self, camera_name): 
        self.camera_name = "" #must add camera name
        self.camera = None
        self.initialize_camera()