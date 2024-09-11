"""
Low level inteface to APO Ash Dome
"""

import time
import timer
import numpy as np
from threading import Timer, Lock, Thread
from logging import Logger
from tristate import Tristate
import Encoder

# put in try/except for readthedocs
try :
    import piplates.RELAYplate as RELAY
    import APOSafety
    import RPi.GPIO as GPIO
except :
    print('no APOSafety or RPi.GPIO')

# RELAYPlates relay numbers for different operations
DOME_POWER = 1      #relay 207  pin 47
UPPER_POWER = 2     #relay 205  pin 48
DOME_DIRECTION = 3  #relay 208  pin 5
UPPER_DIRECTION = 4 #relay 206  pin 4
WATCHDOG_RESET = 5  #relay 201  pin 50
LOWER_DIRECTION = 6
LOWER_POWER = 7

# GPIO bit for home sensor
HOME = 16

# time before shutters are reigster open or closed
UPPER_TIME = 86
LOWER_TIME = 5

# Park and home positions
PARK_POSITION = 60
HOME_POSITION = 80
DOME_TOLERANCE = 3

# GPIO pins for azimuth encoder
ENCODER_A = 5
ENCODER_B = 12
# scale for azimuth encoder
steps_per_degree = -724  

from enum import Enum
class ShutterState(Enum) :
    shutterOpen = 0     # Dome shutter status open
    shutterClosed = 1   # Dome shutter status closed
    shutterOpening = 2  # Dome shutter status opening
    shutterClosing = 3  # Dome shutter status closing
    shutterError = 4     # Dome shutter status error

class Dome() :
    def __init__(self, logger=None ) :
        """  Initialize dome properties and capabilities
        """
        self.connected = True
        self.altitude = None
        #try:
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
        GPIO.setup(HOME, GPIO.IN)
        self.SupportedActions=['weather']
        try:
            with open("SavedPosition.txt") as fp :
                self.azimuth=float(fp.read())
                self.enc.pos = int((self.azimuth - HOME_POSITION) * steps_per_degree)
        except: 
            self.azimuth = HOME_POSITION
        self.logger = logger
        self.logger.info('Instantiating dome device')
        self.start_watchdog()
        self.start_weather()

    def save_position(self) :
        """ Save current position to file
        """
        self.get_azimuth()
        with open("SavedPosition.txt","w") as fp :
            fp.write('{:7.1f}'.format(self.azimuth))

    def start_weather(self) :
        """ Start weather monitoring thread
        """
        self.safety=APOSafety.Safety(warnonly=False,use25m=True)
        t=Thread(target=self.monitor_weather)
        t.start()

    def monitor_weather(self,timeout=90) :
        """ Check weather periodically
        """
        while True :
            if not self.safety.issafe() and \
               not (self.shutterstatus == ShutterState.shutterClosed.value) and\
               not (self.shutterstatus == ShutterState.shutterClosing.value) : 
                self.close_shutter()
            time.sleep(timeout)

    def reset_watchdog(self,timeout=110) :
        """ Reset watchdog periodically
        """
        while True :
            self.logger.info('resetting watchdog')
            set_relay(WATCHDOG_RESET,1)
            time.sleep(5)
            set_relay(WATCHDOG_RESET,0)
            time.sleep(timeout)

    def start_watchdog(self) :
        """ Start thread to periodically reset watchdog
        """
        t=Thread(target=self.reset_watchdog)
        t.start()

    def home(self) :
        """ Send dome to home asynchronously
        """
        if  not self.athome() :
            t=Thread(target=self.sendhome)
            t.start()

    def sendhome(self,timeout=180) :
        """ Go to home
        """
        self.logger.info('sending home')
        self.rotate(1)
        t=timer.Timer()
        t.start()
        while not self.athome() and t.elapsed()<timeout :
            time.sleep(0.1)
            continue
        if t.elapsed() < timeout :
            self.logger.info('Encoder position at home: {:d}'.format(self.enc.pos))
            self.enc.pos = 0
            self.logger.info('Setting to zero{:d}'.format(self.enc.pos))
            self.azimuth = HOME_POSITION
            set_relay(DOME_POWER,0)
            self.slewing = False
            self.logger.info('hit home')
        else :
            self.logger.info('Home timer expired before finding home !')
        t.stop()
        self.save_position()


    def athome(self) :
        """ Check if at home position
        """
        if GPIO.input(HOME) :
            return True
        else :
            return False

    def set_upper_open(self) :
        """ Set upper shutter status to open and turn off shutter power 
        """
        self.logger.info('setting upper shutter open')
        self.is_upper_open = True
        self.shutterstatus = ShutterState.shutterOpen.value
        set_relay(UPPER_POWER,0)
        set_relay(UPPER_DIRECTION,0)

    def set_upper_closed(self) :
        """ Set upper shutter status to closed and turn off shutter power 
        """
        self.logger.info('setting upper shutter closed')
        self.is_upper_open = False
        self.shutterstatus = ShutterState.shutterClosed.value
        set_relay(UPPER_POWER,0)

    def open_upper(self) :
        """ Open upper shutter asynchronously
        """
        set_relay(UPPER_POWER,0)
        self.logger.info('starting shutter open')
        set_relay(UPPER_DIRECTION,0)
        set_relay(UPPER_POWER,1)
        self.shutterstatus = ShutterState.shutterOpening.value
        t=Timer(UPPER_TIME,self.set_upper_open)
        t.start()

    def close_upper(self) :
        """ Close upper shutter
        """
        set_relay(UPPER_POWER,0)
        self.logger.info('starting shutter close')
        set_relay(UPPER_DIRECTION,1)
        set_relay(UPPER_POWER,1)
        self.shutterstatus = ShutterState.shutterClosing.value
        t=Timer(UPPER_TIME,self.set_upper_closed)
        t.start()

    def set_lower_open(self) :
        """ Set lower shutter status to open and turn off shutter power 
        """
        self.is_lower_open = True
        set_relay(LOWER_POWER,0)

    def set_lower_closed(self) :
        """ Set lower shutter status to closed and turn off shutter power 
        """
        self.is_lower_open = True
        set_relay(LOWER_POWER,0)
        set_relay(LOWER_DIRECTION,0)

    def open_lower(self) :
        """ Open lower shutter asynchronously
        """
        if is_upper_open == True :
            set_relay(LOWER_POWER,0)
            set_relay(LOWER_DIRECTION,1)
            set_relay(LOWER_POWER,1)
            t=Timer(LOWER_TIME,self.set_upper_open)
            t.start()
        else :
            raise RuntimeError('cannot open lower shutter when upper shutter is not open')

    def close_lower(self) :
        """ Close lower shutter
        """
        if is_upper_open == True :
            set_relay(LOWER_POWER,0)
            set_relay(LOWER_DIRECTION,1)
            set_relay(LOWER_POWER,1)
            t=Timer(LOWER_TIME,self.set_upper_open)
            t.start()
        else :
            raise RuntimeError('cannot close lower shutter when upper shutter is not open')

    def open_shutter(self,lower=False) :
        """ Open the dome shutter(s). If lower, wait 10s after starting upper to start lower
        """
        if not self.safety.issafe() :
            self.logger.info('cannot open shutter due to weather condition!')
            return

        self.open_upper() 
        #if lower :
        #    time.sleep(10)
        #    self.open_lower() 

    def close_shutter(self,lower=False) :
        """ Close the dome shutter(s). If lower, wait 30s after starting lower to start upper
        """
        if lower :
            self.close_lower() 
            time.sleep(30)
        self.close_upper() 

    def atpark(self) :
        """ Is telescope at park position?
        """
        az = self.get_azimuth()
        if abs(az-self.park_position) < DOME_TOLERANCE : 
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
        self.logger.info('sending to park')
        self.slewtoazimuth(self.park_position)
        
    def abort_slew(self) :
        """ Turn off dome rotation power
        """
        self.logger.info('abort: turning dome rotation power off')
        self.stop()

    def stop(self) :
        """ Stop dome rotation
        """
        self.logger.info('stopping dome rotation ')
        set_relay(DOME_POWER,0)
        self.slewing = False
        self.enc.delta=np.array([0,1,-1,2,-1,0,-2,1,1,-2,0,-1,2,-1,1,0])
        #self.logger.debug('counter: {:d}'.format(self.enc.counter))
        #self.logger.debug('counter16: {:d}'.format(self.enc.counter16))
        #self.logger.debug('delta: {:f}'.format(self.enc.delta))
        #self.logger.debug('total events: {:d}'.format(np.sum(self.enc.counter16)))
        #self.logger.debug('sum: {:f}'.format(np.sum(self.enc.delta*self.enc.counter16)))
        #self.logger.debug('pos: {:d}'.format(self.enc.pos))

    def rotate(self,cw=True) :
        """ Start dome rotating
        """
        self.stop()
        if self.verbose : self.logger.info('starting dome rotation: {:d} '.format(cw))
        self.enc.reset()

        if cw :
            set_relay(DOME_DIRECTION,0)
            #self.enc.delta=[0,1,3,2,3,0,2,1,1,2,0,3,2,3,1,0]
        else :
            set_relay(DOME_DIRECTION,1)
            #self.enc.delta=[0,-3,-1,-2,-1,0,-2,-3,-3,-2,0,-1,-2,-1,-3,0]

        set_relay(DOME_POWER,1)
        self.slewing = True

    def get_azimuth(self) :
        """ Get current dome azimuth
        """
        self.azimuth = self.enc.pos/steps_per_degree + HOME_POSITION
        self.azimuth %= 360
        return self.azimuth

    def slewtoazimuth(self,azimuth) :
        """ Start slew to requested azimuth
        """
        t=Thread(target=lambda : self.gotoazimuth(azimuth))
        t.start()

    def gotoazimuth(self,azimuth,timeout=180) :
        """ slew to requested azimuth
        """
        current_az = self.azimuth

        self.logger.info('desired_az: {:f}'.format(azimuth))
        self.logger.info('  current_az: {:f}'.format(current_az))
        delta = diff(azimuth,current_az)
        self.logger.info('  delta: {:f}'.format(delta))
        if abs(delta) < DOME_TOLERANCE :
            return
        elif delta > 0 :
            self.rotate(1)
            #if going CW, undershoot to allow coast
            delta = -1.0
        else :
            self.rotate(0)
            #if going CCW, overshoot to allow coast
            delta = +1.0
        t=timer.Timer()
        t.start()
        x = lambda azimuth : diff(azimuth,self.get_azimuth()) 
        while abs(x(azimuth+delta)) > DOME_TOLERANCE/4. and t.elapsed()<timeout : 
            #print(self.azimuth)
            #time.sleep(1)
            continue
        self.stop()
        if t.elapsed() > timeout :
            self.logger.info('Rotate timer expired before reaching desired azimuth !')
        self.logger.info('self.azimuth: {:f}'.format(self.azimuth))
        t.stop()
        time.sleep(2)
        self.save_position()

    def slewtoaltitude(self, altitude) :
        return 
        #raise RuntimeError('altitude slew not implemented')
        
    def slave(self,val) :
        #self.slaved=True
        raise RuntimeError('slaving not available') 

def set_relay(bit,value) :
    """ Utility routine to turn RELAYplates relays on (1) or off

        Always sleep 200 ms after a call to give system time to respond before subsequent call
    """
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
