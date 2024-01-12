"""
Low level inteface to APO Ash Dome
"""

from tristate import Tristate
import time
from threading import Timer, Lock, Thread
from logging import Logger
import piplates.RELAYplate as RELAY
import Encoder
import timer

DOME_POWER = 1      #relay 207  pin 47
UPPER_POWER = 2     #relay 205  pin 48
DOME_DIRECTION = 3  #relay 208  pin 5
UPPER_DIRECTION = 4 #relay 206  pin 4
WATCHDOG_RESET = 5  #relay 201  pin 50

LOWER_DIRECTION = 6
LOWER_POWER = 7
HOME = 1

UPPER_TIME = 6
LOWER_TIME = 5
PARK_POSITION = 60
HOME_POSITION = 89
steps_per_degree = 725

ENCODER_A = 6
ENCODER_B = 13

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
        self.azimuth = HOME_POSITION
        self.is_upper_open = Tristate()
        self.is_upper_closed = Tristate()
        self.is_lower_open = Tristate()
        self.is_lower_closed = Tristate()
        self.cansetaltitude = False
        self.cansetazimuth = True
        self.cansetpark = True
        self.cansetshutter = True
        self.canfindhome = True
        self.canslave = False
        self.canpark = True
        self.cansyncazimuth = True
        self.slaved = False
        self.shutterstatus = ShutterState.shutterError.value
        self.slewing = False
        self.park_position = PARK_POSITION
        self.verbose = True
        self.enc = Encoder.Encoder(ENCODER_A,ENCODER_B)

    def reset_watchdog(self) :
        set_bit(WATCHDOG_RESET,1)
        set_bit(WATCHDOG_RESET,0)

    def home(self) :
        """ Send dome to home asynchronously
        """
        if  not self.athome() :
            t=Thread(target=self.sendhome)
            t.start()

    def sendhome(self,timout=180) :
        """ Go to home
        """
        if self.verbose : print('sending home')
        self.rotate(1)
        t=timer.Timer()
        t.start()
        while not self.athome() and t.elapsed()<timeout :
            continue
        if t.elapsed < timeout :
            self.azimuth = HOME_POSITION
        else :
            print('Home timer expired before finding home !)
        t.stop()

    def athome(self) :
        """ Check if at home position
        """
        #if get_bit(HOME) :
        if self.azimuth == HOME_POSITION :   # change when home sensing is implemented
            self.azimuth = HOME_POSITION
            set_bit(DOME_POWER,0)
            self.slewing = False
            return True
        else :
            return False

    def set_upper_open(self) :
        """ Set upper shutter status to open and turn off shutter power 
        """
        if self.verbose: print('setting upper shutter open')
        self.is_upper_open = True
        self.shutterstatus = ShutterState.shutterOpen.value
        set_bit(UPPER_POWER,0)

    def set_upper_closed(self) :
        """ Set upper shutter status to closed and turn off shutter power 
        """
        if self.verbose: print('setting upper shutter closed')
        self.is_upper_open = False
        self.shutterstatus = ShutterState.shutterClosed.value
        set_bit(UPPER_POWER,0)

    def open_upper(self) :
        """ Open upper shutter asynchronously
        """
        set_bit(UPPER_POWER,0)
        if self.verbose: print('starting shutter open')
        set_bit(UPPER_DIRECTION,1)
        set_bit(UPPER_POWER,1)
        self.shutterstatus = ShutterState.shutterOpening.value
        t=Timer(UPPER_TIME,self.set_upper_open)
        t.start()

    def close_upper(self) :
        """ Close upper shutter
        """
        set_bit(UPPER_POWER,0)
        if self.verbose: print('starting shutter close')
        set_bit(UPPER_DIRECTION,0)
        set_bit(UPPER_POWER,1)
        self.shutterstatus = ShutterState.shutterClosing.value
        t=Timer(UPPER_TIME,self.set_upper_closed)
        t.start()

    def set_lower_open(self) :
        """ Set lower shutter status to open and turn off shutter power 
        """
        self.is_lower_open = True
        set_bit(LOWER_POWER,0)

    def set_lower_closed(self) :
        """ Set lower shutter status to closed and turn off shutter power 
        """
        self.is_lower_open = True
        set_bit(LOWER_POWER,0)

    def open_lower(self) :
        """ Open lower shutter asynchronously
        """
        if is_upper_open == True :
            set_bit(LOWER_POWER,0)
            set_bit(LOWER_DIRECTION,1)
            set_bit(LOWER_POWER,1)
            t=Timer(LOWER_TIME,self.set_upper_open)
            t.start()
        else :
            raise RuntimeError('cannot open lower shutter when upper shutter is not open')

    def close_lower(self) :
        """ Close lower shutter
        """
        if is_upper_open == True :
            set_bit(LOWER_POWER,0)
            set_bit(LOWER_DIRECTION,1)
            set_bit(LOWER_POWER,1)
            t=Timer(LOWER_TIME,self.set_upper_open)
            t.start()
        else :
            raise RuntimeError('cannot close lower shutter when upper shutter is not open')

    def open_shutter(self,lower=False) :
        """ Open the dome shutter(s)
        """
        self.open_upper() 
        if lower :
            time.sleep(10)
            self.open_lower() 

    def close_shutter(self,lower=False) :
        """ Close the dome shutter(s)
        """
        if lower :
            self.close_lower() 
            time.sleep(10)
        self.close_upper() 

    def atpark(self) :
        """ Is telescope at park position?
        """
        az = self.get_azimuth()
        if abs(az-self.park_position) < 1 : 
            return True
        else :
            return False

    def set_park(self) :
        """ Set park position to current position
        """
        self.park_position = self.get_azimuth()

    def park(self) :
        """ Send dome to park asynchronously
        """
        if  not self.atpark() :
            t=Thread(target=self.sendpark)
            t.start()

    def sendpark(self) :
        """ Go to park
        """
        if self.verbose : print('sending to park')
        self.slewtoazimuth(self.park_position)
        
    def abort_slew(self) :
        """ Turn off dome rotation power
        """
        if self.verbose : print('abort: turning dome rotation power off')
        self.stop()

    def stop(self) :
        """ Stop dome rotation
        """
        if self.verbose : print('stopping dome rotation ')
        set_bit(DOME_POWER,0)
        self.slewing = False

    def rotate(self,cw=True) :
        """ Start dome rotating
        """
        self.stop()
        if self.verbose : print('starting dome rotation ', cw)
        if cw :
            set_bit(DOME_DIRECTION,1)
        else :
            set_bit(DOME_DIRECTION,0)
        set_bit(DOME_POWER,1)
        self.slewing = True

    def get_azimuth(self) :
        """ Get current dome azimuth
        """
        self.azimuth = self.enc.read()/steps_per_degree + HOME_POSITION
        return self.azimuth

        
    def slewtoazimuth(self,azimuth,timeout=180) :
        """ Slew to requested azimuth
        """
        current_az = self.azimuth

        print('desired_az',azimuth)
        print('  current_az',current_az)
        delta = diff(azimuth,current_az)
        print('  delta: ',delta)
        if delta > 0 :
            self.rotate(1)
        else :
            self.rotate(0)
        t=timer.Timer()
        t.start()
        while abs(diff(azimuth,self.get_azimuth())) > 1 and t.elapsed()<timeout : 
            print(self.azimuth)
            continue
        self.stop()
        if t.elapsed > timeout :
            print('Rotate timer expired before reaching desired azimuth !)
        print('self.azimuth', self.azimuth)
        t.stop()

    def slewtoaltitude(self, altitude) :
        raise RuntimeError('altitude slew not implemented')
        
    def slave(self,val) :
        raise RuntimeError('slaving not available') 

def set_bit(bit,value) :
    if value == 1 :
        RELAY.relayON(0,bit)
    else :
        RELAY.relayOFF(0,bit)
    time.sleep(0.2)
    return

def get_bit(bit,fake=None) :
    if fake is not None :
        return fake
    else :
        return 0

def diff(azimuth,current_az) :
    """ Get proper delta dome motion
    """
    delta = ( azimuth - current_az ) 
    if delta > 180 : delta-=360
    elif delta < -180 : delta+=360
    return delta
