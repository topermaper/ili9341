#!/usr/bin/python
# -*- coding:utf-8 -*-

from . import config
import RPi.GPIO as GPIO
import time
import numpy as np
import logging
import mmap
import os


from PIL import Image
from threading import Event
from multiprocessing import Lock, Value, Condition
import ctypes


class Frontpanel(object):

    def __init__(self, display, spi_speed):
        super()

        self._display = []

        for disp in display:
            # Only ILI9341 is supported by now
            if disp == 'ILI9341':
                from .ili9341 import ILI9341
                self._display.append(ILI9341(disp_id=len(self._display),spi_speed=spi_speed))
            else:
                logging.error("Display {} not supported".format(disp))
                sys.exit()

        for disp in self._display:
            disp.Init()

        # Create shared memory buffer, one per display
        self._shm_buffer_name = []
        self._shm_buffer = []

        for cs in range(len(self._display)):
            bufsize = self._display[cs].width * self._display[cs].height * 2
            self._shm_buffer.append(mmap.mmap(-1, length=bufsize, access=mmap.ACCESS_WRITE))

        # Parameters to share between processes
        self._image_ready = Value(ctypes.c_bool,False,lock=False) # This object is stored in shared memory
        self._condition = Condition(lock=Lock())

        pid = os.fork()
        if pid == 0:
            # Child process
            self.renderer(self._condition, self._image_ready)


    def display(self,image,disp_id=0):

        # Convert RGB888 to RGB565
        img = np.asarray(image)
        pix = np.zeros((240, 320,2), dtype = np.uint8)
        
        pix[...,[0]] = np.add(np.bitwise_and(img[...,[0]],0xF8),np.right_shift(img[...,[1]],5))
        pix[...,[1]] = np.add(np.bitwise_and(np.left_shift(img[...,[1]],3),0xE0), np.right_shift(img[...,[2]],3))

        nd_array = np.ndarray(shape=pix.shape, dtype = pix.dtype, buffer=self._shm_buffer[disp_id])
           
        with self._condition:
            if self._image_ready.value == True: 
                self._condition.wait()

            nd_array[:] = pix[:]

            self._image_ready.value = True
            self._condition.notify()


    def renderer(self, condition, image_ready):
        
        logging.debug("I'm the renderer process")

        #start_time = time.time()
        #end_time   = 0

        while True:

            #fps = (1/(end_time - start_time))
            #start_time = end_time

            self._display[0].SetWindows(0, 0, 320, 240)
            config.digital_write(self._display[0]._dc,GPIO.HIGH)

            #image = np.frombuffer(buffer= self._shm_buffer[0].buf, dtype=np.uint8)

            with condition:
                if image_ready.value == False:
                    condition.wait()

                # Use spi_writebytes2 to avoid calling tolist()
                config.spi_writebytes2(self._shm_buffer[0], 0)

                self._image_ready.value = False     
                condition.notify()

            #logging.info("Rendering at {:.1f} fps".format(fps))
            #end_time = time.time()  
