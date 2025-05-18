"""
py dash test
------------
test script for setting up the basics of a digital dash using a CM4

Notes
-------------
Files:
    -readme                 >   required package installs, "todo" items, and future feature requests
    -py_dash_defines        >   static value defines used throughout (think background and foreground colors)
    -py_dash_CANdefines     >   CANbus data/labels/vars *****this is what dictates what's handled from CANbus
"""

#-----------------------------imports
from lib import *                       #import files as defined in __init__ file of 'lib' directory

#-----------------------------support functions
''' @brief: message receive routine
    @param: rx_msg  - CANbus message object
    @notes: function is called on a new message rx'd over CANbus
            and parses the appropriate data before calling the
            data update check function
    @retrn: (none)
'''
def msg_rx_routine(rx_msg):
    rx_data = rx_msg.data                               #data part of the message
    rx_addr = rx_msg.arbitration_id                     #address part of the message
    #rx_len = rx_msg.dlc                                 #data length of rx'd packet
    #rx_ext = True if rx_msg.is_extended_id == 'X' else False            #boolean if rx'd ID is an "extended ID"
    upd_CAN_data(rx_addr,rx_data)                       #check rx'd message address against logging channels

''' @brief: update data check
    @param: addr    - CANbus message address
            msg     - CANbus message object
    @notes: function cycles through all of the stored "display"
            indeces of the class (as defined in CANdefines.py)
            and comapres the rx'd address to the array to see which
            index it corresponds to. If the rx'd address and desired
            address match, then the rx'd data is stored to the class.
    @retrn: (none)
'''
def upd_CAN_data(addr, msg):
    for i in range(di_sz):                  #cycle through all the vars
        if(addr == di[i].CAN_addr):         #rx'd message matches one of the display channels
            upd_CAN_dec(i, msg)             #process the data from HEX to DEC

''' @brief: update decimal value from CAN
    @param: index   - data array index that is being updated
            msg     - CANbus message object
    @notes: function takes the current rx'd data message and
            converts it to a decimal/integer value and stores
            that in the struct.
    @retrn: (none)
'''
def upd_CAN_dec(indx, msg):
    data_arry = msg                                             #rx'd data array
    offset = di[indx].dec_ofst                                  #any decimal offset in the calculation
    val = int(data_arry[1])*256 + int(data_arry[0]) + offset    #calculate result
    if di[indx].fxd_pt: val /= 10                               #if value is fixed point, divide by 10
    di[indx].var_value = val                                    #set updated value
    #di[indx].no_data = False                                    #set flag to false, data has been rx'd
    #di[indx].t_last_rx = (now in ms)                            #update time data last rx'd

''' @brief: generate CANbus filters
    @param: (none)
    @notes: function cycles through all of the assigned values in the
            display data class (defined in the CANdefines.py file) and
            appends their addresses to a temporary filter array that is
            used to assign the CANbus filter.
    @retrn: CANbus filter array
'''
def gen_CAN_filters():
    tmp_filter = []                                     #temp CANbus filter array
    tmp_mask = 0x3FF                                    #temp mask to let in all 11-byte addresses
    tmp_id = 0x000                                      #temp ID - to be set in loop below
    tmp_xtnd = False                                    #temp extended frame (currently no for all)

    for i in range(di_sz):                              #loop through array
        tmp_id = di[i].CAN_addr                         #set address for displayed data     
        tmp_filter.append({"can_id": tmp_id, "can_mask": tmp_mask, "extended": tmp_xtnd})   #append to filter array

    return tmp_filter                                   #return filter array

''' @brief: update stringVar
    @param: index   - index of the label class that is being updated
    @notes: function assigns/updates the label stringVar with the
            current corresponding decimal/integer values
    @retrn: (none) 
'''
def upd_strvar(indx):
    data = di[indx].var_value                           #data array value
    #tmout_chk = di[indx].no_data and di[indx].chk_tmout #timeout parameter
    
    #if(tmout_chk):                                      #data has timed out, so update value to IDFK
    #    di[indx].val.set("IDFK")                    
    if(isinstance(data, float)):                        #format to 1 dec if its a float
        di[indx].val.set("{:3.1f}".format(data))
    else:                                               #otherwise, integer assign is fine
        di[indx].val.set(str(data))

#-----------------------------init functions
#can comment out the below before the main window class if static testing

#----CANBUS init
os.system("sudo /sbin/ip link set can0 up type can bitrate 500000")     #bring up can0 interface at 500kbps
time.sleep(0.05)	                                                    #brief pause TODO: does this need to be increased?
CAN1 = can.interface.Bus(channel='can0', bustype='socketcan')           #instance CAN object
#can_filter = gen_CAN_filters()                                          #generate list of filters                    
#CAN1.set_filters(can_filter)                                            #apply list of filters
CAN1_listener = msg_rx_routine                                          #assign message handler as a listener
CAN1_notifier = can.Notifier(CAN1, [CAN1_listener])                     #assign listener to notifier


#-----------------------------class for main window
class MainWindow(tk.Tk):
    #-----main window initilization
    def __init__(self):
        super().__init__()
        
        self.wndw_Default()         #call default window setup
        self.upd_dsply()            #start updating display after init

    ''' @brief: default window definition
        @param: (none)
        @notes: function contains all the widgets/objects for the default
                window to be displayed
        @retrn: (none)
    '''
    def wndw_Default(self):
        #----window settings/info
        self.overrideredirect(True)                         #override direct gets rid of the title bar (fullscreen)
        self.title("Electron Racing Dash")                  #title bar for testing
        disp_res = str(disp_xSz)+'x'+str(disp_ySz)+"+0+0"   #make string for geometry and placement
        self.geometry(disp_res)                             #window size and palcement
        self.maxsize(disp_xSz,disp_ySz)                     #set max size
        self.resizable(False,False)                         #fixed size

        #----init stringvar for data labels
        for i in range(di_sz):                          #loop through array
            di[i].val = tk.StringVar(self, '')          #and assign as a strvar type
            upd_strvar(i)

        #----background image
        self.bgimg = bgimg = tk.PhotoImage(file = working_dir + filepath_bg_img)          #background image
        canv = self.canvas_bg = canvas_bg = tk.Canvas(self, width=disp_xSz, height=disp_ySz) #use canvas to take advantage of the transparencies in the bgimg
        canv.pack(expand=True)
        canv.configure(borderwidth=0,highlightthickness=0)        #remove the border and highlight thickness (kind of the white border)
        canv.configure(bg=bg_color)                               #configure background color of the canvas
        canv.create_image((disp_xc,disp_yc), image=bgimg)         #add image

        #----Indicator shapes
        #RPM bar graph; make rectange full size, same color as background (hidden)
        self.rpm_rect = rpm_rect = canv.create_rectangle(bar_rpm_x0,bar_rpm_y0,bar_rpm_x1,bar_rpm_y1, fill=bg_color)
        canv.tag_lower(self.rpm_rect)                                                 #place rectangle

        #FAN indicator
        self.fan_ind = fan_ind = self.draw_circle(canv, 770,500, 38)
        self.fan_capt = fan_capt = self.draw_txt_lbl(self, txt="FAN", font=default_font_sm); self.fan_capt.place(x=820,y=498, height=noPad_height_sm)

        #headlight indicator
        c = di[indx_lobm]
        self.lobm_img = lobm_img = self.make_image(working_dir + filepath_light_lo, c.lbl_h)
        di[indx_lobm].lbl_ref = self.lobm_id = lobm_id = canv.create_image(c.lbl_x0, c.lbl_y0, image=lobm_img, anchor="w")
        canv.itemconfigure(lobm_id, state='hidden')
        di[indx_lobm].alt_func = self.updInd_LITE
        di[indx_lobm].scope_ref = canv

        c = di[indx_hibm]
        self.hibm_img = hibm_img = self.make_image(working_dir + filepath_light_hi, c.lbl_h)
        di[indx_hibm].lbl_ref = self.hibm_id = hibm_id = canv.create_image(c.lbl_x0, c.lbl_y0, image=hibm_img, anchor="w")
        canv.itemconfigure(hibm_id, state='hidden')
        di[indx_hibm].alt_func = self.updInd_LITE
        di[indx_hibm].scope_ref = canv

        #----data labels
        #RPM label
        c = di[indx_rpm]    #assign temp class var copy of this specific index for shorthand
        #place background rounded rectangle
        self.rpm_bg_rect = rpm_bg_rect = self.draw_round_rect(canv, 360,142,360,65)
        #place data label caption
        self.rpm_capt = rpm_capt = self.draw_txt_lbl(self, txt=c.capt); self.rpm_capt.place(x=c.capt_x0,y=c.capt_y0, height=c.capt_h)
        #place data label, bound to stringvar
        self.lbl_rpm = self.draw_txt_lbl(self, strvar=c.val, anchor="e")
        self.lbl_rpm.place(x=c.lbl_x0,y=c.lbl_y0, height=c.lbl_h, width=c.lbl_w)
        #update other functions for the "data channel"
        di[indx_rpm].lbl_ref = self.lbl_rpm                            #label reference for updating
        di[indx_rpm].scope_ref = canv                                  #scope reference for updating
        di[indx_rpm].alt_func = self.updInd_rpm                        #assign alternate function associated with the label
        
        #ECT label
        c = di[indx_ect]
        self.bg_ect_rect = bg_ect_rect = self.draw_round_rect(canv, 100,250,320,64)
        self.ect_capt = ect_capt = self.draw_txt_lbl(self, txt=c.capt); self.ect_capt.place(x=c.capt_x0,y=c.capt_y0, height=c.capt_h)
        self.lbl_ect = self.draw_txt_lbl(self, strvar=c.val, anchor="e")
        self.lbl_ect.place(x=c.lbl_x0,y=c.lbl_y0, height=c.lbl_h, width=c.lbl_w)
        di[indx_ect].lbl_ref = self.lbl_ect
        di[indx_ect].scope_ref = canv
        di[indx_ect].alt_func = self.updInd_fan

        #wbo2 label
        c = di[indx_o2]
        self.bg_o2_rect = bg_o2_rect = self.draw_round_rect(canv, 604,250,320,64)
        self.o2_capt = o2_capt = self.draw_txt_lbl(self, txt=c.capt); self.o2_capt.place(x=c.capt_x0,y=c.capt_y0, height=c.capt_h)
        self.lbl_wbo2 = self.draw_txt_lbl(self, strvar=c.val, anchor="e")
        self.lbl_wbo2.place(x=c.lbl_x0,y=c.lbl_y0, height=c.lbl_h, width=c.lbl_w)
        di[indx_o2].lbl_ref = self.lbl_wbo2
        di[indx_o2].scope_ref = canv

        #OilP label
        c = di[indx_oilp]
        self.bg_oilp_rect = bg_oilp_rect = self.draw_round_rect(self.canvas_bg, 100,360,320,64)
        self.oilp_capt = oilp_capt = self.draw_txt_lbl(self, txt=c.capt); self.oilp_capt.place(x=c.capt_x0,y=c.capt_y0, height=c.capt_h)
        self.lbl_oilp = self.draw_txt_lbl(self, strvar=c.val, anchor="e")
        self.lbl_oilp.place(x=c.lbl_x0,y=c.lbl_y0, height=c.lbl_h, width=c.lbl_w)
        di[indx_oilp].lbl_ref = self.lbl_oilp
        di[indx_oilp].scope_ref = canv

        #MAP label
        c = di[indx_map]
        self.bg_map_rect = bg_map_rect = self.draw_round_rect(self.canvas_bg, 604,360,320,64)
        self.map_capt = map_capt = self.draw_txt_lbl(self, txt=c.capt); self.map_capt.place(x=c.capt_x0,y=c.capt_y0, height=c.capt_h)      
        self.lbl_map = self.draw_txt_lbl(self, strvar=c.val, anchor="e")
        self.lbl_map.place(x=c.lbl_x0,y=c.lbl_y0, height=c.lbl_h, width=c.lbl_w)
        di[indx_map].lbl_ref = self.lbl_map
        di[indx_map].scope_ref = canv
        
    #-----support classes/functions
    ''' @brief: draw roung rectangle
        @param: canv    - canvas object rectangle is being placed on
                x0, y0  - initial anchor points (*of the top-left corner)
                w,h     - width and height
                r       - corner radius
        @notes: default kwargs set to standard values
        @retrn: rounded rectangle object  
    '''
    def draw_round_rect(self, canv, x0, y0, w, h, r=20, **kwargs):
        #special thanks to SneakyTurtle on stackoverflow for this
        #remeber with **kwargs any of the default options works
        x1=x0+w; y1=y0+h
        points = [  x0+r, y0, x0+r, y0,
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
        
        #do some default appearance assignments via kwargs
        kwargs.setdefault("width", 3)
        kwargs.setdefault("fill", bg_color)

        return canv.create_polygon(points, smooth = True, **kwargs) #return created polygon
    
    ''' @brief: draw cicle
        @param: canv    - canvas object rectangle is being placed on
                x0, y0  - initial anchor points (*of the top-left corner)
                scale   - x/y size scale (in pixels) to get to x1, y1
        @notes: modified from the draw elipse to just have a square scale
        @retrn: circle canvas object 
    '''
    def draw_circle(self, canv, x0, y0, scale, **kwargs):
        #default kwarg assignments
        kwargs.setdefault("width", 3)
        kwargs.setdefault("fill", bg_color)
        kwargs.setdefault("outline", lbl_otln_color)
        return canv.create_oval(x0,y0,x0+scale, y0+scale, **kwargs) #return circle object
    
    ''' @brief: draw text label
        @param: scope   - window or scope the tkinter object is being created in
                txt     - text to be hard-fixed to the label (if its a static label)
                strvar  - stringVar to be assigned to the label (for dynamic labels)
        @notes: modified from the draw elipse to just have a square scale
        @retrn: label object 
    '''
    def draw_txt_lbl(self, scope, txt=None, strvar=None, **kwargs):
        tmp_lbl = tk.Label(scope)                                   #create temp label

        #do some default appearance assignments via kwargs
        kwargs.setdefault("font", default_font) 
        kwargs.setdefault("fg", lbl_fg_color)    
        kwargs.setdefault("bg", bg_color)       
        kwargs.setdefault("anchor", "w")

        tmp_lbl.config(**kwargs)                                    #apply configuration
        if txt is not None: tmp_lbl.config(text=txt.upper())        #assign text if passed
        if strvar is not None: tmp_lbl.config(textvariable=strvar)  #and/or bind label to if passed
        return tmp_lbl
    
    ''' @brief: place image
        @param: canv    - canvas object rectangle is being placed on
                x, y    - anchor points (*of the top-left corner)
                h_scale - height scale of desired output
        @notes: the height scale is passed and then for non-square images
                the width-scale is calculated. It's not exact but is 
                "rounded" via truncation to the closest value.
        @retrn: image canvas object 
    '''
    def make_image(self, img, h_scale=None):
        self.i_img = i_img = Image.open(img)                        #open passed image
        if h_scale is not None:                                     #rescale image
            w_scale = int(i_img.width*h_scale / i_img.height)       #get width scale
            self.r_img = r_img = i_img.resize((w_scale,h_scale))    #and resize
        else: self.r_img = r_img = i_img                            #otherwise leave native size
        self.tmp_img = tmp_img = ImageTk.PhotoImage(r_img)          #create tk Image after any modification
        return ImageTk.PhotoImage(r_img)                            #return image object

    ''' @brief: update display
        @param: (none)
        @notes: function serves as a "refresh" type function to update the
                various stringvars as well as some formatting conditions like
                the warning/error text colors, etc.
        @retrn: (none)
    '''
    def upd_dsply(self):
        for i in range(di_sz):                      #cycle through all the entires of disp_data
            self.upd_lbl_colors(i)                  #update colors accordingly
            upd_strvar(i)                           #update label stringvars
            #self.check_chan_timeout(i)              #check the data channel timeout intervals
        self.after(refresh_rate, self.upd_dsply)    #continue to update every interval

    ''' @brief: update label colors
        @param: i   - label index
        @notes: function looks at the upper/lower bounds for the
                warning and error values and updates the label colors
                accordingly.
        @retrn: (none)
    '''    
    def upd_lbl_colors(self, indx):
        func = di[indx].alt_func
        if func is not None: func()             #if the secondary function tied to the var isn't blank, then call it
        if(not(di[indx].warn_en)): return None  #color change not enabled, so return early
        val = di[indx].var_value
        lbl = di[indx].lbl_ref
        typ = di[indx].lbl_typ
        dngr_lo= di[indx].dngr_lo
        wrn_lo = di[indx].warn_lo
        wrn_hi = di[indx].warn_hi
        dngr_hi= di[indx].dngr_hi
        
        #--see if the value falls in the alert ranges
        if(val <= dngr_lo): tmp_fg = alert_lbl_fg_color     ;tmp_bg = dngr_color    #value is less than the danger threshold
        elif(val <= wrn_lo): tmp_fg = alert_lbl_fg_color    ;tmp_bg = warn_color    #same but warning
        elif(val >= dngr_hi): tmp_fg = alert_lbl_fg_color   ;tmp_bg = dngr_color    #value is greater than the danger threshold
        elif(val >= wrn_hi): tmp_fg = alert_lbl_fg_color    ;tmp_bg = warn_color    #same but warning
        else:tmp_fg = lbl_fg_color                          ;tmp_bg = bg_color      #value is OK, so "standard" colors get set

        #--update label colors
        if(typ == lbl_type_data):   lbl.config(fg = tmp_fg, bg = tmp_bg)            #update data label colors
        elif(typ == lbl_type_ind):  self.canvas_bg.itemconfig(lbl, fill=bg_color)   #update indicator colors
        else: pass                                                                  #do nothing if undefined

    ''' @brief: channel timeout
        @param: i   - channel index
        @notes: function checks when data was last reveived and sets
                a flag accordingly. If no data has been rx'd in the aloted
                timeout window, then the dash will update the current value
        @retrn: (none)
    '''
    '''
    def check_chan_timeout(self, i):
        t_lrx = di[i].t_last_rx     #last rx     
        t_tmout = di[i].t_tmout     #timeout interval
        t_now = 0                   #current time

        if((t_now - t_lrx) > t_tmout): di[i].no_data = True
    '''

    ''' @brief: update indicator - RPM bar graph
        @param: (none)
        @notes: function updates the size and color of the RPM bar
                graph based on the current RPM value. called as a
                "secondary function" to the RPM label.
        @retrn: (none)
    '''
    def updInd_rpm(self):
        ind = self.rpm_rect
        _canv = self.canvas_bg

        #temp vals for hard-coding the test implementation
        current_rpm = di[indx_rpm].var_value
        warn_rpm = di[indx_rpm].warn_hi
        danger_rpm = di[indx_rpm].dngr_hi

        #----update shape
        x0,y0, x1, y1 = _canv.coords(ind)                   #get the coords of the rectangle
        x1 = x0 + (current_rpm / max_rpm)*max_width         #do a calculate for the width
        _canv.coords(ind,x0,y0, x1, y1)                     #set new coords

        #----update color
        if(current_rpm>danger_rpm): fill_color='#FF0000'    #red color for redline
        elif(current_rpm>warn_rpm): fill_color='#FFFF00'    #yellow color for near redline
        else:                       fill_color='#00FF00'    #normal color (green for now)  
        _canv.itemconfig(ind, fill=fill_color)              #set fill color depending on value

    ''' @brief: update indicator - Fan on/off dot
        @param: (none)
        @notes: function updates the indicator dot for the "fan is on"
                label. called as a "secondary function" to the ECT label.
        @retrn: (none)
    '''
    def updInd_fan(self):
        ind = self.fan_ind
        _canv = self.canvas_bg
        current_temp = di[indx_ect].var_value

        #----update color
        if(current_temp>fan_on):    fill_color=ind_on_color     #set indicator to "on"
        elif(current_temp<fan_off): fill_color=ind_off_color    #set indicator to "off"
        else:                       fill_color=bg_color         #default background color
        _canv.itemconfig(ind, fill=fill_color)                  #set fill color depending on value

    ''' @brief: update indicator - headlights
        @param: (none)
        @notes: function updates the indicator for the headlight
                on/off and hi/lo
        @retrn: (none)
    '''
    def updInd_LITE(self):
        lo_canv = di[indx_lobm].scope_ref
        hi_canv = di[indx_hibm].scope_ref
        lo_ind = di[indx_lobm].lbl_ref
        hi_ind = di[indx_hibm].lbl_ref
        lobm = di[indx_lobm].var_value
        hibm = di[indx_hibm].var_value

        #check to see if lights are on, and if highbeam is on
        if(lobm >= lobm_on):    _lobm_on = True
        else:                   _lobm_on = False
        if(hibm >= hibm_on):    _hibm_on = True
        else:                   _hibm_on = False

        #display the correct symbol
        if(_lobm_on and _hibm_on):              #show hi-beam
            lo_canv.itemconfigure(lo_ind, state='hidden')
            hi_canv.itemconfigure(hi_ind, state='normal')
        elif(_lobm_on and not(_hibm_on)):       #show lo-beam
            hi_canv.itemconfigure(hi_ind, state='hidden')
            lo_canv.itemconfigure(lo_ind, state='normal')
        else:                                   #both off, show nothing
            lo_canv.itemconfigure(lo_ind, state='hidden')
            hi_canv.itemconfigure(hi_ind, state='hidden')

#end of main window class

#-----------------------------main loop
if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
