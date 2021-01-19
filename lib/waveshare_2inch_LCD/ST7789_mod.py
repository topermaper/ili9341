#!/usr/bin/python
# -*- coding:utf-8 -*-

from . import config
import RPi.GPIO as GPIO
import time
import numpy as np

from threading import Lock, Event


class ST7789MOD(object):
    def __init__(self, cs=[0]):
        self.width = 240
        self.height = 320
        
        self._dc = config.DC_PIN
        self._rst = config.RST_PIN
        self._bl = config.BL_PIN
        self._cs = config.CS_PIN
        self._cs_a = cs
        
        self._buffer_1 = [0xff]*(self.width * self.height * 2)
        self._buffer_2 = None

        # Renderer lock
        self._rl = Lock()
        # Processor lock
        self._pl = Lock()


    """    Write register address and data     """
    def command(self, cmd, cs):
        config.digital_write(self._cs, GPIO.LOW)
        config.digital_write(self._dc, GPIO.LOW)
        config.spi_writebyte([cmd], cs)
        config.digital_write(self._cs, GPIO.HIGH)

    def data(self, val, cs):
        config.digital_write(self._cs, GPIO.LOW)
        config.digital_write(self._dc, GPIO.HIGH)
        config.spi_writebyte([val], cs)
        config.digital_write(self._cs, GPIO.HIGH)

    def Init(self):
        """Initialize dispaly""" 
        config.module_init(self._cs_a)
        
        self.reset()
        
        for cs_id, cs in enumerate(self._cs_a):
            self.command(0x36, cs_id)
            self.data(0x00, cs_id) 

            self.command(0x3A, cs_id) 
            self.data(0x05, cs_id)

            self.command(0x21, cs_id) 

            self.command(0x2A, cs_id)
            self.data(0x00, cs_id)
            self.data(0x00, cs_id)
            self.data(0x01, cs_id)
            self.data(0x3F, cs_id)

            self.command(0x2B, cs_id)
            self.data(0x00, cs_id)
            self.data(0x00, cs_id)
            self.data(0x00, cs_id)
            self.data(0xEF, cs_id)

            self.command(0xB2, cs_id)
            self.data(0x0C, cs_id)
            self.data(0x0C, cs_id)
            self.data(0x00, cs_id)
            self.data(0x33, cs_id)
            self.data(0x33, cs_id)

            self.command(0xB7, cs_id)
            self.data(0x35, cs_id) 

            self.command(0xBB, cs_id)
            self.data(0x1F, cs_id)

            self.command(0xC0, cs_id)
            self.data(0x2C, cs_id)

            self.command(0xC2, cs_id)
            self.data(0x01, cs_id)

            self.command(0xC3, cs_id)
            self.data(0x12, cs_id)   

            self.command(0xC4, cs_id)
            self.data(0x20, cs_id)

            self.command(0xC6, cs_id)
            self.data(0x0F, cs_id) 

            self.command(0xD0, cs_id)
            self.data(0xA4, cs_id)
            self.data(0xA1, cs_id)

            self.command(0xE0, cs_id)
            self.data(0xD0, cs_id)
            self.data(0x08, cs_id)
            self.data(0x11, cs_id)
            self.data(0x08, cs_id)
            self.data(0x0C, cs_id)
            self.data(0x15, cs_id)
            self.data(0x39, cs_id)
            self.data(0x33, cs_id)
            self.data(0x50, cs_id)
            self.data(0x36, cs_id)
            self.data(0x13, cs_id)
            self.data(0x14, cs_id)
            self.data(0x29, cs_id)
            self.data(0x2D, cs_id)

            self.command(0xE1, cs_id)
            self.data(0xD0, cs_id)
            self.data(0x08, cs_id)
            self.data(0x10, cs_id)
            self.data(0x08, cs_id)
            self.data(0x06, cs_id)
            self.data(0x06, cs_id)
            self.data(0x39, cs_id)
            self.data(0x44, cs_id)
            self.data(0x51, cs_id)
            self.data(0x0B, cs_id)
            self.data(0x16, cs_id)
            self.data(0x14, cs_id)
            self.data(0x2F, cs_id)
            self.data(0x31, cs_id)
            self.command(0x21, cs_id)

            self.command(0x11, cs_id)

            self.command(0x29, cs_id)

    def reset(self):
        """Reset the display"""
        config.digital_write(self._rst,GPIO.HIGH)
        time.sleep(0.01)
        config.digital_write(self._rst,GPIO.LOW)
        time.sleep(0.01)
        config.digital_write(self._rst,GPIO.HIGH)
        time.sleep(0.01)
        
    def SetWindows(self, Xstart, Ystart, Xend, Yend, cs=0):
        #set the X coordinates
        self.command(0x2A, cs)
        self.data(Xstart>>8, cs)         #Set the horizontal starting point to the high octet
        self.data(Xstart & 0xff, cs)     #Set the horizontal starting point to the low octet
        self.data(Xend>>8, cs)           #Set the horizontal end to the high octet
        self.data((Xend - 1) & 0xff, cs) #Set the horizontal end to the low octet 
        
        #set the Y coordinates
        self.command(0x2B, cs)
        self.data(Ystart>>8, cs)
        self.data((Ystart & 0xff), cs)
        self.data(Yend>>8, cs)
        self.data((Yend - 1) & 0xff , cs)

        self.command(0x2C, cs)    

    
    def ProcessImage(self, image, disp_id=0):
        """Set buffer to value of Python Imaging Library image."""

        imwidth, imheight = image.size
        if imwidth == self.height and imheight == self.width:
            img = np.asarray(image)
            pix = np.zeros((self.width, self.height,2), dtype = np.uint8)
            #RGB888 >> RGB565
            pix[...,[0]] = np.add(np.bitwise_and(img[...,[0]],0xF8),np.right_shift(img[...,[1]],5))
            pix[...,[1]] = np.add(np.bitwise_and(np.left_shift(img[...,[1]],3),0xE0), np.right_shift(img[...,[2]],3))

            self._buffer_2 = pix.flatten().tolist()

            #print('im the processor all done, notifying {0:.3f}'.format(time.time()))
            self._image_event.set()
            #print('im the processor END {0:.3f}'.format(time.time()))
  


    def Render(self, shm_buffer, disp_id=0):
        """Set buffer to value of Python Imaging Library image."""
        """Write display buffer to physical display"""
        
        # Render buffer
        #print('im the rendered going to sleep {0:.3f}'.format(time.time()))

        if shm_buffer is not None:
            self.command(0x36, disp_id)
            self.data(0x70, disp_id) 
            self.SetWindows ( 0, 0, self.height,self.width, disp_id)
            config.digital_write(self._dc,GPIO.HIGH)

            image = np.frombuffer(buffer=shm_buffer.buf, dtype=np.uint8)

            # Use spi_writebytes2 to avoid calling tolist()
            config.spi_writebytes2(image)

            '''
            image = image.tolist()
            for i in range(0,len(image),4096):
                config.spi_writebyte(image[i:i+4096], disp_id)
            '''


        
    def clear(self, disp_id=0):
        """Clear contents of image buffer"""
        _buffer = [0xff]*(self.width * self.height * 2)
        self.SetWindows ( 0, 0, self.width, self.height, disp_id)
        config.digital_write(self._dc,GPIO.HIGH)
        for i in range(0,len(_buffer),4096):
            config.spi_writebyte(_buffer[i:i+4096], disp_id)		
