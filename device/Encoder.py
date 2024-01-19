"""
Encoder library for Raspberry Pi for measuring quadrature encoded signals.
created by Mivallion <mivallion@gmail.com>
Version 1.0 - 01 april 2020 - inital release
"""
import RPi.GPIO as GPIO
import pigpio

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
        self.state = 0
        #GPIO.setmode(GPIO.BCM)
        #GPIO.setup(A, GPIO.IN)
        #GPIO.setup(B, GPIO.IN)
        #if GPIO.input(A):
        #    self.state |= 1
        #if GPIO.input(B):
        #    self.state |= 2
        #GPIO.remove_event_detect(A)
        #GPIO.remove_event_detect(B)
        #GPIO.add_event_detect(A, GPIO.BOTH, callback=self.__update)
        #GPIO.add_event_detect(B, GPIO.BOTH, callback=self.__update)
 
        self.pi=pigpio.pi()
        self.pi.set_mode( A, pigpio.INPUT) 
        self.pi.set_mode( B, pigpio.INPUT) 
        cb1 = self.pi.callback(A, pigpio.EITHER_EDGE, self.__update)
        cb2 = self.pi.callback(B, pigpio.EITHER_EDGE, self.__update)

    """
    update() calling every time when value on A or B pins changes.
    It updates the current position based on previous and current states
    of the rotary encoder.
    """
    def __update(self, channel):
        state = self.state & 3
        if self.pi.read(self.A):
            state |= 4
        if self.pi.read(self.B):
            state |= 8
        #if GPIO.input(self.A):
        #    state |= 4
        #if GPIO.input(self.B):
        #    state |= 8

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
