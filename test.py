#!/usr/bin/python
# -*- coding:utf-8 -*-

import time
import sys
import os
import argparse
import collections
import logging
import time
import psutil
import numpy as np


picdir = os.path.join(os.getcwd(), 'pic')
libdir = os.path.join(os.getcwd(), 'lib')

if os.path.exists(libdir):
    sys.path.append(libdir)

from LCD import frontpanel
from PIL import Image, ImageDraw, ImageFont
from statistics import mean

from lib.utils.ball import Ball
from random import randint


class ILI9341Test:

    def initLCD(self):

        # Initialize front panel
        self._fp = frontpanel.Frontpanel(['ILI9341'], spi_speed=self._args.spi_clock)


    def parseArgs(self):
        parser = argparse.ArgumentParser(description='Drives 1 or 2 ILI9341 TFT screens over SPI using a RP3B+')
        parser.add_argument('--clock', dest='spi_clock', type=int, default=32000000, help='SPI clock speed Hz')
        parser.add_argument('--bubbles', dest='bubbles', type=int, default=0, help='Amount of bubbles per frames. Bubbles are used to stress to CPU during testing.')
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




    # Returns pixel array in format RGB565, ready for rendering
    def drawDisplay1(self):
        self._cpu.append(psutil.cpu_percent())

        image = Image.new('RGB', (320, 240), (255,255,255)) 

        draw = ImageDraw.Draw(image)

        # print draw line
        draw.line([(40,20),(200,20)],   fill = "BLUE",width = 5)
        draw.line([(40,20),(40,200)],   fill = "BLUE",width = 5)
        draw.line([(40,200),(200,200)], fill = "BLUE",width = 5)
        draw.line([(200,20),(200,200)], fill = "BLUE",width = 5)

        # draw rectangle
        draw.rectangle([(50,30),(190,65)],fill = "BLUE")
            
        # draw text
        draw.text((60, 29), 'It works !', font = self._fonts['font30'], fill = "WHITE")
        draw.text((65, 85), 'Temperature: {0:.1f}°C'.format(psutil.sensors_temperatures()['cpu_thermal'][0].current), font = self._fonts['font12'], fill = "BLUE")
        draw.text((75, 113), 'ILI9341@{0:.1f}fps'.format(self.fps), font = self._fonts['font12'], fill = "BLUE")
        draw.text((75, 140), 'CPU usage: {}%'.format(int(mean(self._cpu))), font = self._fonts['font12'], fill = "BLUE")
        #draw.text((65, 170), 'CPU clock: {0}MHz'.format(int(psutil.cpu_freq().current)), font = self._fonts['font12'], fill = "BLUE")
            
        draw.text((240, 90), '1', font = self._fonts['font30'], fill = "BLACK")
        
        # Display some bubbles to stress the cpu
        for i in range(self._args.bubbles):
            Ball(draw,randint(0,320),randint(0,240),randint(5,25))

        return image


    def loadFonts(self):
        self._fonts = {}
        self._fonts['font60'] = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 60)
        self._fonts['font30'] = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 30)
        self._fonts['font12'] = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 12)

 
    def main(self):

        self.parseArgs()
        self.initLCD()

        # Load fonts
        self.loadFonts()

        start_time = time.time()
        end_time   = 0

        self._cpu = collections.deque([0], maxlen=20)

        while True: 

            self.fps = (1/(end_time - start_time))

            start_time = end_time

            image = self.drawDisplay1()
            self._fp.display(image=image, disp_id=0)

            end_time = time.time()



if __name__ == "__main__":
    app = ILI9341Test()
    app.main()

