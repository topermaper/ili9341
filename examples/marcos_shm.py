#!/usr/bin/python
# -*- coding:utf-8 -*-

import time
import sys
import os
import argparse

picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
import time
import numpy as np

from waveshare_2inch_LCD import ili9341

from PIL import Image,ImageDraw,ImageFont

from multiprocessing import shared_memory
import multiprocessing
import threading
from ball import Ball
from random import randint

import psutil



logging.basicConfig(level=logging.INFO)


class MarcosST7789Test:

    def initLCD(self):

        # Initialize  ILI9341 library
        if self._args == 1:
            self._disp = [ili9341.ILI9341(0)]
        elif self._args == 2:
            self._disp = [ili9341.ILI9341(0),self._disp = ili9341.ILI9341(1)]
        else:
            Exception('Only 2 LCD screens supported')


        self._disp = ili9341.ILI9341([0])
        for disp in self._disp:
            disp.Init()


    def parseArgs(self)
        parser = argparse.ArgumentParser(description='Drives 1 or 2 ILI9341 TFT screens over SPI using a RP3B+')
        parser.add_argument('--clock', dest='spi_clock_speed', type=int, default=32000000, help='SPI clock speed Hz')
        parser.add_argument('--display', dest='display', type=int, default=1, help='1 or 2 screens')
        self._args = parser.parse_args()


    def main(self):

        self.parseArgs()
        self.initLCD()
        
        condition = multiprocessing.Condition()
        
        process1 = multiprocessing.Process(target=self.processor, args=(condition,))
        process2 = multiprocessing.Process(target=self.renderer, args=(condition,))
        process1.start()
        process2.start()



    # A thread that produces data 
    def processor(self, condition):


        shm = shared_memory.SharedMemory(name='sh_buffer', create=True, size=(self._disp.height*self._disp.width*2))

        font30 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 30)
        font15 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 15)

        start_time = time.time()
        end_time   = 0

        while True: 

            fps = (1/(end_time - start_time))

            start_time = end_time

            image = Image.new('RGB', (self._disp.height,self._disp.width), (255,255,255)) 

            draw = ImageDraw.Draw(image)

            # print draw line
            draw.line([(40,20),(200,20)],   fill = "BLUE",width = 5)
            draw.line([(40,20),(40,200)],   fill = "BLUE",width = 5)
            draw.line([(40,200),(200,200)], fill = "BLUE",width = 5)
            draw.line([(200,20),(200,200)], fill = "BLUE",width = 5)

            # draw rectangle
            draw.rectangle([(50,30),(190,70)],fill = "BLUE")
                
            # draw text
            draw.text((60, 30), u'It works !', font = font30, fill = "WHITE")
            draw.text((85, 85), 'ILI9341 test', font = font15, fill = "BLUE")
            draw.text((90, 110), 'fps: {0:.2f}'.format(fps), font = font15, fill = "BLUE")
         
            # gives a single float value
            draw.text((90, 140), 'CPU: {0:.1f}%'.format(psutil.cpu_percent()), font = font15, fill = "BLUE")
            

            
            # Display some bubbles to stress the cpu
            for i in range(35):
                Ball(draw,randint(0,320),randint(0,240),randint(5,25))
            
   

            img = np.asarray(image)
            pix = np.zeros((240, 320,2), dtype = np.uint8)
            #RGB888 >> RGB565
            pix[...,[0]] = np.add(np.bitwise_and(img[...,[0]],0xF8),np.right_shift(img[...,[1]],5))
            pix[...,[1]] = np.add(np.bitwise_and(np.left_shift(img[...,[1]],3),0xE0), np.right_shift(img[...,[2]],3))
            
            #array = pix.flatten().tolist()

            with condition:
                condition.wait()
                nd_array = np.ndarray(shape=pix.shape, dtype = pix.dtype, buffer=shm.buf)
                nd_array[:] = pix[:]
                print ('Image ready for rendering')
            
            end_time = time.time()


    # A thread that consumes data 
    def renderer(self, condition):

        shm_buffer = shared_memory.SharedMemory(name='sh_buffer')
        
        start_time = time.time()
        end_time   = 0

        while True: 

            fps = (1/(end_time - start_time))
            start_time = end_time

            #read_from_buf = np.frombuffer(buffer=shm.buf, dtype=np.uint8)
            self._disp.Render(disp_id=0, shm_buffer=shm_buffer)

            with condition:
                condition.notify()

            print("Rendering at {:.3f}".format(fps))
            end_time = time.time()




if __name__ == "__main__":
    app = MarcosST7789Test()
    app.main()






