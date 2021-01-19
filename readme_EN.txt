/*****************************************************************************
* | File      	:   Readme_CN.txt
* | Author      :   Waveshare team
* | Function    :   Help with use
* | Info        :
*----------------
* |	This version:   V1.0
* | Date        :   2019-09-24
* | Info        :   Here is an English version of the documentation for your quick use.
******************************************************************************/
This file is to help you use this Demo.
A brief description of the use of this project is here:

1. Basic information:
This Demo has been verified on the Raspberry Pi 3B+;
This Demo has been verified using the 2inch LCD Module. 


2. Pin connection:
Pin connections can be viewed in \lib\waveshare_2inch_LCD\config.py and will be repeated here:
LCD         =>    Jetson Nano/RPI(BCM)
VCC         ->    3.3V
GND         ->    GND
DIN         ->    MOSI(10)
CLK         ->    SCLK(11)
CS          ->    8
DC          ->    25
RST         ->    27
BL          ->    18

3.Installation library
	sudo apt-get update
	sudo apt-get install python-pip
	sudo apt-get install python-pil
	sudo pip install RPi.GPIO
	sudo pip install spidev
	sudo apt-get install python-imaging

or
	sudo apt-get update
	sudo apt-get install python3-pip
	sudo apt-get install python3-pil
	sudo pip3 install RPi.GPIO
	sudo pip install spidev
	sudo apt-get install python-imaging

4. Basic use:
Test the program in the examples\ directory:
python2
    sudo python main.py

python3
    sudo python3 main.py