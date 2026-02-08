"""
File:       MainWindow.py
Function:   This file contains the main application window called when running the application.
"""

from lib import *

class wndw_Main(tk.Tk):
    """Primary tkinter window class"""
    def __init__(self):
        tk.Tk.__init__(self)

        if check_new_config() == True: load_new_config(self)    #if a new config archive exists, load into filesystem
        self.init_framework()                                   #define display framework

        if check_config_exists() == True:                       #if the config file exists
            self.init_dash()                                        #initialize core variables
            self.instance_cfg()                                     #and attempt to load config
        else:                                                   #else update error dict
            err_msg = [create_err_msg('Core','CFG','Config XML file not found - check SD card')]
            self.upd_errors(err_msg)

        if len(self.errors) > 0:            #if errors are present at this point, do not start normal operation
            self.dash_ctl.goto_page(page_menu_errorsMain(self))     #display errors view
            self.display_refresh_loop()
        else:                               #else, ok to build dash pages and start operation
            self.start_dash()

        #self.dash_ctl.goto_page(page_fullscreen_text(self.prnt_frame, 'test page'))        #display test page for debug and tracing

    def init_framework(self):
        """function sets up the main display framework and elements needed for any operation"""
        #----window settings/info
        if sys_inDEBUG == False: self.overrideredirect(True)        #override direct gets rid of the title bar (fullscreen)
        self.title("PyDash")                                        #title bar (only displayed in testing env)
        disp_res = str(sys_disp_xSz)+'x'+str(sys_disp_ySz)+"+0+0"   #make string for geometry and placement
        self.geometry(disp_res)                                     #window size and palcement
        self.maxsize(sys_disp_xSz,sys_disp_ySz)                     #set max size
        self.resizable(False,False)                                 #fixed size

        #----display frame
        self.prnt_frame = tk.Frame(self)                    #define the primary frame that everything is contained in
        self.prnt_frame.pack(fill="both", expand=True)      #place and fill frame to window size
        self.dash_ctl = dash_control(self)                  #instance the "dash_control" class that handles current state, etc.

        #----misc core properties
        self.errors = []                                    #list for tracking any errors encountered
    
    def init_dash(self):
        """function defines and instances any variables required for normal operation"""
        self.dash_settings = dash_config()              #var for the user control settings (like back-light brightness, etc.)
        self.dash_CAN = CAN_core(self)                  #var for the CANbus control
        self.dash_theme = dash_theme_user()             #var for theme used in user pages (colors, fonts, etc)
        self.dash_pages_user = {}                       #var of the user configured "gauge" type pages
        self.dash_pages_menu = {}                       #var of the non-user configured "menu_pages" like settings, CAN sniffer, etc.

    def instance_cfg(self):
        """function builds menu pages and loads dash configuration"""
        menuPages_instMain(self)                #populate the constant menu pages
        dashCFG_load(self)                      #populate the various classes with the dash_config.xml file
        dashCFG_ErrChk(self)                    #and check for any errors

    def start_dash(self):
        """function builds user dash pages and starts normal dash operation"""
        self.dash_ctl.dash_start_HW_ops()       #start any hardware functions
        self.dash_ctl.dash_buildPages()         #build the various dash pages
        self.dash_ctl.page_ele_CANref_init()    #set page element triggers for CAN data
        self.dash_ctl.goto_user_FirstPage()     #go to first user page
        self.display_refresh_loop()             #enter main refresh loop
    
    def display_refresh_loop(self):
        """function updates the current displayed page, if needed. Note that not all pages will have this
        functionality, primarily is used in menu windows. Dash pages should function based on event triggers
        and not need this processing."""

        if callable(getattr(self.dash_ctl.active_page_ref, 'upd_page',None)):   #if current page has an update routine
            self.dash_ctl.active_page_ref.upd_page()                            #then call it

        self.after(sys_refresh_rate, self.display_refresh_loop) #continue to update every interval
    
    def upd_errors(self, err_msgs):
        """function updates the global error tracking dict with the passed values"""
        for e in err_msgs:
            self.errors.append(e)
    
    def clear_errs(self):
        """function clears any 'clearable' errors in the error tracking dict. Note that any
        critical system-level errors are non-clearable"""
        for k, v in self.errors.items():            #loop through all errors
            if v.clr == True: self.errors.pop(k)    #if its clearable, then remove from dict

#-----------------------------main loop
if __name__ == "__main__":
    app = wndw_Main()
    app.mainloop()