"""
File:       dash_control.py
Function:   This file contains any of the classes and methods related to general control
            and functions of the dash, including I/O interations, etc.
"""
from .sys import *
from .com_defs import GPIOconvert_dict, EleTypes_dict

class dash_control:
    def __init__(self, master):
        self.master_ref = master            #master window ref
        self.prnt_frm = master.prnt_frame   #primary frame that all canvas objects are displayed on
        self.active_page_ref = None         #reference to the current active page being displayed
        self.menu_prev_pages = []           #tuple to track previous nested menu pages

        self.usrBtns_init()                 #initialize user input controls - Needed immediately for menus / error navigation

        #---default user menu page button actions
        self.dflt_user_pg_btns = [None,
                                  self.goto_menu_FirstPage,
                                  None,
                                  self.goto_user_PrevPage,
                                  None,
                                  self.goto_user_NextPage]
        
        #---default menu page button actions
        self.dflt_menu_pg_btns = [None,
                                  self.goto_menu_BackPage,
                                  None,
                                  self.goto_menu_PrevPage,
                                  None,
                                  self.goto_menu_NextPage]

    def get_page_indx_user(self, pg_name):
        """function gets the order index of the passed page name
        
        :param pg_name: the reference name of the page to display
        :type pg_name: `string` that matches a main `dash_page_user` instance key value
        :returns: main `dash_page_user` dict instance index
        :rtype: int
        """
        return list(self.master_ref.dash_pages_user).index(pg_name)
    
    def get_page_name_user(self, pg_indx):
        """function gets the user page name at the passed index
        
        :param pg_indx: an index number to check against the main `dash_page_user` instance
        :type pg_indx: `int`
        :returns: key value from main `dash_page_user` instance at the passed key
        :rtype: `string`
        """
        rval = None
        if 0 <= pg_indx < len(self.master_ref.dash_pages_user):
            rval = list(self.master_ref.dash_pages_user)[pg_indx]
        return rval

    def get_page_indx_menu(self, pg_name):
        """function gets the order index of the passed page name
        
        :param pg_name: the reference name of the page to display
        :type pg_name: `string` that matches a main `dash_pages_menu` instance key value
        :returns: main `dash_pages_menu` dict instance index
        :rtype: int
        """
        return list(self.master_ref.dash_pages_menu).index(pg_name)
    
    def get_page_name_menu(self, pg_indx):
        """function gets the user page name at the passed index
        
        :param pg_indx: an index number to check against the main `dash_pages_menu` instance
        :type pg_indx: `int`
        :returns: key value from main `dash_pages_menu` instance at the passed key
        :rtype: `string`
        """
        rval = None
        if 0 <= pg_indx < len(self.master_ref.dash_pages_menu):
            rval = list(self.master_ref.dash_pages_menu)[pg_indx]
        return rval

    def check_page_ifUser(self, pg_name):
        """function checks if the passed page name is a defined user page or not
        
        :param pg_name: the reference name of the page to display
        :type pg_name: `string` that matches a main `dash_page_user` instance key value
        :returns: true/false if value is a user page - True if it is
        :rtype: `bool`
        """
        if pg_name in self.master_ref.dash_pages_user: rval = True  #check if page name is in user pages dict
        else: rval = False
        return rval
    
    def goto_page(self, pg_ref):
        """function loads the passed page into the main container frame
        
        :param pg_ref: reference to a page class to load into the main container frame
        :type pg_ref: `tk.Frame` reference
        """

        try: self.active_page_ref.pack_forget()                 #hide currrent frame if displayed
        except: pass
        self.active_page_ref = pg_ref                           #update to the new frame
        self.active_page_ref.pack(fill="both", expand=True)     #place new frame and fill new frame to window size

    def goto_page_user(self, pg_name):
        """function loads a user page to the dash display based on the passed name
        
        :param pg_name: the reference name of the page to display
        :type pg_name: `string` that matches a main `dash_page_user` instance key value
        """
        pg_ref = self.master_ref.dash_pages_user[pg_name]       #get the active page ref
        self.goto_page(pg_ref)                                  #and go to the page
    
    def goto_page_menu(self, pg_name, nxt_lvl=False):
        """function loads a menu page to the dash display based on the passed name
        
        :param pg_name: the reference name of the page to display
        :type pg_name: `string` that matches a main `dash_page_menu` instance key value
        :param nxt_lvl: the menu page is another level deep and the "last" page should be stored
        :type nxt_lvl: bool - Optional, default False
        """
        if nxt_lvl==True:                                                   #if going "down" a menu level
            self.menu_prev_pages.append(self.active_page_ref.name)              #then append the current name as the "last" page to navigate back to
        pg_ref = self.master_ref.dash_pages_menu[pg_name]                   #get the active page ref
        self.goto_page(pg_ref)                                              #and go to the page
    
    def goto_user_FirstPage(self):
        """function goes to the first user page, typically used on load"""
        first_pg_name = next(iter(self.master_ref.dash_pages_user))         #get the first page name
        self.goto_page_user(first_pg_name)                                  #goto the first user page

    def goto_user_NextPage(self):
        """function goes to the next defined user page. If the current page is the last
        page it will wrap around to the first"""
        crnt_pg_indx = self.get_page_indx_user(self.active_page_ref.name)   #get the index of the current page

        if len(self.master_ref.dash_pages_user) == crnt_pg_indx+1:          #if the current page is the last page
            goto_pg_indx = 0                                                    #then goto the first page
        else: goto_pg_indx = crnt_pg_indx+1                                 #otherwise go to the "next" page
        
        goto_pg_name = self.get_page_name_user(goto_pg_indx)                #get page name at the new index
        self.goto_page_user(goto_pg_name)                                   #and go to the page
    
    def goto_user_PrevPage(self):
        """function goes to the prior defined user page. If the current page is the first
        page it will wrap around to the last"""
        crnt_pg_indx = self.get_page_indx_user(self.active_page_ref.name)   #get the index of the current page

        if crnt_pg_indx == 0:                                               #if the current page is the first page
            goto_pg_indx = len(self.master_ref.dash_pages_user) - 1             #then goto the last page
        else: goto_pg_indx = crnt_pg_indx-1                                 #otherwise go to the "previous" page
        
        goto_pg_name = self.get_page_name_user(goto_pg_indx)                #get page name at the new index
        self.goto_page_user(goto_pg_name)                                   #and go to the page

    def goto_menu_FirstPage(self):
        """function goes to the first menu page, typically used on entering the menu"""
        first_pg_name = next(iter(self.master_ref.dash_pages_menu))         #get the first page name
        pg_ref = self.master_ref.dash_pages_menu[first_pg_name]
        self.goto_page_menu(first_pg_name, True)                            #goto the first menu page

    def goto_menu_BackPage(self):
        """function goes "back" to the page when currently in a menu page. For example, this may be
        the last user dash page visited or it may also be a parent menu page"""
        prev_pg_name = self.menu_prev_pages.pop()           #pop off previous page name
        if self.check_page_ifUser(prev_pg_name) == True:    #if its a user page
            self.goto_page_user(prev_pg_name)                   #then go to user page
        else: self.goto_page_menu(prev_pg_name)             #else go to menu page

    def goto_menu_NextPage(self):
        """function goes to the next defined menu page. If the current page is the last
        page it will wrap around to the first"""
        crnt_pg_indx = self.get_page_indx_menu(self.active_page_ref.name)   #get the index of the current page

        if len(self.master_ref.dash_pages_menu) == crnt_pg_indx+1:          #if the current page is the last page
            goto_pg_indx = 0                                                    #then goto the first page
        else: goto_pg_indx = crnt_pg_indx+1                                 #otherwise go to the "next" page
        
        goto_pg_name = self.get_page_name_menu(goto_pg_indx)                #get page name at the new index
        self.goto_page_menu(goto_pg_name)                                   #and go to the page
    
    def goto_menu_PrevPage(self):
        """function goes to the prior defined menu page. If the current page is the first
        page it will wrap around to the last"""
        crnt_pg_indx = self.get_page_indx_menu(self.active_page_ref.name)   #get the index of the current page

        if crnt_pg_indx == 0:                                               #if the current page is the first page
            goto_pg_indx = len(self.master_ref.dash_pages_menu) - 1             #then goto the last page
        else: goto_pg_indx = crnt_pg_indx-1                                 #otherwise go to the "previous" page
        
        goto_pg_name = self.get_page_name_menu(goto_pg_indx)                #get page name at the new index
        self.goto_page_menu(goto_pg_name)                                   #and go to the page

    def dash_start_HW_ops(self):
        """Function starts any core instances or operations required for the dash to normally
        function. This is typically done after the config has been loaded, verified, and found
        to be OK. For example, without a valid dash config, loading the CAN bus function is
        not necessary and would result in a function error.
        """
        self.dash_start_HW_CAN()            #start CANbus operation
    
    def dash_start_HW_CAN(self):
        """Function starts the required CAN functions for normal dash operation"""
        CANref = self.master_ref.dash_CAN   #temp local ref to CANbus for shorthand
        CANref.CAN_init()                   #initialize CAN operation
        if CANref.CANcom_OK == True:        #if CANbus was successfully started at the HW level, proceed
            CANref.CAN_set_RXlistener(CANref.CAN_msgRX_func)    #assign the listener function to call on a message RX
            CANref.CAN_gen_RXfilters(CANref.RX_filter_en)       #generate the CAN message RX filters, and enable if set
            CANref.CAN_RTR_init()                               #instance/create any RTR requests
            CANref.CAN_RTR_ALLstart()                           #and start all RTR requests
    
    def page_ele_CANref_init(self):
        """function links the data elements to the associated CAN cannel
        and sets trace triggers for data updates"""
        for p in self.master_ref.dash_pages_user.values():      #cycle through all the defined user pages
            for ele in p.Lbl_dat.values(): self.page_ele_CANref_set(ele)    #set triggers for data labels
            for ele in p.Ind_blt.values(): self.page_ele_CANref_set(ele)    #set triggers for bullet indicators
            for ele in p.Ind_bar.values(): self.page_ele_CANref_set(ele)    #set triggers for bar indicators

    def page_ele_CANref_set(self, ele_cfg):
        """function sets the CAN reference for the passed element
        
        :param ele_cfg: page element config class
        :type ele_cfg: any of the dash data element classes like `Label_Data` or `Indicator_Bullet`
        """
        tmp_CANch = self.master_ref.dash_CAN.CANchs                     #shorthand local ref for CAN channels
        ele_cfg.CAN_dec_ref = tmp_CANch[ele_cfg.data_ch].val_dec        #assign ref to CAN channel
        ele_cfg.CAN_dec_ref.trace_add('write', ele_cfg.update_state)    #add trace to update page element

    def dash_buildPages(self):
        """Function builds the various pages in the configuration and udpates the main dash pages dict
        with the instanced/built values
        """
        for p in self.master_ref.dash_pages_user.values():      #cycle through all the defined user pages
            self.dash_buildPage(p)                                  #construct page
            p.btn_func = self.master_ref.dash_ctl.dflt_user_pg_btns #assign default button functions
            
    def dash_buildPage(self, page):
        """function builds and defines the various page elements for the passed page
        
        :param page: passed page to construct
        :type page: `class` dash_page_user instance
        """        
        pg_canv = page.canv                                                 #local ref for the canvas object of the page

        #--set background page color
        pg_bg_clr=self.master_ref.dash_theme.colors.get(page.bg_clr)        #get the page background color value from theme
        pg_canv.configure(bg=pg_bg_clr)                                     #set the page background color

        #--add page background image
        frm_bg_img=self.master_ref.dash_theme.images.get(page.bg_img)       #get the frame background image path
        if frm_bg_img is not None:
            pg_canv.bg_img_obj = self.addImg(pg_canv, frm_bg_img)           #add background image and set ref to prevent trash collection

        #--add page elements
        for ele_cfg in page.Lbl_stc.values():   #loop through all static label configs
            self.addWidget(EleTypes_dict['LBL_STAT'], pg_canv, ele_cfg)
        for ele_cfg in page.Lbl_dat.values():   #loop through all data label configs
            self.addWidget(EleTypes_dict['LBL_DAT'], pg_canv, ele_cfg)
        for ele_cfg in page.Ind_blt.values():   #loop through all bullet indicator configs
            self.addWidget(EleTypes_dict['IND_BLT'], pg_canv, ele_cfg)
        for ele_cfg in page.Ind_bar.values():   #loop through all bar indicator configs
            self.addWidget(EleTypes_dict['IND_BAR'], pg_canv, ele_cfg)

    def usrBtns_init(self):
        """Function binds the input button interrups for the dash and initializes any related required
        methods and bindings"""

        if sys_inDEBUG == True:     #if indebug mode, assign interrups to the numpad inputs
            self.master_ref.bind("<Key>", self.usrBtns_press)
        else:
            #---configure hardware
            GPIO.setmode(GPIO.BCM)              #set GPIO to broadcom specific pin numbers
            #NOTE: PCB has external debounce and pullup, so no need to use "pullup" param
            GPIO.setup(sys_dash_btn1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(sys_dash_btn2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(sys_dash_btn3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(sys_dash_btn4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(sys_dash_btn5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(sys_dash_btn6, GPIO.IN, pull_up_down=GPIO.PUD_UP)

            #---set interrupts
            #----attach button interrupts
            #NOTE: PCB has debounce network for each GPIO but using a relatively small debounce window just to be safe
            GPIO.add_event_detect(sys_dash_btn1, GPIO.FALLING, callback=self.usrBtns_press, bouncetime=sys_btn_bouncetime)
            GPIO.add_event_detect(sys_dash_btn2, GPIO.FALLING, callback=self.usrBtns_press, bouncetime=sys_btn_bouncetime)
            GPIO.add_event_detect(sys_dash_btn3, GPIO.FALLING, callback=self.usrBtns_press, bouncetime=sys_btn_bouncetime)
            GPIO.add_event_detect(sys_dash_btn4, GPIO.FALLING, callback=self.usrBtns_press, bouncetime=sys_btn_bouncetime)
            GPIO.add_event_detect(sys_dash_btn5, GPIO.FALLING, callback=self.usrBtns_press, bouncetime=sys_btn_bouncetime)
            GPIO.add_event_detect(sys_dash_btn6, GPIO.FALLING, callback=self.usrBtns_press, bouncetime=sys_btn_bouncetime)

    def usrBtns_press(self, GPIO_ch):
        """function handles processing the user input button presses
        
        :param GPIO_ch: GPIO channel that triggered the interrupt
        :type GPIO_ch: `GPIO.setmode` pin number; same as defined in sys_dash_btn(x) definitions
        """
        
        #DEBUG: assign the input based on the current run mode
        if sys_inDEBUG == True: event_input = GPIO_ch.char      #get the character of the pressed key
        else: event_input = GPIO_ch                             #assign the GPIO number of the pressed button'''        

        #-----process interrupt
        try:
            userInput_indx = GPIOconvert_dict[event_input]  #convert the event input into a 0-based index for page action management
            call_func = self.active_page_ref.btn_func[userInput_indx]   #get the potential function assigned to the button
            if call_func is not None: call_func()                       #if its assigned a valid function then call it
        except: pass

    def addImg(self, canv, image, x=0, y=0):
        """Function adds an imave to the pased canvas object at the listed coords.
        
        :param canv: parent canvas to make object on
        :type canv: `Tk.Canvas` class
        :param image: absolute filepath to image
        :type image: string
        :param x: x0 position of the image, upper-left corner (default=0)
        :type x: `int`
        :param y: y0 position of the image, upper-left corner (default=0)
        :type y: `int`
        :returns: PhotoImage reference
        :rtype: `tk.PhotoImage` int
        """
        tkImg = tk.PhotoImage(master=canv, file=image)                  #create tk photoImage
        canv.create_image(x, y, image = tkImg, anchor=tk.NW)            #place image
        return tkImg    #return tk image for ref
    
    def addWidget(self, ele_type, ref_canv, ele_cfg):
        """function instances new dash element to the passed canvas. This is typically used when
        loading an existing dash configuration but is also used when adding a new element from the editor.
        When instancing a new dash element, it is placed on the passed canavas, all of the required action 
        bindings for the editor control, and external references required for the class definition are also
        set or assigned.
        
        :param ele_type: the element type being created
        :type ele_type: `DashEle_types`
        :param ref_canv: the parent canvas the widget (dash element) is placed on
        :type ref_canv: `tk.canvas` reference
        :param ele_cfg: the completed element configuration to create
        :type ele_cfg: `element` class instance - IE `label_static` or `indicator_bar` etc
        """
        ele_refID, ele_padID = self.instance_widget(ele_type,
                                                    ref_canv,
                                                    ele_cfg.get_edtr_wgt_kwargs())  #create new widget and assign to object ref in class
        ele_cfg.upd_config({'objID':ele_refID, 'padID':ele_padID})                  #set self refID and background pad refID

    def instance_widget(self, ele_type, prnt_canv, widg_kwargs):
        """function to create a new element in the dash page editor. If only an opbject is created, the
        retrun value will be a tuple of the reference ID and `none` as the second value. If the created 
        widget has a "background pad" rectangle it will also return the ref ID of the background object.

        :param ele_type: the dash element type being created
        :type ele_type: Dict `DashEle_types`
        :param prnt_canv: parent canvas to make object on
        :type prnt_canv: `Tk.Canvas` class
        :param widg_kwargs: widget creation KWARGs - Will be converted here based on the named objects (for font, color, etc.)
        :type widg_kwargs: Dict {kwarg_name \: value}
        :returns: tuple of reference ID of the created object, and pad reference
        :rtype: `tk.canvas` reference
        """
        wigt_ref = None
        
        try:    #processing for widgets with background padding
            pad = widg_kwargs.pop('pad', False)
            clr_bg = widg_kwargs.pop('clr_bg',None)
        except: pass

        #make objects
        if ele_type == EleTypes_dict['LBL_STAT']:
            wigt_ref = prnt_canv.create_text(widg_kwargs.pop('x0'), widg_kwargs.pop('y0'), **widg_kwargs)
        elif ele_type == EleTypes_dict['LBL_DAT']:
            wigt_ref = prnt_canv.create_text(widg_kwargs.pop('x0'), widg_kwargs.pop('y0'), **widg_kwargs)
        elif ele_type == EleTypes_dict['IND_BLT']: 
            wigt_ref = prnt_canv.create_oval(widg_kwargs.pop('x0'), widg_kwargs.pop('y0'),widg_kwargs.pop('x1'), widg_kwargs.pop('y1'),**widg_kwargs)       #set result as oval
        elif ele_type == EleTypes_dict['IND_BAR']:
            wigt_ref = prnt_canv.create_rectangle(widg_kwargs.pop('x0'), widg_kwargs.pop('y0'),widg_kwargs.pop('x1'), widg_kwargs.pop('y1'),**widg_kwargs)  #set result as rectangle

        if pad == True:                     #if widget has background padding, then make it
            pad_ref = self.elePad_create(prnt_canv, wigt_ref, clr_bg)   
            return wigt_ref, pad_ref        #and return created widget reference and pad object reference
        else: return wigt_ref, None         #otherwise, only return created widget reference

    def elePad_create(self, prnt_canv, prnt_wgt, pad_clr):
        """function supports dash element creation. If element has a "background pad" rectangle, this function
        is used to create it.

        :param prnt_canv: parent canvas to make object on
        :type prnt_canv: `Tk.Canvas` class
        :param prnt_wgt: parent object ID the background pad is placed behind
        :type prnt_wgt: dash element class reference
        :param pad_clr: fill color
        :type pad_clr: HEX string color value
        :returns: tuple of reference ID of the created object
        :rtype: `tk.canvas` reference
        """
        prntX0, prntY0, prntX1, prntY1 = prnt_canv.bbox(prnt_wgt)           #find the size of the parent widget
        padX0=prntX0-sys_pad_margin; padX1=prntX1+sys_pad_margin            #calculate X0, x1 for background pad object
        padY0=prntY0; padY1=prntY1                                          #calcualte Y0, Y1 for background pad object
        pad_ref_id = self.draw_rectangle(prnt_canv, padX0, padY0, padX1, padY1, pad_clr)    #create the background pad rectangle
        prnt_canv.tag_lower(pad_ref_id, prnt_wgt)                           #place the background pad below the parent widget
        return pad_ref_id   #return the background pad ID
    
    def draw_rectangle(self, prnt_canv, x0, y0, x1, y1, clr, r=sys_dflt_pad_radius):
        """function draws a rectagle on the parent canvas. Rectangle is based on the passed coords.
        The start coordinate is upper-left corner of the rectangle, end coordinate is lower-left corner 
        of the rectangle. Can pass an optional value (r) to add a radius to the rectangle corners    
            
        :param prnt_canv: parent canvas to draw rectangle on
        :type prnt_canv: `tk.Canvas`
        :param x0: start x coordinate
        :type x0: `int`
        :param y0: start y coordinate
        :type y0: `int`
        :param x1: end x coordinate
        :type x1: `int`
        :param y1: end y coordinate
        :type y1: `int`
        :param clr: color
        :type clr: HEX string color value
        :param r: (optional) rectangle corner radius
        :type r: num pixels in `int`
        :returns: reference ID of the created object
        :rtype: `tk.canvas` reference
        """
        points = [x0+r, y0, x0+r, y0,   #create the polycon points
                x1-r, y0, x1-r, y0,
                x1, y0,
                x1, y0+r, x1, y0+r,
                x1, y1-r, x1, y1-r,
                x1, y1,
                x1-r, y1, x1-r, y1,
                x0+r, y1, x0+r, y1,
                x0, y1,
                x0, y1-r, x0, y1-r,
                x0, y0+r, x0, y0+r,
                x0, y0]
        
        return prnt_canv.create_polygon(points, smooth = True, fill=clr)    #create the background polygon and return refID