#screen defines portion of the pydash

#-----------------------------Library Inputs-----------------------------
import RPi.GPIO as GPIO 
GPIO.setmode(GPIO.BCM)              #set GPIO to broadcom specific pin numbers

#-------display update params
refresh_rate = 67       #approximately 15 Hz in miliseconds
disp_xSz = 1024         #display x-dim size
disp_ySz = 600          #display y-dim size
disp_xc = disp_xSz/2    #display center, x-dim
disp_yc = disp_ySz/2    #display center, y-dim

#-------GPIO / Button inputs
"""
        button layout
        
        1   |               |   4
            |               |
        2   |    screen     |   5
            |               |
        3   |               |   6

        1- Page up
        2- Settings
        3- Page Down
        4- Scroll up
        5- Enter/select
        6- Scroll Down
"""
dash_btn1 = 24
dash_btn2 = 19
dash_btn3 = 6
dash_btn4 = 2
dash_btn5 = 4
dash_btn6 = 27

# debounce time set to 200ms, should be ok with external debounce network but can adjust if needed
btn_bouncetime = 200                #button debounce time in ms

# PCB has external debounce and pullup, so no need to use "pullup" param
# for testing on devboard using pull_up_down=GPIO.PUD_UP
GPIO.setup(dash_btn1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dash_btn2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dash_btn3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dash_btn4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dash_btn5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dash_btn6, GPIO.IN, pull_up_down=GPIO.PUD_UP) 

#-----------------------------classes-----------------------------
#class for screen control
class screen_info:
    def __init__(self):
        self.frames = {}                    #dictionary to store all defined frames
        self.callback_func = None           #button interrupt callback     

    ''' @brief:     return frame index
        @notes:     the {key:value pair} is a {numerical_index : frame} pair
        @return:    Index of the target frame
                    if the target frame isn't in the list then return None
    '''
    def get_frm_index(self, tgt_frm):
        for key, val in self.frames.items():
            if(val == tgt_frm): return key
        return None

    #call assigned
    def interupt_callback(self, GPIO_ch):
        self.callback_func(GPIO_ch)             #send pressed button to callback
        pass

    ''' @brief:     initialize frames
        @notes:     instances the frames and creates a dictionary to store them.
                    The passed parent and controller give refernce to the environment
                    they should appear in. the {key:value pair} is a 
                    {numerical_index : frame} pair.

                    Numerical index was chosen to make navigating (by increment/decrement)
                    easier.
        @return:    (none)
    '''
    def init_frames(self, frm_list, frm_parent, frm_controller):
        for F in frm_list:      #loop through the list of passed frames           
            #self.frames.update({len(self.frames) : F})
            tmp_frm = F(parent=frm_parent, controller=frm_controller)   #temp instance the frame and assign parent/controller
            self.frames.update({len(self.frames) : tmp_frm})            #add to dictionary of frames

#------------Window or navigation specific functions--------------
scrn = screen_info()        #instance screen info at max brightness

#----attach button interrupts
GPIO.add_event_detect(dash_btn1, GPIO.FALLING, callback=scrn.interupt_callback, bouncetime=btn_bouncetime)
GPIO.add_event_detect(dash_btn2, GPIO.FALLING, callback=scrn.interupt_callback, bouncetime=btn_bouncetime)
GPIO.add_event_detect(dash_btn3, GPIO.FALLING, callback=scrn.interupt_callback, bouncetime=btn_bouncetime)
GPIO.add_event_detect(dash_btn4, GPIO.FALLING, callback=scrn.interupt_callback, bouncetime=btn_bouncetime)
GPIO.add_event_detect(dash_btn5, GPIO.FALLING, callback=scrn.interupt_callback, bouncetime=btn_bouncetime)
GPIO.add_event_detect(dash_btn6, GPIO.FALLING, callback=scrn.interupt_callback, bouncetime=btn_bouncetime)
