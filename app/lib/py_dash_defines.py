'''
py dash defines
-----------------------------------
defines file to clean up the main file a bit.
'''

#library imports
import tkinter as tk                    #tkinter include for UI
import can                              #import python-can lib
import os                               #command line operating system include
import time
from PIL import Image, ImageTk          #Pillow required for place/resize image
#import datetime as dt

#label types
lbl_type_data = 'data'          #data label is a data type, means it will display a numerical value
lbl_type_ind = 'ind'            #data label is an indicator type, means it is an on/off toggle

#display data indecies for different classes
indx_rpm = 0
indx_ect = 1
indx_o2 = 2
indx_oilp = 3
indx_map = 4
indx_lobm = 5
indx_hibm = 6

#configurable data values/points
max_rpm = 5000      #maximum RPM to display
fan_on = 200        #fan on temperature
fan_off = 190       #fan off temperature
lobm_on = 0xFA      #headlight on signal
hibm_on = 0xFA      #highbeam on signal

#display update params
refresh_rate = 67       #approximately 15 Hz in miliseconds
disp_xSz = 1024         #display x-dim size
disp_ySz = 600          #display y-dim size
disp_xc = disp_xSz/2    #display center, x-dim
disp_yc = disp_ySz/2    #display center, y-dim

#key values/defines
bg_color =              '#636363'   #dark grey-ish color for background
lbl_fg_color =          '#00FF00'   #normal label foreground color
lbl_otln_color =        '#00FF00'   #normal outline color
ind_on_color =          '#00FF00'   #indicator "on" color
ind_off_color =         bg_color    #indicator "off" color
alert_lbl_fg_color =    '#000000'   #label foreground color when alterting an out of bounds value
warn_color =            '#FFFF00'   #yellow color for warning
dngr_color =            '#FF0000'   #red color for danger/error

default_font_sz =       45                              #default font size (pt not px)
small_font_sz =         36                              #small font size
default_font =          ("Helvetica",default_font_sz, "bold")  #default font and size
default_font_sm =       ("Helvetica",small_font_sz, "bold")    #default font and size
noPad_height =          default_font_sz*16/12-10        #label height with no vertical padding
noPad_height_sm =       small_font_sz*16/12-6           #label height with no vertical padding

#working_dir = os.getcwd()  #this doesn't work always because it depends on the directory it was executed from
                            #not nesc the actual py script directory
#working_dir = "C:/Users/jlang/Desktop/py_dash_r0_20240405"
working_dir = "/root/py_dash"
filepath_bg_img =       "/images/bckgrnd_image.png"
filepath_light_lo =     "/images/headlight_lo.png"
filepath_light_hi =     "/images/headlight_hi.png"