#!/usr/bin/python
# -*- coding:utf-8 -*-

from . import config
import RPi.GPIO as GPIO
import time
import numpy as np

from threading import Event


# Constants for interacting with display registers.
ILI9341_TFTWIDTH    = 240
ILI9341_TFTHEIGHT   = 320

ILI9341_NOP         = 0x00
ILI9341_SWRESET     = 0x01
ILI9341_RDDID       = 0x04
ILI9341_RDDST       = 0x09

ILI9341_SLPIN       = 0x10
ILI9341_SLPOUT      = 0x11
ILI9341_PTLON       = 0x12
ILI9341_NORON       = 0x13

ILI9341_RDMODE      = 0x0A
ILI9341_RDMADCTL    = 0x0B
ILI9341_RDPIXFMT    = 0x0C
ILI9341_RDIMGFMT    = 0x0A
ILI9341_RDSELFDIAG  = 0x0F

ILI9341_INVOFF      = 0x20
ILI9341_INVON       = 0x21
ILI9341_GAMMASET    = 0x26
ILI9341_DISPOFF     = 0x28
ILI9341_DISPON      = 0x29

ILI9341_CASET       = 0x2A
ILI9341_PASET       = 0x2B
ILI9341_RAMWR       = 0x2C
ILI9341_RAMRD       = 0x2E

ILI9341_PTLAR       = 0x30
ILI9341_MADCTL      = 0x36
ILI9341_PIXFMT      = 0x3A

ILI9341_FRMCTR1     = 0xB1
ILI9341_FRMCTR2     = 0xB2
ILI9341_FRMCTR3     = 0xB3
ILI9341_INVCTR      = 0xB4
ILI9341_DFUNCTR     = 0xB6

ILI9341_PWCTR1      = 0xC0
ILI9341_PWCTR2      = 0xC1
ILI9341_PWCTR3      = 0xC2
ILI9341_PWCTR4      = 0xC3
ILI9341_PWCTR5      = 0xC4
ILI9341_VMCTR1      = 0xC5
ILI9341_VMCTR2      = 0xC7

ILI9341_RDID1       = 0xDA
ILI9341_RDID2       = 0xDB
ILI9341_RDID3       = 0xDC
ILI9341_RDID4       = 0xDD

ILI9341_GMCTRP1     = 0xE0
ILI9341_GMCTRN1     = 0xE1

ILI9341_PWCTR6      = 0xFC

ILI9341_BLACK       = 0x0000
ILI9341_BLUE        = 0x001F
ILI9341_RED         = 0xF800
ILI9341_GREEN       = 0x07E0
ILI9341_CYAN        = 0x07FF
ILI9341_MAGENTA     = 0xF81F
ILI9341_YELLOW      = 0xFFE0
ILI9341_WHITE       = 0xFFFF

class ILI9341(object):

    def __init__(self, disp_id=0):
        self.width  = ILI9341_TFTWIDTH
        self.height = ILI9341_TFTHEIGHT
        
        self._dc  = config.DC_PIN
        self._rst = config.RST_PIN
        self._bl  = config.BL_PIN
        self._cs  = config.CS_PIN[disp_id]

        self._disp_id = disp_id


    """    Write register address and data     """
    def command(self, cmd, disp_id):
        config.digital_write(self._cs, GPIO.LOW)
        config.digital_write(self._dc, GPIO.LOW)
        #print("Command: {} screen: {}".format(hex(cmd),disp_id))
        config.spi_writebyte([cmd], disp_id)
        config.digital_write(self._cs, GPIO.HIGH)

    def data(self, val, disp_id):
        config.digital_write(self._cs, GPIO.LOW)
        config.digital_write(self._dc, GPIO.HIGH)
        #print("Data: {} screen: {}".format(hex(val),disp_id))
        config.spi_writebyte([val], disp_id)
        config.digital_write(self._cs, GPIO.HIGH)

    def Init(self):
        """Initialize dispaly""" 

        config.module_init(self._disp_id)
        
        self.reset()
        
        self.command(0xEF, self._disp_id)
        self.data(0x03, self._disp_id)
        self.data(0x80, self._disp_id)
        self.data(0x02, self._disp_id)
        self.command(0xCF, self._disp_id)
        self.data(0x00, self._disp_id)
        self.data(0XC1, self._disp_id)
        self.data(0X30, self._disp_id)
        self.command(0xED, self._disp_id)
        self.data(0x64, self._disp_id)
        self.data(0x03, self._disp_id)
        self.data(0X12, self._disp_id)
        self.data(0X81, self._disp_id)
        self.command(0xE8, self._disp_id)
        self.data(0x85, self._disp_id)
        self.data(0x00, self._disp_id)
        self.data(0x78, self._disp_id)
        self.command(0xCB, self._disp_id)
        self.data(0x39, self._disp_id)
        self.data(0x2C, self._disp_id)
        self.data(0x00, self._disp_id)
        self.data(0x34, self._disp_id)
        self.data(0x02, self._disp_id)
        self.command(0xF7, self._disp_id)
        self.data(0x20, self._disp_id)
        self.command(0xEA, self._disp_id)
        self.data(0x00, self._disp_id)
        self.data(0x00, self._disp_id)
        self.command(ILI9341_PWCTR1, self._disp_id)    # Power control
        self.data(0x23, self._disp_id)                    # VRH[5:0]
        self.command(ILI9341_PWCTR2, self._disp_id)    # Power control
        self.data(0x10, self._disp_id)                    # SAP[2:0];BT[3:0]
        self.command(ILI9341_VMCTR1, self._disp_id)   # VCM control
        self.data(0x3e, self._disp_id)
        self.data(0x28, self._disp_id)
        self.command(ILI9341_VMCTR2, self._disp_id)    # VCM control2
        self.data(0x86, self._disp_id)                    # --
        self.command(ILI9341_MADCTL, self._disp_id)    #  Memory Access Control
        self.data(0x38, self._disp_id)
        self.command(ILI9341_PIXFMT, self._disp_id)
        self.data(0x55, self._disp_id)
        self.command(ILI9341_FRMCTR1, self._disp_id)
        self.data(0x00, self._disp_id)
        self.data(0x18, self._disp_id)
        self.command(ILI9341_DFUNCTR, self._disp_id)    #  Display Function Control
        self.data(0x08, self._disp_id)
        self.data(0x82, self._disp_id)
        self.data(0x27, self._disp_id)
        self.command(0xF2, self._disp_id)                #  3Gamma Function Disable
        self.data(0x00, self._disp_id)
        self.command(ILI9341_GAMMASET, self._disp_id)    # Gamma curve selected
        self.data(0x01, self._disp_id)
        self.command(ILI9341_GMCTRP1, self._disp_id)    # Set Gamma
        self.data(0x0F, self._disp_id)
        self.data(0x31, self._disp_id)
        self.data(0x2B, self._disp_id)
        self.data(0x0C, self._disp_id)
        self.data(0x0E, self._disp_id)
        self.data(0x08, self._disp_id)
        self.data(0x4E, self._disp_id)
        self.data(0xF1, self._disp_id)
        self.data(0x37, self._disp_id)
        self.data(0x07, self._disp_id)
        self.data(0x10, self._disp_id)
        self.data(0x03, self._disp_id)
        self.data(0x0E, self._disp_id)
        self.data(0x09, self._disp_id)
        self.data(0x00, self._disp_id)
        self.command(ILI9341_GMCTRN1, self._disp_id)    # Set Gamma
        self.data(0x00, self._disp_id)
        self.data(0x0E, self._disp_id)
        self.data(0x14, self._disp_id)
        self.data(0x03, self._disp_id)
        self.data(0x11, self._disp_id)
        self.data(0x07, self._disp_id)
        self.data(0x31, self._disp_id)
        self.data(0xC1, self._disp_id)
        self.data(0x48, self._disp_id)
        self.data(0x08, self._disp_id)
        self.data(0x0F, self._disp_id)
        self.data(0x0C, self._disp_id)
        self.data(0x31, self._disp_id)
        self.data(0x36, self._disp_id)
        self.data(0x0F, self._disp_id)
        self.command(ILI9341_SLPOUT, self._disp_id)    # Exit Sleep
        time.sleep(0.120)
        self.command(ILI9341_DISPON, self._disp_id)    # Display on

    def reset(self):
        """Reset the display"""
        config.digital_write(self._rst,GPIO.HIGH)
        time.sleep(0.01)
        config.digital_write(self._rst,GPIO.LOW)
        time.sleep(0.01)
        config.digital_write(self._rst,GPIO.HIGH)
        time.sleep(0.01)
    

    def SetWindows(self, x0=0, y0=0, x1=None, y1=None, cs=0):
        """Set the pixel address window for proceeding drawing commands. x0 and
        x1 should define the minimum and maximum x pixel bounds.  y0 and y1
        should define the minimum and maximum y pixel bound.  If no parameters
        are specified the default will be to update the entire display from 0,0
        to 239,319.
        """
        if x1 is None:
            x1 = self.width-1
        if y1 is None:
            y1 = self.height-1
        self.command(ILI9341_CASET ,cs)        # Column addr set
        self.data(x0 >> 8, cs)
        self.data(x0, cs)                    # XSTART
        self.data(x1 >> 8, cs)
        self.data(x1, cs)                   # XEND
        self.command(ILI9341_PASET, cs)        # Row addr set
        self.data(y0 >> 8, cs)
        self.data(y0, cs)                # YSTART
        self.data(y1 >> 8, cs)
        self.data(y1, cs)                    # YEND
        self.command(ILI9341_RAMWR, cs)        # write to RAM

    def Render(self, shm_buffer, disp_id=0):
        """Set buffer to value of Python Imaging Library image."""
        """Write display buffer to physical display"""
        
        # Render buffer
        #print('im the rendered going to sleep {0:.3f}'.format(time.time()))

        if shm_buffer is not None:

            self.SetWindows ( 0, 0, self.height, self.width, disp_id)
            config.digital_write(self._dc,GPIO.HIGH)

            image = np.frombuffer(buffer=shm_buffer.buf, dtype=np.uint8)

            # Use spi_writebytes2 to avoid calling tolist()
            config.spi_writebytes2(image, disp_id)

