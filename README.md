# Ascom Alpaca Device Driver for 1m Ash Dome at Apache Point Observatory

Implement a simple Alpaca driver for 1m Ash Dome, using the Autoscope
dome control box. This box has relays that allow for power on/off to
dome rotation motor and shutter motor, and relays that allow for change
of motor direction on each of these. The system also has a watchdog
input, such that if power is dropped on the watchdog, the dome shutter
will close automatically. The system also has relay to switch between
manual and automatic mode; computer control only enabled under the 
latter. Separately from the motor control, there is an encoder on
the rotator gearbox, and a magnetic home sensor.

## Motor control

Specifically, computer control is implemented through four connectors
on the right side of the dome control box:
J805A : supplies power and control for dome rotation power
    Pin 1:
    Pin 2:
    Pin 3:
    Pin 4:
J806A : supplies power and control for dome rotation direction
    Pin 1:
    Pin 2:
    Pin 3:
    Pin 4:
J807A : supplies control for shutter rotation and direction
    Pin 1:
    Pin 2:
    Pin 3:
    Pin 4:
    Pin 5:
    Pin 6:
    Pin 7:
    Pin 8:
    Pin 9:
J808A : supplies +24V from watchdog
    Pin 1:
    Pin 2:
    Pin 3:
    Pin 4:

## Encoder

Dome position is read separately from a quadrature encoder, hooked
up directly to the Raspberry Pi. This gets +5V from the computer,
and returns +5V signals, which must be level-shifted to 3.3V before
input to RPi GPIO pins. Changes in level are detected using pigpiod;
separation of typical pulse times are several hundred microseconds.

## Home sensor

## Setup for Raspberry Pi:
   - enable VNC, SPI
   - python -m venv venv
   - pip install falcon toml ipython pi-plates spidev RPi.GPIO pigpiod
   - pigpiod daemon must be running:  sudo pigpiod -s 10
     (sampling rate of 10 microsec is fine)

## Software routines

Alpaca driver implemented in app.py and dome.py

APO routines are implemented in Dome class in APOAshDome.py and Encoder.py

  

