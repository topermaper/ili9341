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


class MarcosST7789Test:

    def initLCD(self):

        # Initialize  ILI9341 library
        if self._args.dual:
            self._disp = [ili9341.ILI9341(0), ili9341.ILI9341(1)]
        else:
            self._disp = [ili9341.ILI9341(0)]

        for disp in self._disp:
            disp.Init()


    def parseArgs(self):
        parser = argparse.ArgumentParser(description='Drives 1 or 2 ILI9341 TFT screens over SPI using a RP3B+')
        parser.add_argument('--clock', dest='spi_clock', type=int, default=32000000, help='SPI clock speed Hz')
        parser.add_argument('--dual',  default=False, action=argparse.BooleanOptionalAction, help='Enables dual screen')
        parser.add_argument('--bubbles', dest='bubbles', type=int, default=25, help='Amount of bubbles per frames. Bubbles are used to stress to CPU during testing.')
        parser.add_argument(
            '-d', '--debug',
            help="Print lots of debugging statements",
            action="store_const", dest="loglevel", const=logging.DEBUG,
            default=logging.WARNING,
        )
        parser.add_argument(
            '-v', '--verbose',
            help="Be verbose",
            action="store_const", dest="loglevel", const=logging.INFO,
        )
        
        self._args = parser.parse_args()

        logging.basicConfig(level=self._args.loglevel)
        logging.debug(self._args)


    def main(self):

        self.parseArgs()
        self.initLCD()

        condition = multiprocessing.Condition()
        
        process1 = multiprocessing.Process(target=self.processor, args=(condition,))
        process2 = multiprocessing.Process(target=self.renderer, args=(condition,))
        process1.start()
        process2.start()


    # Returns pixel array in format RGB565, ready for rendering
    def drawDisplay1(self):
        image = Image.new('RGB', (ili9341.ILI9341_TFTHEIGHT, ili9341.ILI9341_TFTWIDTH), (255,255,255)) 

        draw = ImageDraw.Draw(image)

        # print draw line
        draw.line([(40,20),(200,20)],   fill = "BLUE",width = 5)
        draw.line([(40,20),(40,200)],   fill = "BLUE",width = 5)
        draw.line([(40,200),(200,200)], fill = "BLUE",width = 5)
        draw.line([(200,20),(200,200)], fill = "BLUE",width = 5)

        # draw rectangle
        draw.rectangle([(50,30),(190,70)],fill = "BLUE")
            
        # draw text
        draw.text((60, 30), u'It works !', font = self._fonts['font30'], fill = "WHITE")
        draw.text((85, 85), 'ILI9341 test', font = self._fonts['font15'], fill = "BLUE")
        draw.text((90, 110), 'fps: {0:.2f}'.format(self.fps), font = self._fonts['font15'], fill = "BLUE")
        
        # gives a single float value
        draw.text((90, 140), 'CPU: {0:.1f}%'.format(psutil.cpu_percent()), font = self._fonts['font15'], fill = "BLUE")

        draw.text((240, 90), '1', font = self._fonts['font60'], fill = "BLACK")
        
        # Display some bubbles to stress the cpu
        for i in range(self._args.bubbles):
            Ball(draw,randint(0,320),randint(0,240),randint(5,25))

        img = np.asarray(image)
        pix = np.zeros((240, 320,2), dtype = np.uint8)
        #RGB888 >> RGB565
        pix[...,[0]] = np.add(np.bitwise_and(img[...,[0]],0xF8),np.right_shift(img[...,[1]],5))
        pix[...,[1]] = np.add(np.bitwise_and(np.left_shift(img[...,[1]],3),0xE0), np.right_shift(img[...,[2]],3))

        return pix


    # Returns pixel array in format RGB565, ready for rendering
    def drawDisplay2(self):
        image = Image.new('RGB', (ili9341.ILI9341_TFTHEIGHT, ili9341.ILI9341_TFTWIDTH), (255,255,255)) 

        draw = ImageDraw.Draw(image)

        # print draw line
        draw.line([(40,20),(200,20)],   fill = "RED",width = 5)
        draw.line([(40,20),(40,200)],   fill = "RED",width = 5)
        draw.line([(40,200),(200,200)], fill = "RED",width = 5)
        draw.line([(200,20),(200,200)], fill = "RED",width = 5)

        # draw rectangle
        draw.rectangle([(50,30),(190,70)],fill = "RED")
            
        # draw text
        draw.text((60, 30), u'It works !', font = self._fonts['font30'], fill = "WHITE")
        draw.text((85, 85), 'ILI9341 test', font = self._fonts['font15'], fill = "RED")
        draw.text((90, 110), 'fps: {0:.2f}'.format(self.fps), font = self._fonts['font15'], fill = "RED")
        
        # gives a single float value
        draw.text((90, 140), 'CPU: {0:.1f}%'.format(psutil.cpu_percent()), font = self._fonts['font15'], fill = "RED")

        draw.text((240, 90), '2', font = self._fonts['font60'], fill = "BLACK")
        
        # Display some bubbles to stress the cpu
        for i in range(self._args.bubbles):
            Ball(draw,randint(0,320),randint(0,240),randint(5,25))

        img = np.asarray(image)
        pix = np.zeros((240, 320,2), dtype = np.uint8)
        #RGB888 >> RGB565
        pix[...,[0]] = np.add(np.bitwise_and(img[...,[0]],0xF8),np.right_shift(img[...,[1]],5))
        pix[...,[1]] = np.add(np.bitwise_and(np.left_shift(img[...,[1]],3),0xE0), np.right_shift(img[...,[2]],3))

        return pix

    def loadFonts(self):
        self._fonts = {}
        self._fonts['font60'] = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 60)
        self._fonts['font30'] = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 30)
        self._fonts['font15'] = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 15)

 
    # A thread that produces data 
    def processor(self, condition):

        # Shared memmory buffer
        shm = shared_memory.SharedMemory(name=self._disp[0]._shm_buffer_name)

        if self._args.dual:
            shm2 = shared_memory.SharedMemory(name=self._disp[1]._shm_buffer_name)

        # Load fonts
        self.loadFonts()


        start_time = time.time()
        end_time   = 0

        while True: 

            self.fps = (1/(end_time - start_time))

            start_time = end_time

            ############## IMAGE 1 ###############
            pix = self.drawDisplay1()
            
            ############## IMAGE 2 ###############
            if self._args.dual:
                pix2 = self.drawDisplay2()

            with condition:
                condition.wait()
                nd_array = np.ndarray(shape=pix.shape, dtype = pix.dtype, buffer=shm.buf)
                nd_array[:] = pix[:]
                if self._args.dual:
                    nd_array2 = np.ndarray(shape=pix2.shape, dtype = pix2.dtype, buffer=shm2.buf)
                    nd_array2[:] = pix2[:]
                logging.debug('Image ready for rendering')
            
            end_time = time.time()


    # A thread that consumes data 
    def renderer(self, condition):
        
        start_time = time.time()
        end_time   = 0

        while True: 

            fps = (1/(end_time - start_time))
            start_time = end_time

            for disp in self._disp:
                disp.Render()

            with condition:
                condition.notify()

            logging.info("Rendering at {:.2f} fps".format(fps))
            end_time = time.time()




if __name__ == "__main__":
    app = MarcosST7789Test()
    app.main()






