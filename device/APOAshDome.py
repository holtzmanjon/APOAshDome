"""
bl4 - shutter power
bl5,bh5 - set shutter direction 

bl2 - lower shutter power
bl3,bh3 - lower shutter direction

bl6 - rotate power
bl7,bh7 - set direction 

is_dome_home bit
"""

import Tristate
import time
from logging import Logger

UPPER_DIRECTION = 1
UPPER_POWER = 1
LOWER_DIRECTION = 1
LOWER_POWER = 1
HOME = 1

class Dome :
    def __init__(self, logger : Logger) :
        self.connected = True
        self.azimuth = None
        self.home = Tristate()
        self.is_upper_open = Tristate()
        self.is_upper_closed = Tristate()
        self.is_lower_open = Tristate()
        self.is_lower_closed = Tristate()

    def home(self) :
        """ Send dome to home 
        """
        if !self.home :
            self.rotate(1)
            while !self.home :
                continue

    def open_upper(self) :
        """ Open upper shutter
        """
        set_bit(UPPER_DIRECTION,1)
        set_bit(UPPER_POWER,1)
        time.sleep(10)
        set_bit(UPPER_POWER,0)
        self.is_upper_open = True

    def close_upper(self) :
        """ Close upper shutter
        """
        set_bit(UPPER_DIRECTION,1)
        set_bit(UPPER_POWER,1)
        time.sleep(10)
        set_bit(UPPER_POWER,0)
        self.is_upper_open = True

    def open_lower(self) :
        """ Open lower shutter
        """
        if is_upper_open == True :
            set_bit(LOWER_DIRECTION,1)
            set_bit(LOWER_POWER,1)
            time.sleep(10)
            set_bit(LOWER_POWER,0)
        else :
	    raise RuntimeError('cannot open lower shutter when upper shutter is not open')

    def close_lower(self) :
        """ Close lower shutter
        """
        if is_upper_open == True :
            set_bit(LOWER_DIRECTION,1)
            set_bit(LOWER_POWER,1)
            time.sleep(10)
            set_bit(LOWER_POWER,0)
        else :
	    raise RuntimeError('cannot close lower shutter when upper shutter is not open')

    def is_home(self) :
        if get_bit(HOME) :
            return True
        else :
            return False
        
    def rotate(self,cw=True) :
        """ Start dome rotating
        """
        if cw :
            set_bit(DOME_DIRECTION,1)
        else :
            set_bit(DOME_DIRECTION,0)
        set_bit(DOME_POWER,1)

    def get_azimuth(self) :

    def goto_azimuth(self,azimuth) :
        current_az = get_azimuth()
        diff = azimuth - current_az
        if abs(diff) > 180 :
            self.rotate(0)
        else :
            self.rotate(1)
        
def set_bit(bit) :
    return

def get_bit(bit) :
    return 0
