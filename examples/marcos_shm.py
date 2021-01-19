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
        if self._args.display == 1:
            self._disp = [ili9341.ILI9341(0)]
        elif self._args.display == 2:
            self._disp = [ili9341.ILI9341(0), ili9341.ILI9341(1)]
        else:
            raise Exception('Only 2 LCD screens supported')

        for disp in self._disp:
            disp.Init()


    def parseArgs(self):
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

        shm = shared_memory.SharedMemory(name=self._disp[0]._shm_buffer_name)

        if self._args.display == 2:
            shm2 = shared_memory.SharedMemory(name=self._disp[1]._shm_buffer_name)

        font60 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 60)
        font30 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 30)
        font15 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 15)

        start_time = time.time()
        end_time   = 0

        while True: 

            fps = (1/(end_time - start_time))

            start_time = end_time

            ############## IMAGE 1 ###############
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
            draw.text((60, 30), u'It works !', font = font30, fill = "WHITE")
            draw.text((85, 85), 'ILI9341 test', font = font15, fill = "BLUE")
            draw.text((90, 110), 'fps: {0:.2f}'.format(fps), font = font15, fill = "BLUE")
         
            # gives a single float value
            draw.text((90, 140), 'CPU: {0:.1f}%'.format(psutil.cpu_percent()), font = font15, fill = "BLUE")

            draw.text((240, 90), '1', font = font60, fill = "BLACK")
            
            # Display some bubbles to stress the cpu
            for i in range(20):
                Ball(draw,randint(0,320),randint(0,240),randint(5,25))

            img = np.asarray(image)
            pix = np.zeros((240, 320,2), dtype = np.uint8)
            #RGB888 >> RGB565
            pix[...,[0]] = np.add(np.bitwise_and(img[...,[0]],0xF8),np.right_shift(img[...,[1]],5))
            pix[...,[1]] = np.add(np.bitwise_and(np.left_shift(img[...,[1]],3),0xE0), np.right_shift(img[...,[2]],3))
            
            ############## IMAGE 2 ###############
            if self._args.display == 2:
                image2 = Image.new('RGB', (ili9341.ILI9341_TFTHEIGHT, ili9341.ILI9341_TFTWIDTH), (255,255,255)) 

                draw2 = ImageDraw.Draw(image2)

                # print draw line
                draw2.line([(40,20),(200,20)],   fill = "RED",width = 5)
                draw2.line([(40,20),(40,200)],   fill = "RED",width = 5)
                draw2.line([(40,200),(200,200)], fill = "RED",width = 5)
                draw2.line([(200,20),(200,200)], fill = "RED",width = 5)

                # draw rectangle
                draw2.rectangle([(50,30),(190,70)],fill = "RED")
                    
                # draw text
                draw2.text((60, 30), u'It works !', font = font30, fill = "WHITE")
                draw2.text((85, 85), 'ILI9341 test', font = font15, fill = "RED")
                draw2.text((90, 110), 'fps: {0:.2f}'.format(fps), font = font15, fill = "RED")
            
                # gives a single float value
                draw2.text((90, 140), 'CPU: {0:.1f}%'.format(psutil.cpu_percent()), font = font15, fill = "RED")

                draw2.text((240, 90), '2', font = font60, fill = "BLACK")
                
                # Display some bubbles to stress the cpu
                for i in range(20):
                    Ball(draw,randint(0,320),randint(0,240),randint(5,25))

                img2 = np.asarray(image2)
                pix2 = np.zeros((240, 320,2), dtype = np.uint8)
                #RGB888 >> RGB565
                pix2[...,[0]] = np.add(np.bitwise_and(img2[...,[0]],0xF8),np.right_shift(img2[...,[1]],5))
                pix2[...,[1]] = np.add(np.bitwise_and(np.left_shift(img2[...,[1]],3),0xE0), np.right_shift(img2[...,[2]],3))



            with condition:
                condition.wait()
                nd_array = np.ndarray(shape=pix.shape, dtype = pix.dtype, buffer=shm.buf)
                nd_array[:] = pix[:]
                if self._args.display == 2:
                    nd_array2 = np.ndarray(shape=pix2.shape, dtype = pix2.dtype, buffer=shm2.buf)
                    nd_array2[:] = pix2[:]
                print ('Image ready for rendering')
            
            end_time = time.time()


    # A thread that consumes data 
    def renderer(self, condition):

        #shm_buffer = shared_memory.SharedMemory(name='sh_buffer')
        
        start_time = time.time()
        end_time   = 0

        while True: 

            fps = (1/(end_time - start_time))
            start_time = end_time

            for disp in self._disp:
                #disp.Render(shm_buffer=shm_buffer)
                #time.sleep(0.1)
                disp.Render()

            with condition:
                condition.notify()

            print("Rendering at {:.3f}".format(fps))
            end_time = time.time()




if __name__ == "__main__":
    app = MarcosST7789Test()
    app.main()






