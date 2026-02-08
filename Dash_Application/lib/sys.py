"""
File:       sys.py
Function:   This file handles any common "system wide" (hence the name "sys") common definitions or includes
            that are used in nearly all files. Good examples of this include common font definitions for
            the application, verision information, constants used, any any other (for lack of a better term)
            "global" information that's common to the application.
"""
import tkinter as tk
import os
import pathlib
import can
import time
import shutil
import xml.etree.ElementTree as ET
import re as rgx
from tkinter import font as tkFont
import copy
from ast import literal_eval
from tkinter.ttk import Treeview as tkTree

#---system state
sys_inDEBUG = False    #variable to handle debug parts of code 
if 'TERM_PROGRAM' in os.environ.keys() and os.environ['TERM_PROGRAM'] == 'vscode': sys_inDEBUG = True
sys_start_time_ms = round(time.time()*1000)            #set start ms for error handling

#---library handling for debug mode vs production mode
#import RPi.GPIO as GPIO    #needed for the GPI buttons on the CM4
GPIO = None

#----constant file paths and other common directories
#root_dir = '/mnt/uSD/'                                 #root dir used in final production
sys_root_dir = str(pathlib.Path(__file__).parents[2]) + '\development\dev_root_dir\\'       #temp root dir used in development
sys_config_dir = sys_root_dir + 'PyDash_Config\\'       #directory of configuration
sys_config_archive = sys_root_dir + 'PyDash_Config.zip' #path for new config archive
sys_cfg_Images_dir = sys_config_dir + 'images\\'       #path for any images used in config
sys_config_file = sys_config_dir + 'PyDash_Config.xml'  #path of dash config file
sys_log_dir = sys_root_dir + 'data_logs'                #directory for storing datalogs

#----physical hardware constants
sys_disp_xSz = 1024             #screen x-dim size
sys_disp_ySz = 600              #screen y-dim size
sys_disp_xc = sys_disp_xSz/2    #display center, x-dim
sys_disp_yc = sys_disp_ySz/2    #display center, y-dim
sys_refresh_rate = 67           #approx 16Hz in ms

#-------GPIO / Button inputs
"""
        button layout
        
        1   |               |   4
            |               |
        2   |    screen     |   5
            |               |
        3   |               |   6
"""
#----rPi GPIO broadcom button numbers
sys_dash_btn1 = 24      #also numpad 7 for debug
sys_dash_btn2 = 19      #also numpad 4 for debug
sys_dash_btn3 = 6       #also numpad 1 for debug
sys_dash_btn4 = 2       #also numpad 9 for debug
sys_dash_btn5 = 4       #also numpad 6 for debug
sys_dash_btn6 = 27      #also numpad 3 for debug

# debounce time set to 200ms, should be ok with external debounce network but can adjust if needed
sys_btn_bouncetime = 200            #button debounce time in ms

#----CAN constants
sys_HW_chnl = 'can0'
sys_CAN_baud = '500000'
sys_CAN_intrfce = 'socketcan'
sys_default_PID = 0xA0              #default self PID for the dash
sys_SFF_mask = 0x7FF                #message filter mask - compare all bits - standard frame format (SFF)
sys_EFF_mask = 0x1FFFFFFF           #message filter mask - compare all bits - extended frame format (EFF)
sys_RTR_freq_dflt = 5               #default RTR frequency in seconds - also used for channel timeouts (why it is very long)

#----misc constants
sys_pad_margin = 2                  #padding margin of the BG pad object, in pixels, larger than its parent
sys_dflt_pad_radius = 20            #default radius of the background pad polygon
sys_dat_sigdig = 0                  #default sigdigs for data labels

#------------------------------------Menu theme------------------------------------
menuTheme_font_tiny = ('Sui Generis', 18)
menuTheme_font_small = ('Sui Generis', 30)
menuTheme_font_medium = ('Sui Generis', 50)
menuTheme_font_large = ('Sui Generis', 72)

menuTheme_color_TextFG = '#02C6D0'
menuTheme_color_BG = '#636363'
menuTheme_color_listboxBG = "#7E7E7E"