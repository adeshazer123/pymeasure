# Author: Amelie Deshazer 
# Date: 2024-07-03
# Purpose: This script will control the piezoelectric stage to move the reference arm. 

import logging 

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class KPC101():
    def __init__(self):
        print("KPC101 initialized")