import os
import logging
import sys
import time


class RaspberryPi:
    # Pin definition
    RST_PIN = 25
    DC_PIN = 24
    BL_PIN = 15
    CS_PIN = [8,7] # GPIO 8 for display 0, GPIO 7 for display 1

    def __init__(self):
       self.SPI = []
             
    def digital_write(self, pin, value):
        self.GPIO.output(pin, value)

    def digital_read(self, pin):
        return self.GPIO.input(pin)

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data, cs=0):
        self.SPI[cs].writebytes(data)

    def spi_writebytes2(self, data, cs=0):
        self.SPI[cs].writebytes2(data)

    def module_init(self, cs=0):
        import spidev as SPI
        import RPi.GPIO

        self.GPIO = RPi.GPIO
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setwarnings(False)
        self.GPIO.setup(self.RST_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.DC_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.BL_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.CS_PIN, self.GPIO.OUT)

        spi = SPI.SpiDev(0, cs)
        spi.mode = 0b00
        spi.max_speed_hz = 32000000 
        self.SPI.append(spi)
        
        return 0

    def module_exit(self):
        logging.debug("spi end")
        for spi in self.SPI:
        	spi.close()

        logging.debug("close 5V, Module enters 0 power consumption ...")
        self.GPIO.output(self.RST_PIN, 0)
        self.GPIO.output(self.DC_PIN, 0)

        self.GPIO.cleanup()


implementation = RaspberryPi()

for func in [x for x in dir(implementation) if not x.startswith('_')]:
    setattr(sys.modules[__name__], func, getattr(implementation, func))
