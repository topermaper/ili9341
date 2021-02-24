import json
from PIL import Image, ImageDraw, ImageFont
import logging

import os
import sys

# Path is relative to the folder where the script runs
cwd = os.getcwd()
os.getcwd()
picdir  = os.path.join(os.getcwd(),'pic')


class MenuLoader():

    def loadMenu(self,path):

        with open(path, 'r') as f:
            data = json.load(f)
            
        logging.debug(data)

        main_menu = Menu(
            width    = data['size']['width'],
            height   = data['size']['height'],
            bg_color = data['bg_color'])

        title = data['title']

        main_menu.addTitle(
            origin = (title['origin'][0], title['origin'][1]),
            text   = title['text'],
            fill   = 'YELLOW'
        )

        for ob in data['objects']:
            
            if ob.get('type') == 'menu':
                origin = (ob['origin'][0], ob['origin'][1])

                main_menu.addMenu(
                    parent = main_menu,
                    menu = Menu(
                        width    = ob['size']['width'],
                        height   = ob['size']['height'],
                        bg_color = ob['bg_color']
                    ),
                    origin = origin
                )

            else:
                logging.error('Type not supported or not specified. Error loading menu object: {}'.format(ob))

        return main_menu



class Menu(object):
    
    def __init__(self,width,height,bg_color):
        self._parent = None
        self._children = []
        self._width = width
        self._height = height

        self._image = Image.new('RGB', (width,height), bg_color)
        self._draw = ImageDraw.Draw(self._image)

        self.loadFonts()


    def addTitle(self, origin, text, fill):
        font = self._fonts['font15']
        self._draw.text(origin, text, font = font , fill = fill)


    def addArea(self,width,heigh,bg_color):
        self._children.append(Area(width,height))


    def addMenu(self,parent,menu,origin=(0,0)):
        self._children.append({'origin': origin, 'object': menu})


    # Recursive call
    def getImage(self):
        for ob in self._children:
            image = ob['object'].getImage()
            self._image.paste(image, box=ob['origin'])

        return self._image


    def loadFonts(self):

        self._fonts = {}

        my_font_path = os.path.join(picdir, 'Font.ttc')
        print('my font : {}'.format(my_font_path))

        self._fonts['font30'] = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 30)
        self._fonts['font15'] = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 15)



class Area(object):

    def __init__(self,width,height,bg_color):
        self._children = []
        self._width = width
        self._height = height

        self._image = Image.new('RGB', (width,height), bg_color)

        self._draw = ImageDraw.Draw(self._image)


    def addWidget(self,origin,width,height):
        self._children.append(Widget(width,height))



class Widget(object):

    def __init__(self,width,height,bg_color):
        self._width = width
        self._height = height

        self._image = Image.new('RGB', (width,height), bg_color)

        self._draw = ImageDraw.Draw(self._image)


    def addText(self,origin,text,font,fill):
        draw.text(origin = origin, text = text, font = font , fill = fill)
    