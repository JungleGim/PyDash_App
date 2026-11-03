"""
File:       can.py
Function:   This file contains any CAN bus specific classes and methods
"""
from .sys import *
from .com_defs import create_err_msg, str2dec
from .com_defs import err_message

class CANch():
    def __init__(self, CANcore):
        """Construct a CANch data instace. Class includes function for converting RX'd 
        data into meaningful decimal values. Additionally includes tk.DoubleVar() reference 
        for PyDash display widgets to link to for updating on new values.
        
        :param CANbus_master: reference back to the main CANbus instance
        :type CANbus_master: `can` library
        """
        #--references
        self.CANcore_ref = CANcore          #reference back to the core configuration
        self.CANbus_ref = CANcore.CANbus    #reference back to CAN bus instance

        #--channel information
        self.Name = None                #data channel name - will be display name in logfile
        self.AID = None                 #CANbus ID for channel
        self.ext_AID = None             #CANbus AID is extended ID
        self.RTR = False                #remote transmit request required
        self.RTR_freq = None            #RTR frequency in seconds
        self.DLC = None                 #number of expected frames

        #--OBD2 specific channel information
        self.OBD2 = False               #data channel is an OBD2 format channel
        self.OBD2_PID = None            #PID being requested
        self.OBD2_bytes = None          #number of bytes PID will send
        #--non-OBD2 values and conversion information
        self.calc_frames = []           #the frames in the RX'd word to use when calulating the value

        #decimal conversion information
        self.calc_Scalar = None         #the final value scalar when converting frames to decimal
        self.calc_Offset = None         #the decimal offset of the caluclated value

        #--error handling
        self.last_RX = None             #time of the last RX'd data frame
        self.err = False                #flag that channel has an error

        #--misc
        self.log_en = False             #datalogging this channel is enabled
        self.RTR_task = None            #reference to the RTR scheduled task
        self.val_rawCAN = []            #raw RX'd CAN frame data
        self.val_dec = tk.DoubleVar()   #raw CAN frame converted to decimal
    
    def set_cfg(self, **kwargs):
        """ function sets class attributes based on the passed KWARGs.
        All KWARGs have default values non-required core fields. IE, RTR
        has a default field, but AID does not.

        :param kwargs: dict of class inputs
        :type kwargs: any type that can be typecast to string
        """
        kwargs = {k.upper(): v for k, v in kwargs.items()}  #convert kwarg names to uppercase. Allows for use with XML and editor attributes
        self.Name = kwargs.get('NAME', None)
        self.AID = str2dec(kwargs.get('AID', None),16)
        self.ext_AID = kwargs.get('EXT', False)
        self.DLC = str2dec(kwargs.get('DLC', 1))
        self.RTR = kwargs.get('REM_REQ', False)
        if self.RTR == True:                            #if RTR enabled
            self.RTR_freq = kwargs.get('REQ_FREQ', sys_RTR_freq_dflt)    #get RTR frequency
        else: self.RTR_freq = None                      #if not enabled then set to none
       
        self.OBD2 = kwargs.get('OBD2', False)
        self.OBD2_PID = str2dec(kwargs.get('OBD2_PID', None),16)
        self.OBD2_bytes = str2dec(kwargs.get('OBD2_BYTES', None),16)
        
        self.calc_frames = kwargs.get('FRAMES', [1])
        self.calc_Scalar = str2dec(kwargs.get('SCALAR', 1))
        self.calc_Offset = str2dec(kwargs.get('OFFSET', 0))
        self.convert_calc_frames_cfg()                  #convert the read frames value to a usable format

    def convert_calc_frames_cfg(self):
        """function converts from the user-friendly config value that is a string of 1
        index frames to the actual 0 index list that is useful for processing a CAN message"""
        tmp_frames = None   #temp var for frame processing
        if self.calc_frames is not None:
            try: tmp_frames = list(literal_eval(self.calc_frames))  #convert to list
            except: tmp_frames = [literal_eval(self.calc_frames)]   #different conversion if only 1 value
            tmp_frames = [v-1 for v in tmp_frames]                  #decrement each item to conver to 0-based index
        self.calc_frames = tmp_frames                               #set to converted result
    
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
        OBD2_chk = self.OBD2
        for attr, val in self.__dict__.items():
            if attr == 'CANbus_ref' or attr =='last_RX' or attr =='RTR_task':
                continue    #skip, these are not config values
            if OBD2_chk is False:       #normal CAN channel checks
                if attr == 'OBD2' or attr =='OBD2_PID' or attr =='OBD2_bytes':
                    continue    #skip, these are OBD2 specific config values
                if (attr != 'RTR') and (attr != 'RTR_freq') and ((val is None) or val == ''):
                    tmp_err_list.append(create_err_msg('CAN','chCFG-'+self.Name,attr+' undefined'))
                elif attr == 'RTR' and (self.RTR_freq == True) and ((val is None) or val == ''):
                    tmp_err_list.append(create_err_msg('CAN','chCFG-'+self.Name,'RTR is en but no freq defined'))
                elif attr == 'calc_Scalar' and (self.calc_Scalar == 0):
                    tmp_err_list.append(create_err_msg('CAN','chCFG-'+self.Name,'Scalar is 0 - will not be a valid value'))
            elif OBD2_chk is True:      #OBD2 specific config checks
                #TODO: if non-OBD2 attribute, continue
                if attr == 'AID' or attr =='calc_frames':
                    continue    #skip, these are nonOBD2 specific config values
                if self.ext_AID == True:
                    tmp_err_list.append(create_err_msg('CAN','chCFG-'+self.Name,'Extended frame cannot be TRUE for OBD2'))
                if self.DLC != 8:
                    tmp_err_list.append(create_err_msg('CAN','chCFG-'+self.Name,'DLC for OBD2 must be 8'))
                if self.OBD2_bytes == '' or self.OBD2_bytes is None or self.OBD2_bytes < 1:
                    tmp_err_list.append(create_err_msg('CAN','chCFG-'+self.Name,'OBD2 number of bytes is invalid'))
        return tmp_err_list #return error list
    
    def upd_calc_dec(self):
        """function calcualtes the current decimal value based on the
        current rawCAN data frame"""
        tmpval = 0
        msb_indx = 0            #temp most-sig byte index for decimal conversion

        if self.OBD2 == False:  #calculate value for non-OBD2 data
            for frm_indx in self.calc_frames:                       #loop through the defined frames to calcualte
                tmpval += self.val_rawCAN[frm_indx]*(256**msb_indx) #convert the frame to decimal from LSB to MSB
                msb_indx += 1   #increment index
        elif self.OBD2 == True: #calculate value for OBD2 data
            end_byte = sys_OBD2_msgIndx_datMSB + self.bytes         #calculate the end byte based on the expected data length
            for byte in self.val_rawCAN[sys_OBD2_msgIndx_datMSB:end_byte]:  #loop through the data values
                tmpval = (tmpval << 8) | byte                               #and calculate
        
        tmpval *= self.calc_Scalar  #scale raw decimal result
        tmpval += self.calc_Offset  #apply final offset
        self.val_dec.set(round(tmpval,5))    #update doublevar - limit to 5 sigdigs
        
    def CANch_RTR_init(self):
        """function initializes the RTR periodic send task for this data
        channel."""
        req_ID = None               #temp var for the ID to send a request
        if self.OBD2 == False: req_ID=self.AID                          #for a non-OBD2 format - ID field is the address
        elif self.OBD2 == True: req_ID=self.CANcore_ref.OBD2_ECU_IDtx   #for an OBD2 format - use the defined ECUid in CANcore
        
        msg = self.CANbus_ref.Message(  arbitration_id=req_ID,      #bus address to request data from
                                        data=None,                  #RTR data field is empty
                                        is_extended_id=self.ext_AID,#CAN frame config
                                        is_remote_frame=True,       #is a RTR
                                        dlc=self.DLC                #number requested bytes
                                    )
        self.RTR_task = self.CANbus_ref.send_periodic(msg, self.RTR_freq)
    
    def CANch_RTR_start(self):
        """function starts the channel's RTR task"""
        if isinstance(self.RTR_task,can.CyclicSendTaskABC): #if RTR task is defined
            self.RTR_task.start()                           #then start RTR task
    
    def CANch_RTR_stop(self):
        """function stops the channel's RTR task"""
        if isinstance(self.RTR_task,can.CyclicSendTaskABC): #if RTR task is defined
            self.RTR_task.stop()                            #then stop RTR task

class CAN_core():
    def __init__(self, master):
        """Construct the main CAN bus control
        
        :param master: reference back to the main/master window
        :type master: main `tk.window` ref
        """
        #--references
        self.master_ref = master    #reference back to the main window

        #--control information
        self.CANbus = None          #CAN HW interface ref
        self.CANcom_OK = False      #current CAN com status
        self.AID = None             #CAN AID of this device
        self.RX_filter_en = False   #filter RX inputs to only the defined channels
        self.CANchs = {}            #dictonary of CAN data channel definitions, in format {ch_name:CAN_ch instance}

        #--OBD2 specific information
        self.OBD2_ECU_IDtx = None   #OBD2 ECU ID - transmit
        self.OBD2_ECU_IDrx = None   #OBD2 ECU ID - response

        #--data handling
        self.RX_filter = []         #iterable of dictionaries for the message RX filter
        self.RX_allData = {152:[0,1,2,3,4,5,6,7]}   #dictionary of all RX'd can data, in format {AID:[data,frames,rx,....,n=8]}
        self.CAN_notifier = None    #instance of the CAN notifier for RX'd messages

    def set_cfg(self, **kwargs):
        """ function sets class attributes based on the passed KWARGs.
        All KWARGs have default values non-required core fields. IE, RTR
        has a default field, but AID does not.

        :param kwargs: dict of class inputs
        :type kwargs: any type that can be typecast to string
        """
        kwargs = {k.upper(): v for k, v in kwargs.items()}  #convert kwarg names to uppercase. Allows for use with XML and editor attributes

        self.AID = str2dec(kwargs.get('BASE_AID', sys_default_AID),16)  #get AID - in decimal format
        self.RX_filter_en = kwargs.get('RX_FILTER', False)              #set true/false status of the RX filter
        self.OBD2_ECU_IDtx = kwargs.get('OBD2_ECU_IDTX', None)          #OBD2 ECU ID - transmit
        self.OBD2_ECU_IDrx = kwargs.get('OBD2_ECU_IDRX', None)          #OBD2 ECU ID - response
    
    def CAN_add_channels(self, CANchs):
        """function adds the passed CAN channels to the class dictionary
        that stores all the required CAN channels that get remote data
        
        :param CANchs: dict of can channels
        :type CANchs: {'channel_name':`class` CANch}
        """
        for k,v in CANchs.items():      #cycle through passed channels
            self.CANchs.update({k:v})   #update the class dict

    def chk_exist_CANch(self, ch_name):
        """function checks if CAN data channel is currently defined
        
        :param ch_name: defined name for can channel
        :type ch_name: `string`
        :returns: can channel name is defined
        :rtype: `boolean` - TRUE if channel is defined
        """
        exists = False                          #all other cases return false
        if ch_name in self.CANchs: return True  #only return true if defined
        return exists

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

        #check for default required values
        if self.AID is None or self.AID == '':
            tmp_err_list.append(create_err_msg('CAN','CFG','No base ArbitID is defined and is required'))
        if self.RX_filter_en is None or self.RX_filter_en == '':
            tmp_err_list.append(create_err_msg('CAN','CFG','CAN RX msg filter enable undefined'))

        ch_OBD2 = False         #temp var to track if any CAN channel is an OBD2 config
        for v in self.CANchs.values():                          #cycle through all CAN channels
            ch_err = v.dashCFG_checkErrs()                      #and check for channel errors
            if ch_err:
                for err in ch_err: tmp_err_list.append(err)     #add any errors
            if v.OBD2 == True: ch_OBD2 = True                   #if any of the channels is an OBD2 format, set true

        #if one of the CAN channels is an OBD2 type, then the TX/RX field needs to be set
        if ch_OBD2 == True and (self.OBD2_ECU_IDrx is None or self.OBD2_ECU_IDtx is None):
            tmp_err_list.append(create_err_msg('CAN','CFG','No OBD2 ECU tx/rx ID set, CAN ch is OBD2 type'))

        return tmp_err_list
    
    def CAN_init(self):
        """function sets up CANbus hardware interface and instances hardware control"""

        sys_string = "sudo /sbin/ip link set "                      #build system string for HW intialization
        sys_string += sys_HW_chnl                                   #channel=can0
        sys_string += " up type can bitrate " + sys_CAN_baud        #baud=500000

        try:                                                        #try to setup CAN hardware
            os.system(sys_string)                                       #initiate can0 interface at 500kbps
            time.sleep(0.05)	                                        #brief pause
            self.CANbus = can.interface.Bus(channel=sys_HW_chnl, 
                                            interface=sys_CAN_intrfce)  #instance CAN object
            self.CANcom_OK = True                                       #set the CAN status as OK
        except:                                                     #record an error if unsuccessful
            self.master_ref.upd_errors([create_err_msg('CAN','HW','Unable to start CANbus - hardware error')])
        
    def CAN_set_RXlistener(self, CANrx_listener_func):
        """function assigns the listener method for any RX'd messages.
        This typically is a function that handles any RX'd messages and
        determines what to do with the information
        
        :param CANrx_listener_func: function to assign as a listener to any RX'd CAN channels
        :type CANrx_listener_func: method/function
        """
        self.CAN_notifier = can.Notifier(self.CANbus, [CANrx_listener_func])    #assign listener to notifier

    def CAN_gen_RXfilters(self, rxfilter_en=False):
        """Function TBD: function generates the requried RX filter based on the defined CANch AIDs
        pythonCAN documentation says its a "iterable of dictionaries" with the below information:        
            Format from docs: [{"can_id": 0x11, "can_mask": 0x21, "extended": False}]

        To let all SFF or EFF frames through, can use the sys_EFF_mask or sys_SFF_mask

        :param rxfilter_en: enable input filters when defining
        :type rxfilter_en: bool - True to enable when defining
        """
        ch_OBD2 = False     #temp var to check if any of the channels are an OBD2 type
        for v in self.CANchs.values():                              #cycle through all defined channels
            if v.OBD2 == False:                     #for non-OBD2 addresses, generate an appropriate filter
                tmp_mask = None                                             #temp mask var
                if v.ext_AID == True: tmp_mask = sys_EFF_mask               #if it's an extended AID, use EFF mask
                else: tmp_mask = sys_SFF_mask                               #otherwise use standard (SFF) mask
                self.RX_filter.append([{'can_id':v.AID, 'can_mask':tmp_mask, 'extended':v.ext_AID}])       #then append filter to list
            elif v.OBD2 == True: ch_OBD2 = True     #flag if any channels are OBD2 types

        if ch_OBD2 == True:     #if a CAN channel was OBD2 related, then add the ECU ID to the filter
            self.RX_filter.append([{'can_id':self.OBD2_ECU_IDrx, 'can_mask':sys_SFF_mask, 'extended':False}])
        
        if rxfilter_en == True: self.CAN_RXfilter_on()      #if the filter enable is set, then also start after generating
    
    def CAN_RXfilter_on(self):
        """function enables the input CAN message filter at the HW level"""
        self.RX_filter_en = True                        #set status var
        try: self.CANbus.set_filters(self.RX_filter)    #enable filter
        except: pass    #catch for cases where CAN is not instanced due to error, cannot toggle filter

    def CAN_RXfilter_off(self):
        """function disables the input CAN message filter at the HW level"""
        self.RX_filter_en = False               #set status car
        try: self.CANbus.set_filters()          #per method, zero-length iterable or None will clear
        except: pass    #catch for cases where CAN is not instanced due to error, cannot toggle filter
            
    def CAN_RTR_init(self, RTR_start=False):
        """function initializes any/all defined CAN channels that require an
        RTR (remote transmit request) to get their data.
        
        :param RTR_start: immediately start RTR transmits when defined
        :type RTR_start: bool - True to immediately start
        """
        for v in self.CANchs.values():  #cycle through defined channels
            if v.RTR == True:
                v.CANch_RTR_init()      #instance RTR schedule for channel
                if RTR_start==True:     #if desired to immediately start
                    v.CANch_RTR_start() #start RTR
    
    def CAN_RTR_ALLstart(self):
        """function starts all RTR periodic requests
        """
        for v in self.CANchs.values():  #cycle through defined channels
            if v.RTR == True:
                v.CANch_RTR_start()     #start RTR for channel
                
    def CAN_RTR_ALLstop(self):
        """function stops all RTR periodic requests
        """
        for v in self.CANchs.values():  #cycle through defined channels
            if v.RTR == True:
                v.CANch_RTR_stop()      #stop RTR for channel

    def CAN_rx_data_update(self, AID, data_frames):
        """function updates the all CAN data RX'd dictionary for the CAN sniffer"""
        #TODO: need to update to handle OBD2 frames
        msg_indx = None
        if AID == self.OBD2_ECU_IDrx:   #if the RX'd message comes from an OBD2 connection
            msg_indx = AID + '|' + data_frames[sys_OBD2_msgIndx_PID]    #then append the PID for a unique entry
        else: msg_indx = AID
        self.RX_allData.update({msg_indx:data_frames})
    
    def CAN_rx_data_clear(self):
        """function clears the all CAN data RX'd dictionary for the CAN sniffer"""
        self.RX_allData.clear()

    def CAN_msgRX_func(self, CAN_msg):
        """function processes any received CAN data packets and calls any associated
        supporting functions as required."""

        rxAID = CAN_msg.arbitration_id  #RX'd address
        rxMSG = CAN_msg.data            #data frames
        #CAN_msg.dlc                    #data length of the RX'd packet
        #True if rx_msg.is_extended_id == 'X' else False    #booloean for EFF data frame

        self.CAN_rx_data_update(rxAID, rxMSG)       #update the raw can RX'd dict with the message
        for v in self.CANchs.values():              #cycle through all CAN channels
            if rxAID == v.AID:                      #if the AID corresponds to a data channel
                v.val_rawCAN = rxMSG                    #set raw CAN frame
                v.upd_calc_dec()                        #and update decimal value