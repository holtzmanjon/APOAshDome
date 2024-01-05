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

from tristate import Tristate
import time
from threading import Timer, Lock, Thread
from logging import Logger
import pigpio

UPPER_DIRECTION = 1
UPPER_POWER = 1
LOWER_DIRECTION = 1
LOWER_POWER = 1
HOME = 1

DOME_POWER = 1
DOME_DIRECTION = 1

UPPER_TIME = 86
LOWER_TIME = 80
PARK_POSITION = 45
HOME_POSITION = 45

from enum import Enum
class ShutterState(Enum) :
    shutterOpen = 0     # Dome shutter status open
    shutterClosed = 1   # Dome shutter status closed
    shutterOpening = 2  # Dome shutter status opening
    shutterClosing = 3  # Dome shutter status closing
    shutterError = 4     # Dome shutter status error

class Dome :
    def __init__(self, logger : Logger) :
        """  Initialize dome properties and capabilities
        """
        self.connected = True
        self.altitude = None
        self.is_upper_open = Tristate()
        self.is_upper_closed = Tristate()
        self.is_lower_open = Tristate()
        self.is_lower_closed = Tristate()
        self.cansetaltitude = False
        self.cansetazimuth = True
        self.cansetpark = True
        self.cansetshutter = True
        self.canfindhome = True
        self.canslave = True
        self.canpark = True
        self.cansyncazimuth = True
        self.slaved = False
        self.shutterstatus = ShutterState.shutterError.value
        self.slewing = False
        self.park_position = PARK_POSITION

    def home(self) :
        """ Send dome to home asynchronously
        """
        if  not self.athome() :
            t=Thread(target=self.sendhome)

    def sendhome(self) :
        self.rotate(1)
        while not self.athome() :
            continue
        self.azimuth = HOME_POSITION

    def athome(self) :
        if get_bit(HOME,fake=1) :
            self.azimuth = HOME_POSITION
            return True
        else :
            return False

    def set_upper_open() :
        self.is_upper_open = True
        self.shutterstatus = ShutterState.shutterOpen.value
        set_bit(UPPER_POWER,0)

    def set_upper_closed() :
        self.is_upper_open = False
        self.shutterstatus = ShutterState.shutterClosed.value
        set_bit(UPPER_POWER,0)

    def open_upper(self) :
        """ Open upper shutter
        """
        set_bit(UPPER_DIRECTION,1)
        set_bit(UPPER_POWER,1)
        self.shutterstatus = ShutterState.shutterOpening.value
        t=Timer(UPPER_TIME,set_upper_open)
        t.start()

    def close_upper(self) :
        """ Close upper shutter
        """
        set_bit(UPPER_DIRECTION,1)
        set_bit(UPPER_POWER,1)
        self.shutterstatus = ShutterState.shutterClosing.value
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

    def atpark(self) :
        az = self.get_azimuth()
        if abs(az-self.park_position) < 1 : 
            return True
        else :
            return False

    def setpark(self) :
        """ Set park position to current position
        """
        self.park_position = self.get_azimuth()
        
    def abort_slew(self) :
        set_bit(DOME_POWER,0)

    def rotate(self,cw=True) :
        """ Start dome rotating
        """
        if cw :
            set_bit(DOME_DIRECTION,1)
        else :
            set_bit(DOME_DIRECTION,0)
        set_bit(DOME_POWER,1)
        self.slewing = True

    def get_azimuth(self,fake=None) :
        if fake is not None :
            az = fake
        else :
            az = 0
        self.azimuth = az
        return az

    def slewtoazimuth(self,azimuth) :
        current_az = self.azimuth
        print('current_az',current_az)
        diff = azimuth - current_az
        if abs(diff) > 180 :
            self.rotate(0)
        else :
            self.rotate(1)
        print('diff', abs(self.get_azimuth(fake=azimuth)-azimuth))
        while abs(self.get_azimuth(fake=azimuth)-azimuth) > 1 : 
            continue
        print('self.azimth', self.azimuth)
        self.slewing = False

    def slewtoaltitude(self, altitude) :
        raise RuntimeError('altitude slew not implemented')
        
def set_bit(bit,value) :
    return

def get_bit(bit,fake=None) :
    if fake is not None :
        return fake
    else :
        return 0
