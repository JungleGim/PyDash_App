"""
File:       com_defs.py
Function:   This file contains any of the common functions used across any of the different
            files or functions within the application
"""

from .sys import *

#-----------------------------------control dicts----------------------------------
#--types of menu pages
pageTypes_dict_menu = {'main_settings':'stngs', #main user configurable settings
                       'error':'err',           #current errors
                       'CAN_sniffer':'snfr'}    #CAN sniffer

#--converting GPIO inputs to 0th index values for button controls
GPIOconvert_dict = {sys_dash_btn1:0,
                    sys_dash_btn2:1,
                    sys_dash_btn3:2,
                    sys_dash_btn4:3,
                    sys_dash_btn5:4,
                    sys_dash_btn6:5,
                    '7':0,                  #development mode - numpad corresponding to dash button
                    '4':1,
                    '1':2,
                    '9':3,
                    '6':4,
                    '3':5,}

#--XML tree types
XMLcfg_types = {'DISP':'DISP',
                'THEME':'THEME',
                'CAN':'CAN',
                'FRAMES':'FRAMES'}

#---dash element types
EleTypes_dict = {'LBL_STAT': 1,     #static label
                 'LBL_DAT':2,       #data label (dynamic value)
                 'IND_BLT':3,       #bullet indicator
                 'IND_BAR':4}       #bar indicator

#---warning limit theme attribute names
WarnState_dict = {'DNGR_LO':'alert_dngr',
                  'WARN_LO':'alert_warn',
                  'WARN_HI':'alert_warn',
                  'DNGR_HI':'alert_dngr',
                  'ALRT_FG':'alert_FG'}

#----------------------------------common methods----------------------------------
def str2dec(val, frmt=10):
    """converts passed value to decimal value

    function can handle a `string`(int), `string`(fraction), `integer`, `float`, 
    or `none` type. If passed a `none` or zero-length string, then `none` is returned. If passed value
    is fractional representation, i.e. (1/10) then it is converted into a float (0.1)

    :param val: value to convert
    :type val: `string`, `char`, `integer`, or `float`
    :param frmt: int conversion base, defaults to base-10
    :type frmt: accepts '10' or '16'
    :returns: converted value
    :rtype: `integer` or `float`
    """
    rval = None
    if val == None: rval = None                 #value is none, so no conversion needed
    elif val == '': rval = None                 #value is a blank string, so return None
    elif type(val) == int: rval = val           #value is already in int format, no need to convert
    elif type(val) == float: rval = val         #value is already in float format, no need to convert
    elif '/' in val:                            #value is in fraction form, split and calculate
        num, den = val.split('/')
        rval = int(num)/int(den)
    elif '.' in val: rval = float(val)          #value has a decimal so use float
    elif frmt == 10: rval = int(val)            #dec format
    elif frmt == 16: rval = int(val, 16)        #hex format
    
    return rval                                 #default return None if unknown

def str2bool(val):
    """converts string to boolean value

    :param val: value to convert
    :type val: `string` or `char`
    :returns: the converted value
    :rtype: `boolean`
    """
    rval = False
    if type(val) == bool: rval = val            #value is already in bool format, no need to convert
    elif val.lower() == 'true': rval = True     #convert to true
    elif val.lower() == 'false': rval = False   #convert to false
    
    return rval                                 #default return false if unknown

def tup2str(tup):
    """function converts the passed tuple into a comma-separated string
        
    :param tup: value to convert
    :type tup: `tuple` of any type
    :returns: the converted value
    :rtype: `string`
    """
    csr = ", ".join(tup)
    return csr

def dec2str(val, sigdig=0):
    """function converts the passed decimal value to a string representation. Additionally
    can specify the number of sig digs used in the conversion. When specifying sigdigs the
    round() function will be used to update the value.
    
    :param val: value to convert
    :type val: `int` or `float`
    :param sigdig: number of significant digits to use in the conversion
    :type sigdig: `int` from 0-5
    :returns: converted value
    :rtype: `string`
    """
    rval = None
    if sigdig == 0: sigdig = None               #if sigdigs is 0, then pass None, otherwise will display a decimal
    elif sigdig > 5: sigdig = 5                 #and cap at 5 significant digits

    if val == None: rval = None                 #value is none, so no conversion needed
    elif not isinstance(val, (int, float, complex)): rval = None #if not a number formatted value, return none
    else: rval = str(round(val, sigdig))        #otherwise convert value

    return rval                                 #default return None if unknown

def check_file_exists(file_path):
    """function checks if the file exists - ONLY for files, not directories
    
    :param file_path: absolute file path to the file to find
    :type file_path: string
    :returns: true if file exists
    :rtype: bool
    """
    rval = False                                #temp return value - default false if not found
    if os.path.isfile(file_path): rval = True   #if found, update to true
    return rval

def check_dir_exists(dir_path):
    """function checks if the directory exists - ONLY for directories, not files
    
    :param dir_path: absolute file path to the directory to find
    :type dir_path: string
    :returns: true if directory exists
    :rtype: bool
    """
    rval = False                                #temp return value - default false if not found
    if os.path.isdir(dir_path): rval = True     #if found, update to true
    return rval

def XML_open(master_ref, xmlFile_path):
    """function opens the passed XML file at the passed directory. If its a valid XML file, then it creates an element-tree XML object and returns the result
    
    :param master_ref: reference back to the main/master window
    :type master_ref: main `tk.window` ref
    :param xmlFile: full file path to the XML file to open
    :type xmlFile: `string`
    :returns: XML element tree result of the opened file
    :rtype: XML ET.parse() object result
    """
    xmlFile_ET = None  #opened XML file
    try: xmlFile_ET = ET.parse(xmlFile_path)
    except Exception as e:        
        master_ref.upd_errors([create_err_msg('Core','CFG','Unable to Open XML congig file. System error is: '+ e.msg)])
    
    return xmlFile_ET

def create_err_msg(system, module, message, clearable=False):
    """function creates a message to send to the master error tracking dictionary and
    returns the correct format
    
    :param system: the system associated with the error
    :type system: `string`
    :param module: the module in the system where the error occurred
    :type module: `string`
    :param message: a short, descriptive error message
    :type message: `string`
    :param clearable: true/false if the error is clearable. Critical messages should be non-clearable.
    :type clearable: `boolean` - Default false
    :returns: completed error dict message
    :rtype: formatted error dict {err_time:`err_message` instance}
    """
    err_time = round((time.time()*1000)) - sys_start_time_ms
    return err_message({'time':err_time,'sys':system,'mod':module,'clr':clearable,'msg':message})

def get_alert_color(val, dngrLO_lim, warnLO_lim, warnHI_lim, dngrHI_lim):
    """Function compares the passed value to the passed limits and returns the warning or
    danger state required for those limits
    
    :param val: decimal value to compare
    :type val: `int` or `float`
    :param dngrLO_lim: alert limit - low danger
    :param warnLO_lim: alert limit - low warning
    :param warnHI_lim: alert limit - high danger
    :param dngrHI_lim: alert limit - high warning
    :returns: name of the theme color attribute
    :rtype: `WarnState_dict` or None - None if inside limits
    """
    rval = None     #temp return for alert state

    if val < dngrLO_lim: rval = WarnState_dict['DNGR_LO']
    elif val < warnLO_lim: rval = WarnState_dict['WARN_LO']
    elif val > dngrHI_lim: rval = WarnState_dict['DNGR_HI']
    elif val > warnHI_lim: rval = WarnState_dict['DNGR_HI']

    return rval

#----------------------------------common classes----------------------------------
class err_message:
    def __init__(self, kwargs):
        """class used for defining error messages"""
        self.time = kwargs.get('time', 't_unk')         #tome the error occurred
        self.sys = kwargs.get('sys', 'sys_unk')         #system that caused the error
        self.mod = kwargs.get('mod', 'mod_unk')         #module in the system that caused the error
        self.clr = kwargs.get('clr', False)             #message is clearable
        self.msg = kwargs.get('msg', 'unknown error')   #error message

class page_template(tk.Frame):
    def __init__(self, prnt_frm):
        """class is the basic page template used as a starting point for user pages
        
        :param prnt_frm: the parent frame this will be contained in
        :type prnt_frm: `tk.Frame` reference
        """
        super().__init__(prnt_frm)
        
        self.canv = tk.Canvas(self, width=sys_disp_xSz, height=sys_disp_ySz)    #page working canvas
        self.canv.pack(expand=True)                                             #fit to full display
        self.canv.configure(borderwidth=0,highlightthickness=0)                 #remove the border and highlight thickness

        #--references
        self.bg_img_obj = None  #reference object to any background image to prevent trash collection

        #--misc
        self.btn_func = []      #list to store the button functions of the current page

class dash_page_fullscreen_text(page_template):
    def __init__(self, master_ref, display_text):
        """class is a full screen text display, typically used when displaying critical errors
        
        :param prnt_frm: the parent frame this will be contained in
        :type prnt_frm: `tk.Frame` reference
        :param display_text: the warning / message text to display
        :type display_text: `string`
        """
        super().__init__(master_ref.prnt_frm)

        self.canv.configure(bg=menuTheme_color_BG)
        disp_txt = self.canv.create_text(sys_disp_xc, sys_disp_yc,
                                         text=display_text, anchor='center',
                                         font=menuTheme_font_medium, fill=menuTheme_color_TextFG,
                                         width=sys_disp_xSz)

class dash_page_user(page_template):
    def __init__(self, master_ref):
        """class is the base class for user configured pages
        
        :param master_ref: reference back to the main/master window
        :type master_ref: main `tk.window` ref
        """
        page_template.__init__(self, master_ref.prnt_frame)     #inherit page construction template args and methods
        
        #--page information
        self.master_ref = master_ref  #set the master reference
        self.name = None        #frame name
        self.level = None       #frame level
        self.parent = None      #named parent frame - default base
        self.type = None        #frame type
        self.bg_clr = None      #named color for background (see theme class)
        self.bg_img = None      #named image for background (see theme class)
        self.width = None       #frame wdith
        self.height = None      #frame height

        #--page elements
        self.Lbl_stc = {}       #dict of static labels. Format is {'Name' : Label_Static_Class}
        self.Lbl_dat = {}       #dict of data labels. Format is {'Name' : Label_Data_Class}
        self.Ind_blt = {}       #dict of bullet indicators. Format is {'Name' : Ind_Bullet_Class}
        self.Ind_bar = {}       #dict of bar indicators. Format is {'Name' : Ind_Bar_Class}

    def set_cfg(self, **kwargs):
        """ function sets class attributes based on the passed KWARGs.
        All KWARGs have default values non-required core fields. IE, RTR
        has a default field, but PID does not.

        :param kwargs: dict of class inputs
        :type kwargs: any type that can be typecast to string
        """
        kwargs = {k.upper(): v for k, v in kwargs.items()}  #convert kwarg names to uppercase. Allows for use with XML and editor attributes
        self.name = kwargs.get('NAME', 0)                   #frame name
        self.level = kwargs.get('LEVEL', 0)                 #frame level
        self.parent = kwargs.get('PARENT', 'MASTER')        #named parent frame - default base
        self.type = kwargs.get('TYPE', 'GAGUE')             #frame type
        self.bg_clr = kwargs.get('BG_CLR', None)            #named color for background (see theme class)
        self.bg_img = kwargs.get('BG_IMG', None)            #named image for background (see theme class)
        self.width = kwargs.get('WIDTH', sys_disp_xSz)
        self.height = kwargs.get('HEIGHT', sys_disp_ySz)
        if self.width is None: self.width = sys_disp_xSz
        if self.height is None: self.height = sys_disp_ySz
    
    def update_eleCfg(self, passed_eles):
        """function updates the contained dash element dictionaries based on the dict of passed element(s).
        The passed dict can consiste of elements of various types and assignment to the appropriate
        definition is handled here.
        
        :param passed_eles: page editor widgets to add or update
        :type passed_eles: `dict` formatted {element_name:`element class`} - Example of an element class instance would be `Label_Static`
        """
        for k, v in passed_eles.items():
            match v:
                case Label_Static():
                    self.Lbl_stc.update({k:v})   #add or update static label
                case Label_Data():
                    self.Lbl_dat.update({k:v})   #add or update data label
                case Indicator_Bullet():
                    self.Ind_blt.update({k:v})   #add or update bullet indicator
                case Indicator_Bar():
                    self.Ind_bar.update({k:v})   #add or update bar indicator
    
    def dashCFG_checkErrs(self, theme_cfg=None, CAN_cfg=None):
        """function checks the required class attributes to see if they are set and if the set value is
        a correct format and/or reference. If it is not set, or the value is not correct for the configuration,
        then the attribute name, and an error message are added to the temporary error dict. Once complete
        this error dict is passed to the custom warning window message to indicate where in a dash configuration
        there may be issues.
        
        :returns: dict of attributes with errors
        :rtype: `dictionary` {attribute_name:"error message"}
        """
        tmp_err_list = []   #temp list for compiling errors
        if theme_cfg == None: theme_cfg = self.master_ref.dash_theme
        
        #--check core page properties
        if self.bg_clr is None:
            tmp_err_list.append(create_err_msg('Page',self.name,'BG color is not defined'))
        else:
            if not theme_cfg.chk_exist_colors(self.bg_clr):
                tmp_err_list.append(create_err_msg('Page',self.name,'BG color '+self.bg_clr+' is not defined in theme'))
        if self.bg_img is not None:
            if not theme_cfg.chk_exist_imgs(self.bg_img):
                tmp_err_list.append(create_err_msg('Page',self.name,'BG image '+self.bg_img+' is not defined in theme'))
        if self.width is None or self.width == '':
            tmp_err_list.append(create_err_msg('Page',self.name,'width value is not defined'))
        if self.height is None or self.height == '': 
            tmp_err_list.append(create_err_msg('Page',self.name,'height value is not defined'))

        #--cycle through all the various page elements and check for errors
        for v in self.Lbl_stc.values():
            stc_errs = v.dashCFG_checkErrs(self.name)
            if stc_errs:
                for err in stc_errs: tmp_err_list.append(err)
        for v in self.Lbl_dat.values():
            dat_errs = v.dashCFG_checkErrs(self.name)
            if dat_errs:
                for err in dat_errs: tmp_err_list.append(err)
        for v in self.Ind_blt.values():
            blt_errs = v.dashCFG_checkErrs(self.name)
            if blt_errs:
                for err in blt_errs: tmp_err_list.append(err)
        for v in self.Ind_bar.values():
            ind_errs = v.dashCFG_checkErrs(self.name)
            if ind_errs:
                for err in ind_errs: tmp_err_list.append(err)

        return tmp_err_list #return error list

class dash_theme_user:
    def __init__(self):
        """class is the theme that's used for all user configured pages"""
        self.colors = {}        #defined colors in format {'ref_name':#HEX_val}
        self.fonts = {}         #defined fonts in format {'ref_name':(font,information,tuple)}
        self.images = {}        #defined images in format {'ref_name':'absolute_path_string'}

        self.alert_FG=None      #named color for FG (text) when alert color-changing is enabled
        self.alert_warn=None    #warning named color for BG when alert color-changing is enabled
        self.alert_dngr=None    #danger named color for BG when alert color-changing is enabled
    
    def set_colors(self, passed_colors):
        """function sets/updates the defined theme color(s) based on the passed dict.
        
        :param passed_colors: dict of color(s) to update the theme with
        :type passed_colors: `dictionary` {color_name:#HEX_VAL}
        """
        for k,v in passed_colors.items():   #cycle through all passed colors
            self.colors.update({k:v})       #update theme color data

    def set_fonts(self, passed_fonts):
        """function sets/updates the defined theme font(s) based on the passed dict.
        
        :param passed_fonts: dict of font(s) to update the theme with
        :type passed_fonts: custom defined `font` class {font_name:`font class`}
        """
        for k,v in passed_fonts.items():    #cycle through all passed fonts
            self.fonts.update({k:v})        #update theme font data

    def set_imgs(self, passed_img):
        """function sets/updates the defined theme images(s) based on the passed dict.
        
        :param passed_img: dict of images(s) to update the theme with
        :type passed_img: `dictionary` {img_name:`absolute_filepath`}
        """
        for k,v in passed_img.items():      #cycle through all passed images
            self.images.update({k:v})       #update theme image data        
    
    def set_alert_colors(self, passed_colors):
        """function sets the colors used in limit warnings (like the warning and/or danger limits). Function
        also updates external color refs for the assigned colors.
        
        :param passed_colors: dict of color key values to update
        :type passed_colors: `dictionary` {alert_kwarg : theme_color_name}
        """
        #--convert passed color names to uppercase. Allows for use with XML and editor attributes
        passed_colors = {k.upper(): v for k, v in passed_colors.items()}

        #--update theme values
        self.alert_FG=passed_colors.get('ALERT_FG', None)
        self.alert_warn=passed_colors.get('ALERT_WARN', None)
        self.alert_dngr=passed_colors.get('ALERT_DNGR', None)
    
    def convert_init_fnt_tup(self):
        """function converts the font tuple string read from the XML file into an actual tuple for
        later use in the theme config"""
        for k,v in self.fonts.items():          #cycle through all the defined fonts
            self.fonts[k] = literal_eval(v)     #convert string into a tuple

    def convert_init_img_path(self):
        """function converts the initial read image name into the actual path where it's located
        for later use in the theme config"""
        for k,v in self.images.items():             #cycle through all the defined images
            tmp_path = sys_cfg_Images_dir+v
            self.images[k] = sys_cfg_Images_dir+v   #update the path

    def dashCFG_checkErrs(self):
        """function checks the required class attributes to see if they are set and if the set value is
        a correct format and/or reference. If it is not set, or the value is not correct for the configuration,
        then the attribute name, and an error message are added to the temporary error dict. Once complete
        this error dict is passed to the custom warning window message to indicate where in a dash configuration
        there may be issues.
        
        :returns: dict of attributes with errors
        :rtype: `dictionary` {attribute_name:"error message"}
        """
        tmp_err_list = []   #temp list for compiling errors
        for k,v, in self.colors.items():        #cycle through all colors
            if self.chk_clr_val(v):                 #if an error is found, append to error list
                tmp_err_list.append(create_err_msg('Theme','Color','Color-'+k+'-invalid hex code'))
        for k,v in self.fonts.items():          #cycle through all fonts
            if self.chk_fnt_val(v):                 #if an error is found, append to the error list
                tmp_err_list.append(create_err_msg('Theme','Font','Font-'+k+'-invalid definition'))
        for k,v in self.images.items():         #cycle through all images
            if self.chk_img_path(v):                #if an error is found, append to the error list
                tmp_err_list.append(create_err_msg('Theme','Img','IMG-'+k+'-invalid path'))
        
        if not self.chk_exist_colors(self.alert_FG):
            tmp_err_list.append(create_err_msg('Theme','CFG','Alert Color-'+self.alert_FG+'-not defined in theme'))
        if not self.chk_exist_colors(self.alert_warn):
            tmp_err_list.append(create_err_msg('Theme','CFG','Alert Color-'+self.alert_warn+'-not defined in theme'))
        if not self.chk_exist_colors(self.alert_dngr):
            tmp_err_list.append(create_err_msg('Theme','CFG','Alert Color-'+self.alert_dngr+'-not defined in theme'))

        return tmp_err_list #return any errors

    def chk_clr_val(self, clr_val):
        """function checks the passed theme color string to ensure it is correct.
        
        :returns: True/False if errors are found - True indicates errors were found
        :rtype: `bool`
        """
        errs = False
        valid_color_pattern = r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$"    #string to match hex color codes
        if not bool(rgx.match(valid_color_pattern, clr_val)):           #check if color hex code is valid or not
            errs = True
        return errs
    
    def chk_fnt_val(self, fnt_tup):
        """function checks the passed theme font tupple to ensure it is correct.
        
        :returns: True/False if errors are found - True indicates errors were found
        :rtype: `bool`
        """
        errs = False
        fnt_dict = {'family': fnt_tup[0],
                            'size': fnt_tup[1],
                            'weight':fnt_tup[2],
                            'slant':fnt_tup[3]}     #build font option dict
        try: myfont = tkFont.Font(**fnt_dict)       #try to define font object using options
        except: errs = True                         #if unable to, then return that there is an error
        return errs
    
    def chk_img_path(self, path):
        """function checks the passed image path to ensure it is exists.
        
        :returns: True/False if errors are found - True indicates image was unable to be found
        :rtype: `bool`
        """
        return not check_file_exists(path)

    def chk_exist_colors(self, clr_name):
        """function checks if color is defined in theme dictionary. Returns true if it is"""
        if clr_name is None: return False
        elif clr_name in self.colors: return True
        else: return False        

    def chk_exist_fonts(self, fnt_name):
        """function checks if color is defined in theme dictionary. Returns true if it is"""
        if fnt_name is None: return False
        elif fnt_name in self.fonts: return True
        else: return False   

    def chk_exist_imgs(self, img_name):
        """function checks if color is defined in theme dictionary. Returns true if it is"""
        if img_name is None: return False
        elif img_name in self.images: return True
        else: return False

class dash_config:
    def __init__(self):
        """Configuration class for core dash options (HW configuration). Examples of contained information
        includes screen resolution, backlight PWM value, and other "core" options."""
        self.Res_x = None       #window x-resolution
        self.Res_y = None       #window y-resolution
        self.Refresh = None     #refresh rate - default of approx 15Hz in ms
        self.Baklite = None     #backlight brightness - default full bright
    
    def upd_cfg(self, **kwargs):
        """ function sets attributes based on the passed KWARGs. All KWARGs have default values
        for typical display values. If kwarg is not passed, the value is not updated

        :param kwargs: dict of class inputs
        :type kwargs: any type that can be typecast to string
        """
        kwargs = {k.upper(): v for k, v in kwargs.items()}  #convert kwarg names to uppercase. Allows for use with XML and editor attributes
        if 'RES_X' in kwargs: self.Res_x = str2dec(kwargs.get('RES_X'))
        if 'RES_Y' in kwargs: self.Res_y = str2dec(kwargs.get('RES_Y'))
        if 'REFRESH' in kwargs: self.Refresh = str2dec(kwargs.get('REFRESH'))
        if 'BAKLITE' in kwargs: self.Baklite = str2dec(kwargs.get('BAKLITE'))
    
    def dashCFG_checkErrs(self):
        """function checks the required class attributes to see if they are set and if the set value is
        a correct format and/or reference. If it is not set, or the value is not correct for the configuration,
        then the attribute name, and an error message are added to the temporary error dict. Once complete
        this error dict is passed to the custom warning window message to indicate where in a dash configuration
        there may be issues.
        
        :returns: dict of attributes with errors
        :rtype: `dictionary` {attribute_name:"error message"}
        """
        tmp_err_list = []   #temp list for compiling errors

        for att, val in self.__dict__.items():  #loop through all attributes
            if val is None or val == '':
                tmp_err_list.append(create_err_msg('Dash CFG','Core',att+'-Value is required and not defined'))

        return tmp_err_list

class Label_Static:
    def __init__(self):
        """Configuration class for static label types"""
        self.text = None            #label text
        self.x0 = None              #position - X0
        self.y0 = None              #position - Y0
        self.fill = None            #foreground (fill) color
        self.name = None            #label name
        self.font = None            #Named font for label (see themes class)
        self.pad = None             #text is padded
        self.clr_bg = None          #foreground color        

        #-----ref vars
        self.master_ref = None      #reference back to the master window > needed for theme and font transformations
        self.canv_ref = None        #reference to the canvas instance object is drawn on
        self.objID = None           #self canvas object reference ID
        self.padID = None           #background padding object reference ID

        #--create tupple for class attributes used to save editor XML file
        self.fields_editorCFG = ('text', 'x0', 'y0', 'fill', 'font', 'pad', 'clr_bg')

        #--create tupple for class attributes used to generate dash config file
        self.fields_dashCFG = self.fields_editorCFG
    
    def init_config(self, kwargs):
        """function sets the initial element configuration values based on the passed kwargs. This is
        typically used when instancing a new element.
        
        :param kwargs: element attributes to update
        :type kwargs: `dict` formatted {kwarg_name:value}
        """
        kwargs = {k.upper(): v for k, v in kwargs.items()}  #convert kwarg names to uppercase. Allows for use with XML and editor attributes
        self.text = kwargs.get('TEXT', None)
        self.x0 = str2dec(kwargs.get('X0', 0))
        self.y0 = str2dec(kwargs.get('Y0', 0)) 
        self.fill = kwargs.get('FILL', False)
        self.name = kwargs.get('NAME', None)
        self.font = kwargs.get('FONT', None) 
        self.pad = str2bool(kwargs.get('PAD', False))
        self.clr_bg = kwargs.get('CLR_BG', False)

    def upd_config(self, kwargs):
        """function updates element configuration values based on the passed kwargs.
        
        :param kwargs: element attributes to update
        :type kwargs: `dict` formatted {kwarg_name:value}
        """
        self.__dict__.update(kwargs)                    #update config
    
    def get_edtr_wgt_kwargs(self, inc_pad=True):
        """function gets the kwargs required to create or update the editor canvas object. Returns a dict of
        parameters that's typically used to pass to tkinter functions. Optionally can include the background
        pad argument (not always used).
        
        :param inc_pad: (optional) include "background pad" arg in returned dict - Default true
        :type inc_pad: `bool` - true to include pad parameter
        :returns: dict of element kwargs
        :rtype: `dictionary` {element_kwarg_name:value}
        """
        #--shorthand refs for theme items
        thm_clrs = self.master_ref.dash_theme.colors
        thm_fnts = self.master_ref.dash_theme.fonts
        
        #--build dict with all kwargs needed to create or update editor widget
        out_kwargs = {'x0': self.x0,
                      'y0': self.y0,
                      'text': self.text,
                      'fill': thm_clrs[self.fill],          #transform from keyword to color HEX code
                      'font': thm_fnts[self.font],          #transform from font name to tuple
                      'anchor':tk.NW}

        if inc_pad == True:                     #include pad kwags with output
            try: color = thm_clrs[self.clr_bg]  #if a valid color is defined, go get it
            except: color = None                    #otherwise assign "None"
            out_kwargs.update({'pad':self.pad,
                               'clr_bg': color})
                    
        return out_kwargs   #retun the complete kwarg dict

    def dashCFG_checkErrs(self, pg_name):
        """function checks the required class attributes to see if they are set and if the set value is
        a correct format and/or reference. If it is not set, or the value is not correct for the configuration,
        then the attribute name, and an error message are added to the temporary error dict. Once complete
        this error dict is passed to the custom warning window message to indicate where in a dash configuration
        there may be issues.
        
        :param pg_name: the dash page which the element is contained on - makes for a better error message fi needed
        :type pg_name: `string`
        :returns: dict of attributes with errors
        :rtype: `dictionary` {attribute_name:"error message"}
        """
        tmp_err_list = []   #temp list for compiling errors

        for attr, val in self.__dict__.items():
            if attr in self.fields_dashCFG:
                if ((attr == 'text') or (attr == 'x0') or (attr == 'y0')):
                    if (val is None) or val == '':
                        tmp_err_list.append(create_err_msg('Page',self.name,'attr-'+attr+'-required and is undefined'))
                elif attr == 'font':
                    if not self.master_ref.dash_theme.chk_exist_fonts(val):
                        tmp_err_list.append(create_err_msg('Page',self.name,'label font-'+val+'-not defined in theme'))
                elif attr == 'fill':
                    if not self.master_ref.dash_theme.chk_exist_colors(val):
                        tmp_err_list.append(create_err_msg('Page',self.name,'color-'+val+'-not defined in theme'))
                elif attr == 'pad':
                    if (val is None) or val == '':
                        tmp_err_list.append(create_err_msg('Page',self.name,'attr-'+attr+'-required and is undefined'))
                    if val == True and not self.master_ref.dash_theme.chk_exist_colors(self.clr_bg):
                        tmp_err_list.append(create_err_msg('Page',self.name,'color-'+self.clr_bg+'-not defined in theme'))

        return tmp_err_list

class Label_Data:
    def __init__(self):
        '''Configuration class for data label types'''
        self.x0 = None              #position - X0
        self.y0 = None              #position - Y0
        self.fill = None            #foreground (fill) color
        self.font = None            #Named font for label (see themes class)
        self.name = None            #label name
        self.data_ch = None         #Named data channel (see CAN class)
        self.sigdig = None          #significant digits to display
        self.pad = None             #text is padded
        self.clr_bg = None          #foreground color
        self.warn_en = None         #warning is enabled
        self.lim_DngrLo = None      #danger low limit
        self.lim_WarnLo = None      #warning low limit
        self.lim_WarnHi = None      #warning high limit
        self.lim_DngrHi = None      #danger high limit

        #-----ref vars
        self.master_ref = None      #reference back to the master window > needed for theme and font transformations
        self.canv_ref = None        #reference to the canvas instance object is drawn on
        self.objID = None           #self canvas object reference ID
        self.padID = None           #background padding object reference ID
        self.CAN_dec_ref = None     #refernece back to the CAN data instance decimal value that widget is based on

        #--create tupple for class attributes used to save editor XML file
        self.fields_editorCFG = ('x0', 'y0', 'fill', 'font', 'max_val', 'data_ch', 'pad', 'clr_bg', 'warn_en', 'lim_DngrLo', 'lim_WarnLo', 'lim_WarnHi', 'lim_DngrHi')

        #--create tupple for class attributes used to generate dash config file
        self.fields_dashCFG = ('x0', 'y0', 'fill', 'font', 'data_ch', 'pad', 'clr_bg', 'warn_en', 'lim_DngrLo', 'lim_WarnLo', 'lim_WarnHi', 'lim_DngrHi')
    
    def init_config(self, kwargs):
        """function sets the initial element configuration values based on the passed kwargs. This is
        typically used when instancing a new element.
        
        :param kwargs: element attributes to update
        :type kwargs: `dict` formatted {kwarg_name:value}
        """
        kwargs = {k.upper(): v for k, v in kwargs.items()}  #convert kwarg names to uppercase. Allows for use with XML and editor attributes
        self.x0 = str2dec(kwargs.get('X0', 0))
        self.y0 = str2dec(kwargs.get('Y0', 0))
        self.fill = kwargs.get('CLR_FG', kwargs.get('FILL', False))
        self.font = kwargs.get('FONT', None)
        self.name = kwargs.get('NAME', None)
        self.data_ch = kwargs.get('DATA_CH', None)
        self.sigdig = kwargs.get('SIGDIG', sys_dat_sigdig)
        self.pad = str2bool(kwargs.get('PAD', False))
        self.clr_bg = kwargs.get('CLR_BG', False)
        self.warn_en = str2bool(kwargs.get('WARN_EN', None))
        self.lim_DngrLo = str2dec(kwargs.get('LIM_DNGRLO', None))
        self.lim_WarnLo = str2dec(kwargs.get('LIM_WARNLO', None))
        self.lim_WarnHi = str2dec(kwargs.get('LIM_WARNHI', None))
        self.lim_DngrHi = str2dec(kwargs.get('LIM_DNGRHI', None))
    
    def upd_config(self, kwargs):
        """function updates element configuration values based on the passed kwargs.
        
        :param kwargs: element attributes to update
        :type kwargs: `dict` formatted {kwarg_name:value}
        """
        self.__dict__.update(kwargs)                    #update config

    def get_edtr_wgt_kwargs(self, inc_pad=True):
        """function gets the kwargs required to create or update the editor canvas object. Returns a dict of
        parameters that's typically used to pass to tkinter functions. Optionally can include the background
        pad argument (not always used).
        
        :param inc_pad: (optional) include "background pad" arg in returned dict - Default true
        :type inc_pad: `bool` - true to include pad parameter
        :returns: dict of element kwargs
        :rtype: `dictionary` {element_kwarg_name:value}
        """
        #--shorthand refs for theme items
        thm_clrs = self.master_ref.dash_theme.colors
        thm_fnts = self.master_ref.dash_theme.fonts
        
        #--build dict with all kwargs needed to create or update editor widget
        out_kwargs = {'x0': self.x0,
                      'y0': self.y0,
                      'fill': thm_clrs[self.fill],          #transform from keyword to color HEX code
                      'font': thm_fnts[self.font],          #transform from font name to tuple
                      'anchor':tk.NW}

        if inc_pad == True:                     #include pad kwags with output
            try: color = thm_clrs[self.clr_bg]  #if a valid color is defined, go get it
            except: color = None                    #otherwise assign "None"
            out_kwargs.update({'pad':self.pad,
                               'clr_bg': color})
        
        return out_kwargs   #retun the complete kwarg dict

    def dashCFG_checkErrs(self, pg_name):
        """function checks the required class attributes to see if they are set and if the set value is
        a correct format and/or reference. If it is not set, or the value is not correct for the configuration,
        then the attribute name, and an error message are added to the temporary error dict. Once complete
        this error dict is passed to the custom warning window message to indicate where in a dash configuration
        there may be issues.
        
        :param pg_name: the dash page which the element is contained on - makes for a better error message fi needed
        :type pg_name: `string`
        :returns: dict of attributes with errors
        :rtype: `dictionary` {attribute_name:"error message"}
        """
        tmp_err_list = []   #temp list for compiling errors

        for attr, val in self.__dict__.items():
            if attr in self.fields_dashCFG:
                if (attr == 'x0') or (attr == 'y0') or (attr == 'sigdig'):
                    if (val is None) or val == '':
                        tmp_err_list.append(create_err_msg('Page',self.name,'attr-'+attr+'-required and is undefined'))
                elif attr == 'font':
                    if not self.master_ref.dash_theme.chk_exist_fonts(val):
                        tmp_err_list.append(create_err_msg('Page',self.name,'label font-'+val+'-not defined in theme'))
                elif attr == 'fill':
                    if not self.master_ref.dash_theme.chk_exist_colors(val):
                        tmp_err_list.append(create_err_msg('Page',self.name,'color-'+val+'-not defined in theme'))
                elif attr == 'data_ch':
                    if not self.master_ref.dash_CAN.chk_exist_CANch(val):
                        tmp_err_list.append(create_err_msg('Page',self.name,'CANch-'+val+'-not defined'))
                elif attr == 'pad':
                    if (val is None) or val == '':
                        tmp_err_list.append(create_err_msg('Page',self.name,'attr-'+attr+'-required and is undefined'))
                    if val == True and not self.master_ref.dash_theme.chk_exist_colors(self.clr_bg):
                        tmp_err_list.append(create_err_msg('Page',self.name,'color-'+self.clr_bg+'-not defined in theme'))
                elif attr == 'warn_en':
                    if (val is None) or val == '':
                        tmp_err_list.append(create_err_msg('Page',self.name,'attr-'+attr+'-required and is undefined'))
                    if val == True:
                        if self.lim_DngrLo is None or self.lim_DngrLo == '':
                            tmp_err_list.append(create_err_msg('Page',self.name,'color for Limit_Danger_Lo not defined in theme'))
                        if self.lim_WarnLo is None or self.lim_WarnLo == '':
                            tmp_err_list.append(create_err_msg('Page',self.name,'color for Limit_Warn_Lo not defined in theme'))
                        if self.lim_WarnHi is None or self.lim_WarnHi == '':
                            tmp_err_list.append(create_err_msg('Page',self.name,'color for Limit_Warn_Hi not defined in theme'))
                        if self.lim_DngrHi is None or self.lim_DngrHi == '':
                            tmp_err_list.append(create_err_msg('Page',self.name,'color for Limit_Danger_Hi not defined in theme'))

        return tmp_err_list
    
    def update_state(self, var, indx, mode):
        """function updates the state of the dash element. Typically called when
        new CAN data that controls the widget is received
        
        :param var_name: (not used) - variable trace related value
        :param indx: (not used) - variable trace related value
        :param mode: (not used) - variable trace related value"""
        thm_ref = self.master_ref.dash_theme            #local ref for dash theme
        thm_clrs = thm_ref.colors                       #local ref for theme colors
        upd_kwargs = {}                                 #temp dict of kwargs to edit/update the displayed widget
        
        new_val = self.CAN_dec_ref.get()                #get current data value
        new_txt = dec2str(new_val, self.sigdig)         #and convert to string
        upd_kwargs.update({'text': new_txt})            #and update text value

        if self.warn_en == True:
            color_attr = get_alert_color(new_val)       #get the current warning attribute
            if color_attr is not None:                  #if alert limit set, set BG and fill colors
                fill_clr_name = thm_clrs[getattr(thm_ref,color_attr)]
                bg_clr_name = thm_clrs[getattr(thm_ref,WarnState_dict['ALRT_FG'])]
            else:                                       #otherwise, use default config values
                fill_clr_name = self.fill
                bg_clr_name = self.clr_bg

            fill_clr = thm_clrs[fill_clr_name]          #get hex code from theme for color
            bg_clr = thm_clrs[bg_clr_name]
            upd_kwargs.update({'fill': fill_clr})       #update fill color
            if self.pad == True:                        #if padded
                self.canv_ref.itemconfigure(self.padID, {'fill':bg_clr})    #update pad object

        self.canv_ref.itemconfigure(self.objID, upd_kwargs)             #update canvas object props
        
class Indicator_Bullet:
    def __init__(self):
        '''Configuration class for bullet indicator types'''
        self.x0 = None              #position - X0
        self.y0 = None              #position - Y0
        self.size = None            #bullet indicator size
        self.name = None            #label name
        self.data_ch = None         #Named linked CAN channel (see CAN class)
        self.lim_lo = None          #low trigger limit
        self.lim_hi = None          #high trigger limit
        self.outln = None           #named outline color (see theme class)
        self.clr_lo = None          #(fill) color - low trigger
        self.clr_hi = None          #(fill) color - hi trigger

        #-----ref vars
        self.master_ref = None      #reference back to the master window > needed for theme and font transformations
        self.canv_ref = None        #reference to the canvas instance object is drawn on
        self.objID = None           #canvas object reference ID - once created
        self.CAN_dec_ref = None     #refernece back to the CAN data instance decimal value that widget is based on

        #--create tupple for class attributes used to save editor XML file
        self.fields_editorCFG = ('x0', 'y0', 'fill', 'size', 'data_ch', 'outln', 'ind_on', 'ind_off', 'warn_en', 'lim_DngrLo', 'lim_WarnLo', 'lim_WarnHi', 'lim_DngrHi')

        #--create tupple for class attributes used to generate dash config file
        self.fields_dashCFG = self.fields_editorCFG
    
    def init_config(self, kwargs):
        """function sets the initial element configuration values based on the passed kwargs. This is
        typically used when instancing a new element.
        
        :param kwargs: element attributes to update
        :type kwargs: `dict` formatted {kwarg_name:value}
        """
        kwargs = {k.upper(): v for k, v in kwargs.items()}      #convert kwarg names to uppercase. Allows for use with XML and editor attributes
        self.x0 = str2dec(kwargs.get('X0', 0))
        self.y0 = str2dec(kwargs.get('Y0', 0))
        self.size = str2dec(kwargs.get('SIZE', None))
        self.name = kwargs.get('NAME', None)
        self.data_ch = kwargs.get('DATA_CH', None)
        self.lim_lo = str2dec(kwargs.get('LIM_LO', None))
        self.lim_hi = str2dec(kwargs.get('LIM_HI', None))
        self.outln = kwargs.get('OUTLN', None)
        self.clr_lo = kwargs.get('CLR_LO', None)
        self.clr_hi = kwargs.get('CLR_HI', None)
    
    def upd_config(self, kwargs):
        """function updates element configuration values based on the passed kwargs.
        
        :param kwargs: element attributes to update
        :type kwargs: `dict` formatted {kwarg_name:value}
        """
        self.__dict__.update(kwargs)                    #update config

    def get_edtr_wgt_kwargs(self):
        """function gets the kwargs required to create or update the editor canvas object. Returns a dict of
        parameters that's typically used to pass to tkinter functions. Optionally can include the background
        pad argument (not always used).
        
        :param inc_pad: (optional) include "background pad" arg in returned dict - Default true
        :type inc_pad: `bool` - true to include pad parameter
        :returns: dict of element kwargs
        :rtype: `dictionary` {element_kwarg_name:value}
        """
        #--shorthand refs for theme items
        thm_clrs = self.master_ref.dash_theme.colors
        
        #--build dict with all kwargs needed to create or update editor widget
        out_kwargs = {'x0': self.x0,
                      'y0': self.y0,
                      'x1': self.x0 + self.size,
                      'y1': self.y0 + self.size,
                      'fill': thm_clrs[self.clr_lo],    #transform from keyword to color HEX code
                      'outline': thm_clrs[self.outln]}  #transform from keyword to color HEX code
        
        return out_kwargs   #retun the complete kwarg dict

    def dashCFG_checkErrs(self, pg_name):
        """function checks the required class attributes to see if they are set and if the set value is
        a correct format and/or reference. If it is not set, or the value is not correct for the configuration,
        then the attribute name, and an error message are added to the temporary error dict. Once complete
        this error dict is passed to the custom warning window message to indicate where in a dash configuration
        there may be issues.
        
        :param pg_name: the dash page which the element is contained on - makes for a better error message fi needed
        :type pg_name: `string`
        :returns: dict of attributes with errors
        :rtype: `dictionary` {attribute_name:"error message"}
        """
        tmp_err_list = []   #temp list for compiling errors

        for attr, val in self.__dict__.items():
            if attr in self.fields_dashCFG:
                if (attr == 'x0') or (attr == 'y0') or (attr == 'size') or (attr =='lim_lo') or (attr == 'lim_hi'):
                    if (val is None) or val == '':
                        tmp_err_list.append(create_err_msg('Page',self.name,'attr-'+attr+'-required and is undefined'))
                elif (attr == 'outln') or (attr == 'clr_lo') or (attr == 'clr_hi'):
                    if not self.master_ref.dash_theme.chk_exist_colors(val):
                        tmp_err_list.append(create_err_msg('Page',self.name,'color-'+val+'-not defined in theme'))
                elif attr == 'data_ch':
                    if not self.master_ref.dash_CAN.chk_exist_CANch(val):
                        tmp_err_list.append(create_err_msg('Page',self.name,'CANch-'+val+'-not defined'))
                elif attr == 'warn_en':
                    if (val is None) or val == '':
                        tmp_err_list.append(create_err_msg('Page',self.name,'attr-'+attr+'-required and is undefined'))
                    if val == True:
                        if self.lim_DngrLo is None or self.lim_DngrLo == '':
                            tmp_err_list.append(create_err_msg('Page',self.name,'color for Limit_Danger_Lo not defined in theme'))
                        if self.lim_WarnLo is None or self.lim_WarnLo == '':
                            tmp_err_list.append(create_err_msg('Page',self.name,'color for Limit_Warn_Lo not defined in theme'))
                        if self.lim_WarnHi is None or self.lim_WarnHi == '':
                            tmp_err_list.append(create_err_msg('Page',self.name,'color for Limit_Warn_Hi not defined in theme'))
                        if self.lim_DngrHi is None or self.lim_DngrHi == '':
                            tmp_err_list.append(create_err_msg('Page',self.name,'color for Limit_Danger_Hi not defined in theme'))

        return tmp_err_list
    
    def update_state(self, var, indx, mode):
        """function updates the state of the dash element. Typically called when
        new CAN data that controls the widget is received
        
        :param var_name: (not used) - variable trace related value
        :param indx: (not used) - variable trace related value
        :param mode: (not used) - variable trace related value"""
        thm_ref = self.master_ref.dash_theme            #local ref for dash theme
        thm_clrs = thm_ref.colors                       #local ref for theme colors
        upd_kwargs = {}                                 #temp dict of kwargs to edit/update the displayed widget
        
        new_val = self.CAN_dec_ref.get()                #get current data value
        
        #--check fill state
        if new_val > self.lim_hi:                       #if above the "high" limit
            upd_kwargs.update({'fill': thm_clrs[self.clr_hi]})  #update fill color
        elif new_val < self.lim_lo:                     #or below the "low" limit
            upd_kwargs.update({'fill': thm_clrs[self.clr_lo]})  #update fill color

        self.canv_ref.itemconfigure(self.objID, upd_kwargs)     #update canvas object props

class Indicator_Bar:
    def __init__(self):
        '''Configuration class for bar indicator types'''
        self.x0 = None              #position - X0 : This value never changes
        self.y0 = None              #position - Y0 : This value never changes
        self.x1 = None              #position - X1 : This value never changes
        self.y1 = None              #position - Y1 : value changes based on current value and scale lo/hi
        self.width = None           #bar width : This value never changes
        self.height = None          #bar height : This value never changes
        self.fill = None            #foreground (fill) color
        self.outln = None           #named outline color (see theme class)
        self.name = None            #label name
        self.data_ch = None         #Named linked CAN channel (see CAN class)
        self.ordr = None            #layer order (FG or BG)
        self.scale_lo = None        #lower bound of scale
        self.scale_hi = None        #upper bound of scale
        self.warn_en = None         #warning is enabled
        self.lim_DngrLo = None      #danger low limit
        self.lim_WarnLo = None      #warning low limit
        self.lim_WarnHi = None      #warning high limit
        self.lim_DngrHi = None      #danger high limit

        #-----ref vars
        self.master_ref = None      #reference back to the master window > needed for theme and font transformations
        self.canv_ref = None        #reference to the canvas instance object is drawn on
        self.objID = None           #canvas object reference ID - once created
        self.CAN_dec_ref = None     #refernece back to the CAN data instance decimal value that widget is based on

        #--create tupple for class attributes used to save editor XML file
        self.fields_editorCFG = ('x0', 'y0', 'width', 'height', 'fill', 'data_ch', 'outln', 'ordr', 'scale_lo', 'scale_hi', 'warn_en', 'lim_DngrLo', 'lim_WarnLo', 'lim_WarnHi', 'lim_DngrHi')

        #--create tupple for class attributes used to generate dash config file
        self.fields_dashCFG = self.fields_editorCFG
    
    def init_config(self, kwargs):
        """function sets the initial element configuration values based on the passed kwargs. This is
        typically used when instancing a new element.
        
        :param kwargs: element attributes to update
        :type kwargs: `dict` formatted {kwarg_name:value}
        """
        kwargs = {k.upper(): v for k, v in kwargs.items()}      #convert kwarg names to uppercase. Allows for use with XML and editor attributes
        self.x0 = str2dec(kwargs.get('X0', 0))
        self.y0 = str2dec(kwargs.get('Y0', 0))
        self.width = str2dec(kwargs.get('WIDTH', None))
        self.height = str2dec(kwargs.get('HEIGHT', None))
        self.x1 = self.x0 + self.width
        self.y1 = self.y0 + self.height
        self.fill = kwargs.get('FILL', None)
        self.outln = kwargs.get('OUTLN', None)
        self.name = kwargs.get('NAME', None)
        self.data_ch = kwargs.get('DATA_CH', None)
        self.ordr = kwargs.get('ORDR', 'FG')
        self.scale_lo = str2dec(kwargs.get('SCALE_LO', None))
        self.scale_hi = str2dec(kwargs.get('SCALE_HI', None))
        self.warn_en = str2bool(kwargs.get('WARN_EN', None))
        self.lim_DngrLo = str2dec(kwargs.get('LIM_DNGRLO', None))
        self.lim_WarnLo = str2dec(kwargs.get('LIM_WARNLO', None))
        self.lim_WarnHi = str2dec(kwargs.get('LIM_WARNHI', None))
        self.lim_DngrHi = str2dec(kwargs.get('LIM_DNGRHI', None))
    
    def upd_config(self, kwargs):
        """function updates element configuration values based on the passed kwargs.
        
        :param kwargs: element attributes to update
        :type kwargs: `dict` formatted {kwarg_name:value}
        """
        self.__dict__.update(kwargs)                    #update config

    def get_edtr_wgt_kwargs(self):
        """function gets the kwargs required to create or update the editor canvas object. Returns a dict of
        parameters that's typically used to pass to tkinter functions. Optionally can include the background
        pad argument (not always used).
        
        :param inc_pad: (optional) include "background pad" arg in returned dict - Default true
        :type inc_pad: `bool` - true to include pad parameter
        :returns: dict of element kwargs
        :rtype: `dictionary` {element_kwarg_name:value}
        """
        #--shorthand refs for theme items
        thm_clrs = self.master_ref.dash_theme.colors
        
        #--build dict with all kwargs needed to create or update editor widget
        out_kwargs = {'x0': self.x0,
                      'y0': self.y0,
                      'x1': self.x1,
                      'y1': self.y1,
                      'fill': thm_clrs[self.fill],          #transform from keyword to color HEX code
                      'outline': thm_clrs[self.outln]}    #transform from keyword to color HEX code
        
        return out_kwargs   #retun the complete kwarg dict

    def dashCFG_checkErrs(self, pg_name):
        """function checks the required class attributes to see if they are set and if the set value is
        a correct format and/or reference. If it is not set, or the value is not correct for the configuration,
        then the attribute name, and an error message are added to the temporary error dict. Once complete
        this error dict is passed to the custom warning window message to indicate where in a dash configuration
        there may be issues.
        
        :param pg_name: the dash page which the element is contained on - makes for a better error message fi needed
        :type pg_name: `string`
        :returns: dict of attributes with errors
        :rtype: `dictionary` {attribute_name:"error message"}
        """
        tmp_err_list = []   #temp list for compiling errors

        for attr, val in self.__dict__.items():
            if attr in self.fields_dashCFG:
                if (attr == 'x0') or (attr == 'y0') or (attr == 'width') or (attr == 'height') or (attr =='ind_on') or (attr == 'ind_off') or (attr == 'ordr') or (attr == 'scale_lo') or (attr == 'scale_hi'):
                    if (val is None) or val == '':
                        tmp_err_list.append(create_err_msg('Page',self.name,'attr-'+attr+'-required and is undefined'))
                elif attr == 'fill':
                    if not self.master_ref.dash_theme.chk_exist_colors(val):
                        tmp_err_list.append(create_err_msg('Page',self.name,'color-'+val+'-not defined in theme'))
                elif attr == 'data_ch':
                    if not self.master_ref.dash_CAN.chk_exist_CANch(val):
                        tmp_err_list.append(create_err_msg('Page',self.name,'CANch-'+val+'-not defined'))
                elif attr == 'warn_en':
                    if (val is None) or val == '':
                        tmp_err_list.append(create_err_msg('Page',self.name,'attr-'+attr+'-required and is undefined'))
                    if val == True:
                        if self.lim_DngrLo is None or self.lim_DngrLo == '':
                            tmp_err_list.append(create_err_msg('Page',self.name,'color for Limit_Danger_Lo not defined in theme'))
                        if self.lim_WarnLo is None or self.lim_WarnLo == '':
                            tmp_err_list.append(create_err_msg('Page',self.name,'color for Limit_Warn_Lo not defined in theme'))
                        if self.lim_WarnHi is None or self.lim_WarnHi == '':
                            tmp_err_list.append(create_err_msg('Page',self.name,'color for Limit_Warn_Hi not defined in theme'))
                        if self.lim_DngrHi is None or self.lim_DngrHi == '':
                            tmp_err_list.append(create_err_msg('Page',self.name,'color for Limit_Danger_Hi not defined in theme'))

        return tmp_err_list
    
    def update_state(self, var, indx, mode):
        """function updates the state of the dash element. Typically called when
        new CAN data that controls the widget is received
        
        :param var_name: (not used) - variable trace related value
        :param indx: (not used) - variable trace related value
        :param mode: (not used) - variable trace related value"""
        thm_ref = self.master_ref.dash_theme            #local ref for dash theme
        thm_clrs = thm_ref.colors                       #local ref for theme colors
        upd_kwargs = {}                                 #temp dict of kwargs to edit/update the displayed widget
        
        new_val = self.CAN_dec_ref.get()                #get current data value

        #--calculate new y1 val
        new_y1 = self.y0 + (new_val-self.scale_lo)/(self.scale_hi-self.scale_lo)*self.width
        upd_kwargs.update({'y1': new_y1})

        #--check warning limits
        if self.warn_en == True:
            color_attr = get_alert_color(new_val)       #get the current warning attribute
            if color_attr is not None:                  #if alert limit set, set BG and fill colors
                ele_color_name = thm_clrs[getattr(thm_ref,color_attr)]
            else:                                       #otherwise, use default config values
                ele_color_name = self.fill
            ele_color = thm_clrs[ele_color_name]        #get hex code from theme for color
            upd_kwargs.update({'outline': ele_color,
                               'fill':ele_color})       #add fill and outline to color update       

        self.canv_ref.itemconfigure(self.objID, upd_kwargs)     #update canvas object props
