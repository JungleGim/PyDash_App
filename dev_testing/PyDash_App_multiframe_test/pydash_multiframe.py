"""
multi window test
------------
test script for setting up the basics of a multi window tk envinronment


TODO
-------------
-I think the "goto_frames", and "frame_switch" functions could be moved
    to the "SCRNdefines" file.
    ~Place them in the "scrn" struct. Unsure but may need a "scope" var passed to 
        them so when instancing the frames they're referenced correctly back to the
        master window. Maybe not since the frame (As instanced/stored in the dict) already
        has that information?

    
    ~after doing the above,  it would also subsume the need for updating the callback 
        function here in the main window (since it would exist in the instanced screen class 
        in that file already) which would make things much cleaner

-the "previous frame" variable only works with a single "back" its more of a "go to previous".
    update the functionality to a list of frames instead. Each time the user goes to "next" it'll 
    append to the list and then each time they go "back" can use the .pop() command to pull it off 
    the list and navigate one back. Would also have to track if its a "subscreen" or not. Don't need
    to add on the list if just navigating around the home screens. the "settings" Screen would be a
    great example of a sub-screen.

    for example. At the home screen on initial start it should be a blank list. navigating to different
    gauge windows should stay blank. Going into "settings" the list would be whatever window the user
    came from, say [Gauge0]. Then if theres another settings sub-window it would be 
    [Gauge0, settings] (when in the settings_sub1 window), etc. Then clicking the "back" button
    would pop "settings" off and return from "setttings_sub1" to "settings". The list then would be
    [Gauge0]. Clicking the "back" button again would pop "Gauge0" off and return from "settings" to
    "Gauge0".

    ~make a "goto_prev_frame" type function to handle this.
"""

#-----------------------------imports
from lib import *           #import files as defined in __init__ file of 'lib' directory

#-----------------------------support functions


#-----------------------------init functions


#-----------------------------class for root TK window
''' @brief: Root window
    @notes: nothing specifically is done here but is the main TK instance
'''
class RootWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        #REMINDER: if defining a new frame, it has to be added to this list
        frame_list = (Wndw_Gauge0, Wndw_Settings, Wndw_CANsniff)

        #----local vars
        self.container = tk.Frame(self)                     #define the master window as the container to hold the other frames
        self.container.pack(fill="both", expand=True)       #fill container to window size
        self.active_frame = tk.Frame()                      #current displayed frame
        self.prev_frame_indx = None                        #previous displayed frame index     
        
        #----set up app
        self.init_wndw()                                    #initialize window
        self.init_frames(frame_list)                        #initialize all the child frames used for the dash
        self.goto_frame(0)                                  #open default frame
    
    def init_wndw(self):
        #----window settings/info
        #self.overrideredirect(True)                         #override direct gets rid of the title bar (fullscreen)
        self.title("Electron Racing Dash")                  #title bar for testing
        disp_res = str(disp_xSz)+'x'+str(disp_ySz)+"+0+0"   #make string for geometry and placement
        self.geometry(disp_res)                             #window size and palcement
        self.maxsize(disp_xSz,disp_ySz)                     #set max size
        self.resizable(False,False)                         #fixed size

    def init_frames(self, frame_list):
        scrn.init_frames(frame_list, self.container, self)  #instance frames into control dictionary
        scrn.callback_func = self.frm_switch                #assign the frame switch function as the interrupt callback

    #NOTE: the defined functions here can be handled by the frames with master.[func]
    ''' @brief: Go To Frame
        @notes: switches the frame displayed in the root window 
    '''
    def goto_frame(self, new_frm_indx):
        new_frame = scrn.frames[new_frm_indx]       #get the frame based on the passed index
        self.prev_frame = scrn.get_frm_index(self.active_frame)         #save previous frame - for navigation of "back" button
        self.active_frame.pack_forget()                    #hide currrent frame
        self.active_frame = new_frame                      #update to the new frame        
        self.active_frame.pack(fill="both", expand=True)   #fill new frame to window size
    
    ''' @brief: Frame switch
        @notes: handles the displayed frame state and switches based on inputs
    '''
    def frm_switch(self, btn):
        indx_crnt_frame = scrn.get_frm_index(self.active_frame)    #get index of the current frame
        '''
        handle frame switching baseed on the pressed button. Have to do a bunch of else-if statements
        here because PyThOn MaTcH sTaTeMeNtS aRe MoRe PoWeRfUl but can't do something fucking
        simple like value matching. All because PEP-635 says that doing something like that doesn't
        "add any more value than a bunch of if/else statements". So. Fucking here we are.
        '''
        if btn == dash_btn1:
            if(indx_crnt_frame == 0):                       #if currently at the "first" frame
                self.goto_frame(len(scrn.frames)-1)      #wrap around to last frame
            else:
                self.goto_frame(indx_crnt_frame - 1)   #go to previous frame in list
        elif btn == dash_btn2:
            if(indx_crnt_frame == 1):
                self.goto_frame(self.prev_frame)        #go "back" to the previous frame
            else:
                self.goto_frame(1)                      #go to settings frame
        elif btn == dash_btn3:
            if(indx_crnt_frame == len(scrn.frames)-1):        #if currently at the "last" frame
                self.goto_frame(0)                     #wrap around to first frame
            else:
                self.goto_frame(indx_crnt_frame + 1)   #go to next frame in list
        elif btn == dash_btn4: pass #currently no action
        elif btn == dash_btn5: pass #currently no action
        elif btn == dash_btn6: pass #currently no action
        else:
            self.goto_frame(Wndw_Gauge0)    #default to showing the gauges0 window
#end of the root window          

#-----------------------------class for default gauge display
''' @brief: Gauge 0 frame
    @notes: frame is the primary gauge display
'''
class Wndw_Gauge0(tk.Frame):
    #-----main window initilization
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.frame_eles()           #place frame elements

    ''' @brief: frame elements
        @param: (none)
        @notes: function contains all the widgets/objects for the default
                window to be displayed
        @retrn: (none)
    '''
    def frame_eles(self):
        capt = drw_func.draw_txt_lbl(self, txt="Main Gauge Window", font=default_font_sm); capt.place(x=100,y=150, height=noPad_height_sm)
#end of main window class

#-----------------------------class for settings frame
''' @brief: Settings frame
    @notes: frame shows all the common configurable items like backlight PWM
'''
class Wndw_Settings(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.frame_eles()           #place frame elements

    ''' @brief: frame elements
        @param: (none)
        @notes: function contains all the widgets/objects for the default
                window to be displayed
        @retrn: (none)
    '''
    def frame_eles(self):
        capt = drw_func.draw_txt_lbl(self, txt="Settings Window", font=default_font_sm); capt.place(x=100,y=150, height=noPad_height_sm)
#end of the settings frame

#-----------------------------class for CAN sniffer frame
''' @brief: CAN sniffer frame
    @notes: frame is a list box with all the RX'd CAN data 
'''
class Wndw_CANsniff(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.frame_eles()           #place frame elements

    ''' @brief: frame elements
        @param: (none)
        @notes: function contains all the widgets/objects for the default
                window to be displayed
        @retrn: (none)
    '''
    def frame_eles(self):
        capt = drw_func.draw_txt_lbl(self, txt="CAN Sniffer Window", font=default_font_sm); capt.place(x=100,y=150, height=noPad_height_sm)
#end of the CAN sniffer frame

#-----------------------------main loop
if __name__ == "__main__":
    app = RootWindow()
    app.mainloop()
