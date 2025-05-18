'''
py dash defines
-----------------------------------
defines file to clean up the main file a bit.
'''

#label types
lbl_type_data = 'data'          #data label is a data type, means it will display a numerical value
lbl_type_ind = 'ind'            #data label is an indicator type, means it is an on/off toggle

#configurable data values/points
max_rpm = 7500      #maximum RPM to display
fan_on = 200        #fan on temperature
fan_off = 190       #fan off temperature
lobm_on = 0xFA      #headlight on signal
hibm_on = 0xFA      #highbeam on signal

#working_dir = os.getcwd()  #this doesn't work always because it depends on the directory it was executed from
                            #not nesc the actual py script directory

#working_dir = "C:/Users/jlang/Desktop/py_dash_r0_20250505" #windows dev dir
#working_dir = "/root/py_dash"                              #deployment dir
working_dir = "/home/pi/Desktop/py_dash_r1a_20250517"		#test pi development
filepath_bg_img =       "/images/bckgrnd_image.png"
filepath_bg_img_RPM =   "/images/bckgrnd_image_RPM.png"     #background image with RPM bar-graph cutout
filepath_light_lo =     "/images/headlight_lo.png"
filepath_light_hi =     "/images/headlight_hi.png"

#-----------------------------classes-----------------------------
#class for settings
class dash_settings:
    def __init__(self, **kwargs):
        #do some default settings via kwargs
        lite_pwm = kwargs.setdefault("lite_pwm", 100)       #full bright
        CAN_PID = kwargs.setdefault("CAN_PID", 0x9A)        #self CAN address

        self.setngs = kwargs                                #assign all KWARGS to a settings dict

dash_config = dash_settings()                               #instance settings using default values
