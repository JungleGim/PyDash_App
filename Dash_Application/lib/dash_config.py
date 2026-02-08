"""
File:       dash_config.py
Function:   This file contains any of the functions used for checking, loading, updating, and general
            operations for the PyDash config used in the dash
"""

from .sys import *
from .com_defs import check_file_exists, check_dir_exists, XML_open, create_err_msg
from .com_defs import XMLcfg_types
from .can import CANch
from .com_defs import dash_page_user, Label_Static, Label_Data, Indicator_Bullet, Indicator_Bar, err_message

def check_new_config():
    """function checks if there is a new config available
    
    :returns: true or false if a new dash config is available - True is a new config exists
    :rtype: bool
    """
    return check_file_exists(sys_config_archive)

def check_config_exists():
    """function checks if the dash configuration is present
    
    :returns: true or false if the config exists - True is a new config exists
    :rtype: bool
    """
    return check_file_exists(sys_config_file)

def load_new_config(master_ref):
    """function loads the new config to the PyDash config folder. Current dash config is
    removed and the new config from the archive is extracted to the folder. Additionally,
    the new config archive is deleted once extracted
    """
    if check_file_exists(sys_config_archive):       #check if config archive exists
        #NOTE: file should exist if this function is called but still a good error check just in case
        try:
            if check_dir_exists(sys_config_dir) == True:                #if config directory exists
                shutil.rmtree(sys_config_dir)                           #remove config directory and all its contents (old config)
        except:
            master_ref.upd_errors([create_err_msg('FileSys','CFG Dir','Error rem cfg dir for new cfg.')])
        try:
            os.mkdir(sys_config_dir)                                    #remake empty config directory
        except:
            master_ref.upd_errors([create_err_msg('FileSys','CFG Dir','Error creating cfg dir for new cfg.')])
        try:
            shutil.unpack_archive(sys_config_archive, sys_config_dir)   #extract new config to directory
            os.remove(sys_config_archive)                               #remove config archive
        except:
            master_ref.upd_errors([create_err_msg('FileSys','CFG Dir','Error extracting ZIP for new cfg.')])
    else:
        master_ref.upd_errors([create_err_msg('FileSys','CFG Dir','Unknown error extracting new cfg')])

def dashCFG_load(master_ref):
    """Function loads the dash config XML file to populate the various data classes
    
    :param master_ref: reference back to the main/master window
    :type master_ref: main `tk.window` ref
    """   
    xmlFile_ET = XML_open(master_ref, sys_config_file)              #open the config file 
    if xmlFile_ET is not None: parseXML(master_ref, xmlFile_ET)     #if successful, then start parsing the contents
    
def dashCFG_ErrChk(master_ref):
    err_msgs = []   #temp list for compiled error messages    
    
    dash_err = master_ref.dash_settings.dashCFG_checkErrs()     #check core config errors
    can_err = master_ref.dash_CAN.dashCFG_checkErrs()           #check for CAN config errors
    theme_err = master_ref.dash_theme.dashCFG_checkErrs()       #check for theme errors
    #--update temp list
    if dash_err:
        for err in dash_err: err_msgs.append(err)
    if can_err: 
        for err in can_err: err_msgs.append(err)
    if theme_err: 
        for err in theme_err: err_msgs.append(err)

    for pg in master_ref.dash_pages_user.values():              #cycle through all defined pages
        page_err = pg.dashCFG_checkErrs()                           #and check for core page and individual element errors    
        if page_err:
            for err in page_err: err_msgs.append(err)

    master_ref.upd_errors(err_msgs) #append all error messages

def parseXML(master_ref, config_tree):
    """function serves as the primary function for parsing an XML file. The passed element tree
    of the opened file is split into its various defined sections related to the PyDash configuration. Individual
    functions are then called to prase and convert the XML file into the internal class structure for
    storing and editing information. When done, the "buildPages" funciton is also called to generate the core
    editor configuration.
    
    :param master_ref: reference back to the main/master window
    :type master_ref: main `tk.window` ref
    :param config_tree: opened XML file element tree
    :type config_tree: XML ET.file() object
    """
    config_root = config_tree.getroot()             #get root element

    #--parse XML file blocks for various dash config options
    parseXML_CORE(master_ref, config_root.find(XMLcfg_types['DISP']))       #cycle through DISPLAY (core) config
    parseXML_THEME(master_ref, config_root.find(XMLcfg_types['THEME']))     #cycle through THEME config
    parseXML_CAN(master_ref, config_root.find(XMLcfg_types['CAN']))         #cycle through CAN channels config
    parseXML_PAGES(master_ref, config_root.find(XMLcfg_types['FRAMES']))    #cycle through page definitions

def parseXML_CORE(master_ref, block):
    """function parses the core config information for a PyDash editor file
    
    :param master_ref: reference back to the main/master window
    :type master_ref: main `tk.window` ref
    :param block: XML element tree specific to the read config class, IE the "theme" block or the "CAN" block
    :type block: XML ET.file() object
    """
    tmp_config = master_ref.dash_settings               #shorthand ref for config being updated
    read_DISPconfig = {}                                #temp dict for read values
    
    for cfg in block:                                   #cycle through all the config values
        read_DISPconfig.update({cfg.tag : cfg.text})        #append to temp dict
    tmp_config.upd_cfg(**read_DISPconfig)               #update main definition with read values

def parseXML_THEME(master_ref, block):
    """function parses the theme config information for a PyDash editor file
    
    :param master_ref: reference back to the main/master window
    :type master_ref: main `tk.window` ref
    :param block: XML element tree specific to the read config class, IE the "theme" block or the "CAN" block
    :type block: XML ET.file() object
    """
    tmp_theme = master_ref.dash_theme           #shorthand ref for config being updated
    for clrs in block.findall('COLORS'):        #read all colors
        read_colors = {}                            #temp colors dict for read values
        for clr in clrs.findall('COLOR'):           #cycle through all parsed colors
            read_colors.update({clr.attrib.get('NAME') : clr.text})     #append color to temp dict
        tmp_theme.set_colors(read_colors)           #set theme colors
    for fnts in block.findall('FONTS'):         #read all fonts
        read_fnts = {}                              #temp fonts dict for read values
        for fnt in fnts.findall('FONT'):            #cycle through all parsed fonts
            read_fnts.update({fnt.attrib.get('NAME') : fnt.text})  #append font to temp dict
        tmp_theme.set_fonts(read_fnts)              #set theme fonts
    for imgs in block.findall('IMAGES'):        #read all images
        read_imgs = {}                              #temp dict for read images
        for img in imgs.findall('IMG'):             #cycle through all parsed images
            read_imgs.update({img.attrib.get('NAME') : img.text})   #append image to temp dict
        tmp_theme.set_imgs(read_imgs)               #set theme images
    for alert in block.findall('ALERT_COLORS'): #read all alert colors
        alert_colors = {}                           #temp dict for read alert color settings
        for alrt_color in alert:                    #read all alert colors
            alert_colors.update({alrt_color.tag:alrt_color.text}) #append to temp dict
        tmp_theme.set_alert_colors(alert_colors)    #set the alert colors
    
    tmp_theme.convert_init_fnt_tup()                #convert all the font (string format) tupples to be correct format
    tmp_theme.convert_init_img_path()               #convert all the images to their full path
   
def parseXML_CAN(master_ref, block):
    """function parses the CAN config information for a PyDash editor file
    
    :param master_ref: reference back to the main/master window
    :type master_ref: main `tk.window` ref
    :param block: XML element tree specific to the read config class, IE the "theme" block or the "CAN" block
    :type block: XML ET.file() object
    :param master_ref: reference back to the main/master window
    :type master_ref: main `tk.window` ref
    """
    tmp_CAN = master_ref.dash_CAN                       #shorthand ref for config being updated
    #--get core config values
    CAN_coreCFG = {}                                    #temp dict for CAN core CFG values 
    for canCFG in block.findall('CORE'):
        for cfg in canCFG:
            CAN_coreCFG.update({cfg.tag : cfg.text})    #append to temp dict
    tmp_CAN.set_cfg(**CAN_coreCFG)                      #set core CAN config
    
    #--get CAN data channels
    for chs in block.findall('CHANNELS'):
        read_CAN_data = {}                                              #temp CANch property dict for read values
        read_CAN_ch = {}                                                #temp CANch array for read values

        for ch in chs.findall('CH'):                                    #cycle through all defined channels
            read_CAN_data.update({'NAME' : ch.attrib.get('NAME')})      #append CANch Name to temp dict
            for ch_props in ch:
                read_CAN_data.update({ch_props.tag : ch_props.text})    #append CANch props to temp dict
            tmp_ch = CANch(tmp_CAN.CANbus)                              #create temp CAN channel
            tmp_ch.set_cfg(**read_CAN_data)                             #update config
            read_CAN_ch.update({ch.attrib.get('NAME'): tmp_ch})         #append CANch data to temp dict
        
        tmp_CAN.CAN_add_channels(read_CAN_ch)                           #update CAN master with all the read channels

def parseXML_PAGES(master_ref, block):
    """function parses the page config information for a PyDash editor file.
    
    :param master_ref: reference back to the main/master window
    :type master_ref: main `tk.window` ref
    :param block: XML element tree specific to the read config class, IE the "theme" block or the "CAN" block
    :type block: XML ET.file() object
    """
    tmp_cfg_pages = master_ref.dash_pages_user  #temp dict for user pages
    for child in block:
        read_frame_props = {}                   #temp page prop dict for core page props
        read_frame_props.update({'NAME' : child.attrib.get('NAME')})
        for atrb in child:                      #for each page
            if atrb.tag != 'ELM':
                read_frame_props.update({atrb.tag : atrb.text})

        read_frame = dash_page_user(master_ref) #instance read frame
        read_frame.set_cfg(**read_frame_props)  #set the properties
        read_frame_props.clear()                #clear temp dict

        for elmnts in child.findall('ELM'):     #elements in page
            read_elm = {}                       #temp element dict for all read elements
            read_lbl = {}                       #temp static label element dict
            for lbl_static in elmnts.findall('LBL_STATIC'):            
                for lbl in lbl_static:
                    read_lbl.update({'NAME' : lbl.attrib.get('NAME')})
                    for atributes in lbl:
                        read_lbl.update({atributes.tag : atributes.text})
                    tmp_stat_ele = Label_Static()                               #instance element
                    tmp_stat_ele.init_config(read_lbl)                          #set its config
                    tmp_stat_ele.master_ref = master_ref                        #set reference to main window
                    read_elm.update({lbl.attrib.get('NAME') : tmp_stat_ele})    #append static label to read elements
            read_lbl.clear()                    #clear temp dict
            for lbl_data in elmnts.findall('LBL_DATA'):
                for lbl in lbl_data:
                    read_lbl.update({'NAME' : lbl.attrib.get('NAME')})
                    for atributes in lbl:
                        read_lbl.update({atributes.tag : atributes.text})
                    tmp_dat_ele = Label_Data()                                  #instance element
                    tmp_dat_ele.init_config(read_lbl)                           #set its config
                    tmp_dat_ele.master_ref = master_ref                         #set reference to main window
                    read_elm.update({lbl.attrib.get('NAME') : tmp_dat_ele})     #append data labels to read elements
            read_lbl.clear() #clear temp dict
            for lbl_data in elmnts.findall('IND_BLT'):
                for lbl in lbl_data:
                    read_lbl.update({'NAME' : lbl.attrib.get('NAME')})
                    for atributes in lbl:
                        read_lbl.update({atributes.tag : atributes.text})
                    tmp_blt_ele = Indicator_Bullet()                            #instance element
                    tmp_blt_ele.init_config(read_lbl)                           #set its config
                    tmp_blt_ele.master_ref = master_ref                         #set reference to main window
                    read_elm.update({lbl.attrib.get('NAME') : tmp_blt_ele})     #append data labels to read elements
            read_lbl.clear() #clear temp dict
            for lbl_data in elmnts.findall('IND_BAR'):
                for lbl in lbl_data:
                    read_lbl.update({'NAME' : lbl.attrib.get('NAME')})
                    for atributes in lbl:
                        read_lbl.update({atributes.tag : atributes.text})
                    tmp_bar_ele = Indicator_Bar()                               #instance element
                    tmp_bar_ele.init_config(read_lbl)                           #set its config
                    tmp_bar_ele.master_ref = master_ref                         #set reference to main window
                    read_elm.update({lbl.attrib.get('NAME') : tmp_bar_ele})     #append data labels to read elements
            read_lbl.clear() #clear temp dict

        read_frame.update_eleCfg(read_elm)                      #add page elements
        read_elm.clear()                                        #clear temp dict
        tmp_cfg_pages.update({read_frame.name : read_frame})    #add or update page to config dict