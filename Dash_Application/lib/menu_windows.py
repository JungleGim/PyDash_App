"""
File:       menu_windows.py
Function:   This file contains any of the window classes for constant windows that are non-user
            configurable (config window, CAN sniffer, etc.)
"""

from .com_defs import page_template
from .com_defs import pageTypes_dict_menu, str2dec
from .sys import *

#----------------------------------methods----------------------------------
def menuPages_instMain(master_ref):
    """Function builds the various menu pages that are used for the dash and updates the main
    menu pages dict the values
    
    :param master_ref: reference back to the main/master window
    :type master_ref: `tk.window` ref
    """
    #--update the menu pages dict to contain all the defined menu pages
    master_ref.dash_pages_menu.update({pageTypes_dict_menu['main_settings']:page_menu_settingsMain(master_ref),
                                       pageTypes_dict_menu['error']:page_menu_errorsMain(master_ref),
                                       pageTypes_dict_menu['CAN_sniffer']:page_menu_CANsniffer(master_ref),})
    
    #--assign the default button functions
    for page in master_ref.dash_pages_menu.values():
        page.btn_func = master_ref.dash_ctl.dflt_menu_pg_btns   #assign default button calls
        page.assign_btn_calls()                                 #assign page-specific button calls``

#----------------------------------classes----------------------------------
class menu_page_template(tk.Frame):
    def __init__(self, master_ref):
        """class is the basic page template used as a starting point for menu pages
        
        :param master_ref: reference back to the main/master window
        :type master_ref: `tk.window` ref
        """
        super().__init__(master_ref.prnt_frame)

        #----------------refs
        self.master_ref = master_ref    #ref back to master window
        self.btn_func = []              #list to store the button functions of the current page

        #----------------window framework
        #--core page frame
        self.frm_bg_clr = menuTheme_color_BG
        self.wndw_frm = tk.Frame(self, bg=self.frm_bg_clr,
                                 borderwidth=0,highlightthickness=0)    #make the window frame to hold everything
        self.wndw_frm.grid(row=0, column=0, sticky=tk.NSEW)             #expand to fill window     
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.wndw_frm.grid_columnconfigure(0, weight=1)                     #expand whole column
        self.wndw_frm.grid_rowconfigure(1, weight=1)                        #alt frame expands whole height

        #--contents frame for actual display items
        self.alt_frm = tk.Frame(self.wndw_frm, bg=self.frm_bg_clr,
                                 borderwidth=0,highlightthickness=0)        #alternate frame to hold page contents
        self.alt_frm.grid(row=1, column=0, pady=(0,25), sticky=tk.NSEW)
        self.alt_frm.grid_columnconfigure(1, weight=1)                      #assign extra space to error view
        self.alt_frm.grid_rowconfigure(0, weight=1)                         #fill complete height

        #--left button frame for alignment/justification of button labels
        self.lt_btn_frm = tk.Frame(self.alt_frm,bg=self.frm_bg_clr, borderwidth=0,highlightthickness=0)  #left buttons frame
        self.lt_btn_frm.grid(row=0, column=0, padx=10, pady=(0,50), sticky=tk.NS)
        self.lt_btn_frm.grid_rowconfigure(0, weight=1)                                                   #fill complete height

        #--right button frame for alignment/justification of button labels
        self.rt_btn_frm = tk.Frame(self.alt_frm,bg=self.frm_bg_clr, borderwidth=0,highlightthickness=0)  #right buttons frame
        self.rt_btn_frm.grid(row=0, column=2, padx=10, pady=(0,50), sticky=tk.NS)
        self.rt_btn_frm.grid_rowconfigure(0, weight=1)                                                   #fill complete height

        #--default navigation buttons
        btn2_lbl = tk.Label(self.lt_btn_frm, text='Exit', font=menuTheme_font_tiny,
                            fg=menuTheme_color_TextFG, bg=self.frm_bg_clr, justify=tk.LEFT)
        btn2_lbl.grid(row=0, column=0, sticky=tk.W)
        btn4_lbl = tk.Label(self.rt_btn_frm, text='Prv Pg', font=menuTheme_font_tiny,
                            fg=menuTheme_color_TextFG, bg=self.frm_bg_clr, justify=tk.RIGHT)
        btn4_lbl.grid(row=0, column=0, sticky=tk.NE)
        btn6_lbl = tk.Label(self.rt_btn_frm, text='Nxt Pg', font=menuTheme_font_tiny,
                            fg=menuTheme_color_TextFG, bg=self.frm_bg_clr, justify=tk.RIGHT)
        btn6_lbl.grid(row=0, column=0, sticky=tk.SE)   

class page_menu_settingsMain(menu_page_template):
    def __init__(self, master_ref):
        """class is for the main settings menu that displays all the various user configurable settings
        
        :param master_ref: reference back to the main/master window
        :type master_ref: `tk.window` ref
        """
        super().__init__(master_ref)
        self.name = pageTypes_dict_menu['main_settings']
        self.init_window()              #build main window elements
    
    def init_window(self):
        """function builds the main window elements"""
        self.wndw_title_lbl = tk.Label(self.wndw_frm, text='Settings Menu',
                                       font=menuTheme_font_small,
                                       fg=menuTheme_color_TextFG,
                                       bg=self.frm_bg_clr,
                                       padx=10, pady=10, justify=tk.LEFT)   #create menu label
        self.wndw_title_lbl.grid(row=0,column=0)

        #--listbox to display values
        self.data_listbox = tk.Listbox(self.alt_frm, font=menuTheme_font_tiny,
                                       fg=menuTheme_color_TextFG, bg=menuTheme_color_listboxBG) #create listbox to display errors
        self.data_listbox.grid(row=0, column=1, sticky=tk.NSEW)

        #--button labels
        #btn1_lbl=N/A
        #btn2 = default exit menu
        #btn3_lbl=N/A
        #btn4 = default previous page
        #btn5_lbl=N/A
        #btn6 = default next page
    
    def assign_btn_calls(self):
        """function assigns any page-specific button calls/functions"""

    def upd_page(self):
        """function updates the current page with any changed values"""
        #--update listbox
        self.data_listbox.delete(0, tk.END)                     #clear listbox
        for att, val in self.master_ref.dash_settings.__dict__.items():    #loop through settings
            string = f"{att}: {val}"                             #make the display string
            self.data_listbox.insert(tk.END, string)            #insert display string


class page_menu_CANsniffer(menu_page_template):
    def __init__(self, master_ref):
        """class is for the CAN sniffer window that displays any/all current CAN data
        
        :param master_ref: reference back to the main/master window
        :type master_ref: `tk.window` ref
        """
        super().__init__(master_ref)
        self.name = pageTypes_dict_menu['CAN_sniffer']
        self.init_window()              #build main window elements
    
    def init_window(self):
        """function builds the main window elements"""
        #--menu label
        self.wndw_title_lbl = tk.Label(self.wndw_frm, text='CAN sniffer Menu',
                                       font=menuTheme_font_small,
                                       fg=menuTheme_color_TextFG,
                                       bg=self.frm_bg_clr,
                                       padx=10, pady=10, justify=tk.LEFT)   #create menu label
        self.wndw_title_lbl.grid(row=0,column=0)   

        #--listbox to display values
        self.data_listbox = tk.Listbox(self.alt_frm, font=menuTheme_font_tiny,
                                       fg=menuTheme_color_TextFG, bg=menuTheme_color_listboxBG) #create listbox to display errors
        self.data_listbox.grid(row=0, column=1, sticky=tk.NSEW)

        #--button labels
        btn1_lbl = tk.Label(self.lt_btn_frm, text='Reset', font=menuTheme_font_tiny,
                            fg=menuTheme_color_TextFG, bg=self.frm_bg_clr, justify=tk.LEFT)
        btn1_lbl.grid(row=0, column=0, sticky=tk.NW)
        #btn2 = default exit menu

        self.var_filtr_btn_txt = tk.StringVar(value='RX Fltr\n')
        btn3_lbl = tk.Label(self.lt_btn_frm, textvariable=self.var_filtr_btn_txt, font=menuTheme_font_tiny,
                            fg=menuTheme_color_TextFG, bg=self.frm_bg_clr, justify=tk.LEFT)
        btn3_lbl.grid(row=0, column=0, sticky=tk.SW)      

        #btn4 = default previous page
        #btn5_lbl=N/A
        #btn6 = default next page

        #--set initial state of the filter variable
        if self.master_ref.dash_CAN.RX_filter_en == True: self.var_filtr_btn_txt.set('RX Fltr\nOn')
        else: self.var_filtr_btn_txt.set('RX Fltr\nOff')
    
    def assign_btn_calls(self):
        """function assigns any page-specific button calls/functions"""
        self.btn_func[0] = self.master_ref.dash_CAN.CAN_rx_data_clear   #assign the clear CANrx dict call
        self.btn_func[2] = self.toggle_CANrx_filter                     #assign the toggle filter call

    def toggle_CANrx_filter(self):
        """function toggles the CANrx filter state. WARNING: this persists outside of settings menu"""
        if self.master_ref.dash_CAN.RX_filter_en == True:
            self.master_ref.dash_CAN.CAN_RXfilter_off()
            self.var_filtr_btn_txt.set('RX Fltr\nOff')
        else:
            self.master_ref.dash_CAN.CAN_RXfilter_on()
            self.var_filtr_btn_txt.set('RX Fltr\nOn')

    def upd_page(self):
        """function updates the current page with any changed values"""
        #--update listbox
        self.data_listbox.delete(0, tk.END)                         #clear listbox
        for pid, dat_frm in self.master_ref.dash_CAN.RX_allData.items():    #loop through raw data
            #format should be: 0xPID] - [MSB]...[LSB]
            pid_str = f"0x{pid:03X}"                                                #format the PID value
            dat_str = '[{}]'.format(', '.join(f"0x{val:02X}" for val in dat_frm))   #format data string
            string = pid_str + ' - ' + dat_str                      #make the display string
            self.data_listbox.insert(tk.END, string)                #insert display string
        
class page_menu_errorsMain(menu_page_template):
    def __init__(self, master_ref):
        """class is for the main errors window that displays any/all current errors
        
        :param master_ref: reference back to the main/master window
        :type master_ref: `tk.window` ref
        """
        super().__init__(master_ref)
        self.name = pageTypes_dict_menu['error']
        self.init_window()              #build main window elements
    
    def init_window(self):
        """function builds the main window elements"""
        #--menu label
        wndw_title_lbl = tk.Label(self.wndw_frm, text='Errors Menu',
                                  font=menuTheme_font_small,
                                  fg=menuTheme_color_TextFG,
                                  bg=self.frm_bg_clr,
                                  padx=10, pady=10, justify=tk.LEFT)
        wndw_title_lbl.grid(row=0,column=0)

        #--listbox to display values
        self.data_listbox = tk.Listbox(self.alt_frm, font=menuTheme_font_tiny,
                                       fg=menuTheme_color_TextFG, bg=menuTheme_color_listboxBG) #create listbox to display errors
        self.data_listbox.grid(row=0, column=1, sticky=tk.NSEW)

        #--button labels
        btn1_lbl = tk.Label(self.lt_btn_frm, text='Clear', font=menuTheme_font_tiny,
                            fg=menuTheme_color_TextFG, bg=self.frm_bg_clr, justify=tk.LEFT)
        btn1_lbl.grid(row=0, column=0, sticky=tk.NW)
        #btn2 = default exit menu
        #btn3_lbl=N/A
        #btn4 = default previous page
        #btn5_lbl=N/A
        #btn6 = default next page
    
    def assign_btn_calls(self):
        """function assigns any page-specific button calls/functions"""
        self.btn_func[0] = self.master_ref.clear_errs           #assign the clear errors function call

    def upd_page(self):
        """function updates the current page with any changed values"""
        #--update listbox
        self.data_listbox.delete(0, tk.END)                     #clear listbox
        for e in self.master_ref.errors:                        #cycle through entries in error dict
            string = f"[{e.time}] {e.sys}-{e.mod} : {e.msg}"    #make the display string
            self.data_listbox.insert(tk.END, string)            #insert display string