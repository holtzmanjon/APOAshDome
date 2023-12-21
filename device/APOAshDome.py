"""
Low level inteface to APO Ash Dome

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
from threading import Timer, Lock, Thread
from logging import Logger
import pigpio

UPPER_DIRECTION = 1
UPPER_POWER = 1
LOWER_DIRECTION = 1
LOWER_POWER = 1
HOME = 1

UPPER_TIME = 86
LOWER_TIME = 80
PARK_POSITION = 45

class Dome :
    def __init__(self, logger : Logger) :
        """  Initialize dome properties and capabilities
        """
        self.connected = True
        self.azimuth = None
        self.altitude = None
        self.is_upper_open = Tristate()
        self.is_upper_closed = Tristate()
        self.is_lower_open = Tristate()
        self.is_lower_closed = Tristate()
        self.cansetaltitude = False
        self.cansetazimuth = True
        self.cansetpark = True
        self.cansetshutter = True
        self.canslave = True
        self.cansyncazimuth = False
        self.slaved = False
        self.slewing = False
        self.park_position = PARK_POSITION

    def home(self) :
        """ Send dome to home asynchronously
        """
        if !self.athome() :
            t=thread(target=sendhome)

    def sendhome(self) :
        self.rotate(1)
        while !self.athome() :
            continue

    def set_upper_open() :
        self.is_upper_open = True
        set_bit(UPPER_POWER,0)

    def set_upper_closed() :
        self.is_upper_open = True
        set_bit(UPPER_POWER,0)

    def open_upper(self) :
        """ Open upper shutter
        """
        set_bit(UPPER_DIRECTION,1)
        set_bit(UPPER_POWER,1)
        t=Timer(UPPER_TIME,set_upper_open)
        t.start()

    def close_upper(self) :
        """ Close upper shutter
        """
        set_bit(UPPER_DIRECTION,1)
        set_bit(UPPER_POWER,1)
        t=Timer(UPPER_TIME,set_upper_open)
        t.start()

    def set_lower_open() :
        self.is_lower_open = True
        set_bit(LOWER_POWER,0)

    def set_lower_closed() :
        self.is_lower_open = True
        set_bit(LOWER_POWER,0)

    def open_lower(self) :
        """ Open lower shutter
        """
        if is_upper_open == True :
            set_bit(LOWER_DIRECTION,1)
            set_bit(LOWER_POWER,1)
            t=Timer(LOWER_TIME,set_upper_open)
            t.start()
        else :
	    raise RuntimeError('cannot open lower shutter when upper shutter is not open')

    def close_lower(self) :
        """ Close lower shutter
        """
        if is_upper_open == True :
            set_bit(LOWER_DIRECTION,1)
            set_bit(LOWER_POWER,1)
            t=Timer(LOWER_TIME,set_upper_open)
            t.start()
        else :
	    raise RuntimeError('cannot close lower shutter when upper shutter is not open')

    def open_shutter(self) :
        self.open_upper() 
        sleep(10)
        self.open_lower() 

    def close_shutter(self) :
        self.close_lower() 
        sleep(10)
        self.close_upper() 

    def athome(self) :
        if get_bit(HOME) :
            return True
        else :
            return False

    def atpark(self) :
        az = self.azimuth()
        if abs(az-self.park_position) < 1 : 
            return True
        else :
            return False

    def setpark(self) :
       """ Set park position to current position
       """
       self.park_position = azimuth()
        
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
