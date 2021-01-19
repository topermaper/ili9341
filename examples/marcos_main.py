#!/usr/bin/python
# -*- coding:utf-8 -*-
import time
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
import time
from waveshare_2inch_LCD import ST7789
from PIL import Image,ImageDraw,ImageFont

logging.basicConfig(level=logging.INFO)


try:
    print ("2inch LCD Module")
    #disp = ST7789.ST7789([0, 1])
    disp = ST7789.ST7789([0])
    # Initialize library.
    disp.Init()


    font30 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 30)
    font15 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 15)

    start_time = time.time()
    end_time   = 0

    while(1):

        # Clear display.
        #disp.clear()

        fps = (1/(end_time - start_time))

        start_time = end_time

        image = Image.new('RGB', (disp.height,disp.width), (255,255,255)) 

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
        draw.text((50, 85), 'Waveshare Electronic ', font = font15, fill = "BLUE")
        draw.text((80, 120), '2.0inch LCD ', font = font15, fill = "BLUE")
        draw.text((90, 150), 'fps: {0:.2f}'.format(fps), font = font15, fill = "BLUE")
        
        #image=image.rotate(180) 
        disp.ShowImage(image = image, disp_id = 0)
    
        # read bmp file 
        #bmp = Image.open(os.path.join(picdir, 'LCD_2inch.bmp'))	
        #image.paste(bmp, (0,0))  
        #image=image.rotate(180)
        #disp.ShowImage(image, 0)

        end_time = time.time()




except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    exit()

