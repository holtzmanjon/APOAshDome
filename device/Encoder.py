"""
Encoder library for Raspberry Pi for measuring quadrature encoded signals.
based on routine by Mivallion <mivallion@gmail.com>
but mostly modified to use pigpio
"""
import pigpio
import numpy as np

class Encoder(object):
    """
    Encoder class allows to work with rotary encoder
    which connected via two pin A and B.
    Works only on interrupts because all RPi pins allow that.
    This library is a simple port of the Arduino Encoder library
    (https://github.com/PaulStoffregen/Encoder) 
    """
    def __init__(self, A, B):
        self.A = A
        self.B = B
        self.pos = 0
        self.delta=[0,1,-1,2,-1,0,-2,1,1,-2,0,-1,2,-1,1,0]
        self.counter = np.zeros(4,dtype=int)
        self.counter16 = np.zeros(16,dtype=int)
 
        self.pi=pigpio.pi()
        self.pi.set_mode( A, pigpio.INPUT) 
        self.pi.set_mode( B, pigpio.INPUT) 
        #self.pi.set_pull_up_down( A, pigpio.PUD_DOWN)
        #self.pi.set_pull_up_down( B, pigpio.PUD_DOWN)

        # note that we need to keep track of state with each callback, as events
        self.state=0
        self.reset()

        # note that we need to keep track of state with each callback, as events
        # may be generated faster than callbacks are called
        cb1 = self.pi.callback(A, pigpio.EITHER_EDGE, self.__changeA)
        cb2 = self.pi.callback(B, pigpio.EITHER_EDGE, self.__changeB)

    def reset(self) :
        self.state = 0
        self.stateA = np.zeros([1],dtype=np.int16)
        self.stateB = np.zeros([1],dtype=np.int16)
        self.stateA = self.pi.read(self.A)
        self.stateB = self.pi.read(self.B)
        if self.stateA : self.state |= 1
        if self.stateB : self.state |= 2
        self.counter=np.zeros(4,dtype=int)
        self.counter16=np.zeros(16,dtype=int)

    def __changeA(self,channel,level,tick) :
        """ Change stateA 
        """
        if level == 0 : self.stateA=0
        elif level == 1 : self.stateA=1
        #self.stateA = 1 - self.stateA
        self.__updatepos()

    def __changeB(self,channel,level,tick) :
        """ Change stateB 
        """
        if level == 0 : self.stateB=0
        elif level == 1 : self.stateB=1
        #self.stateB = 1 - self.stateB
        self.__updatepos()

    def __updatepos(self) :
        """ Calculate updated position
        """
        state = self.state & 3
        if self.stateA :
            state |= 4
        if self.stateB :
            state |= 8
        self.state = state >> 2
        self.pos += self.delta[state]
        self.counter[abs(self.delta[state])] +=1
        self.counter16[state] +=1

    """
    update() calling every time when value on A or B pins changes.
    It updates the current position based on previous and current states
    of the rotary encoder.
    But this uses read() which may be inaccurate as state might have changed
    """
    def __test(self, channel, level, tick):
        print(channel,level,tick)

    def __update(self, channel, level, tick):
        state = self.state & 3
        if self.pi.read(self.A):
            state |= 4
        if self.pi.read(self.B):
            state |= 8

        self.state = state >> 2

        if state == 1 or state == 7 or state == 8 or state == 14:
            self.pos += 1
        elif state == 2 or state == 4 or state == 11 or state == 13:
            self.pos -= 1
        elif state == 3 or state == 12:
            self.pos += 2
        elif state == 6 or state == 9:
            self.pos -= 2

    """
    read() simply returns the current position of the rotary encoder.
    """
    def read(self):
        return self.pos
