"""
File:       can.py
Function:   This file contains any CAN bus specific classes and methods
"""
from .sys import *
from .com_defs import create_err_msg, str2dec
from .com_defs import err_message

class CANch():
    def __init__(self, CANbus_master):
        """Construct a CANch data instace. Class includes function for converting RX'd 
        data into meaningful decimal values. Additionally includes tk.DoubleVar() reference 
        for PyDash display widgets to link to for updating on new values.
        
        :param CANbus_master: reference back to the main CANbus instance
        :type CANbus_master: `can` library
        """
        #--references
        self.CANbus_ref = CANbus_master #reference back to CAN bus instance
        self.CAN_core_ref = None        #reference back to CAN_core instance
        self.master_ref = None          #reference back to main window

        #--channel information
        self.Name = None                #data channel name - will be display name in logfile
        self.PID = None                 #CANbus PID for channel
        self.ext_PID = None             #CANbus PID is extended ID
        self.RTR = False                #remote transmit request required
        self.RTR_freq = None            #RTR frequency in seconds
        self.DLC = None                 #number of expected frames
        self.time_base = sys_RTR_freq_dflt #expected cycle time (t) in seconds for missed message detection
        self.timeout = 3 * self.time_base  #timeout limit (3*t) in seconds

        #--values and conversion
        self.calc_frames = []           #the frames in the RX'd word to use when calulating the value
        self.calc_Scalar = None         #the final value scalar when converting frames to decimal
        self.calc_Offset = None         #the decimal offset of the caluclated value

        #--error handling
        self.last_RX = None             #time of the last RX'd data frame
        self.err = False                #flag that channel has an error
        self.start_time = time.time()   #time channel started monitoring
        self.drop_out_count = 0         #number of times channel timed out (dropped out)
        self.pick_up_count = 0          #number of times channel recovered (picked up)
        self.flapping_warned = False    #flag if repeated pick-up/drop-out warning was logged
        self.linked_elements = []       #list of UI elements linked to this channel

        #--misc
        self.log_en = False             #datalogging this channel is enabled
        self.RTR_task = None            #reference to the RTR scheduled task
        self.val_rawCAN = []            #raw RX'd CAN frame data
        self.val_dec = tk.DoubleVar()   #raw CAN frame converted to decimal
    
    def set_cfg(self, **kwargs):
        """ function sets class attributes based on the passed KWARGs.
        All KWARGs have default values non-required core fields. IE, RTR
        has a default field, but PID does not.

        :param kwargs: dict of class inputs
        :type kwargs: any type that can be typecast to string
        """
        kwargs = {k.upper(): v for k, v in kwargs.items()}  #convert kwarg names to uppercase. Allows for use with XML and editor attributes
        self.Name = kwargs.get('NAME', None)
        self.PID = str2dec(kwargs.get('PID', None),16)
        self.ext_PID = kwargs.get('EXT', False)
        self.DLC = str2dec(kwargs.get('DLC', 1))
        self.RTR = kwargs.get('REM_REQ', False)
        req_freq_raw = kwargs.get('REQ_FREQ', None)
        if self.RTR == True:                            #if RTR enabled
            if req_freq_raw is not None and req_freq_raw != '':
                self.RTR_freq = str2dec(req_freq_raw)
            else:
                self.RTR_freq = sys_RTR_freq_dflt
        else:
            self.RTR_freq = None

        # Time-base definition for missed message detection (3*t)
        tb_raw = kwargs.get('TIME_BASE', kwargs.get('TIMEBASE', kwargs.get('CYCLE_TIME', kwargs.get('FREQ', None))))
        if tb_raw is not None and tb_raw != '':
            self.time_base = str2dec(tb_raw)
        elif self.RTR and self.RTR_freq is not None:
            self.time_base = self.RTR_freq
        elif req_freq_raw is not None and req_freq_raw != '':
            self.time_base = str2dec(req_freq_raw)
        else:
            self.time_base = sys_RTR_freq_dflt

        # If explicit TIMEOUT was provided, use it or calculate 3*t
        if kwargs.get('TIMEOUT') is not None and kwargs.get('TIMEOUT') != '':
            self.timeout = str2dec(kwargs.get('TIMEOUT'))
        else:
            self.timeout = 3 * self.time_base
        
        self.calc_frames = kwargs.get('FRAMES', [1])
        self.calc_Scalar = str2dec(kwargs.get('SCALAR', 1))
        self.calc_Offset = str2dec(kwargs.get('OFFSET', 0))
        self.convert_calc_frames_cfg()                  #convert the read frames value to a usable format

    def convert_calc_frames_cfg(self):
        """function converts from the user-friendly config value that is a string of 1
        index frames to the actual 0 index list that is useful for processing a CAN message"""
        if self.calc_frames is not None and self.calc_frames != '':
            if isinstance(self.calc_frames, (list, tuple)):
                tmp_frames = [v - 1 for v in self.calc_frames]
            elif isinstance(self.calc_frames, int):
                tmp_frames = [self.calc_frames - 1]
            else:
                try:
                    eval_res = literal_eval(str(self.calc_frames))
                    if isinstance(eval_res, (list, tuple)):
                        tmp_frames = list(eval_res)
                    else:
                        tmp_frames = [eval_res]
                    tmp_frames = [v - 1 for v in tmp_frames]
                except Exception:
                    tmp_frames = None
            self.calc_frames = tmp_frames
        else:
            self.calc_frames = None
    
    def reset_channel_monitoring(self, start_time=None):
        """Resets monitoring start times for all channels."""
        if start_time is None:
            start_time = time.time()
        for ch in self.CANchs.values():
            ch.start_monitoring(start_time)

    def check_timeouts(self, current_time=None):
        """Cycles through all CAN channels and checks for timeouts."""
        if current_time is None:
            current_time = time.time()
        timeouts = {}
        for name, ch in self.CANchs.items():
            if ch.check_timeout(current_time):
                timeouts[name] = ch
        return timeouts

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
        skip_attrs = ('CANbus_ref', 'last_RX', 'RTR_task', 'start_time', 'linked_elements',
                      'drop_out_count', 'pick_up_count', 'flapping_warned', 'CAN_core_ref', 'master_ref')
        for attr, val in self.__dict__.items():
            if attr in skip_attrs:
                continue    #skip, these are not config values
            if (attr != 'RTR') and (attr != 'RTR_freq') and ((val is None) or val == ''):
                tmp_err_list.append(create_err_msg('CAN','chCFG-'+self.Name,attr+' undefined'))
            elif attr == 'RTR' and (self.RTR_freq == True) and ((val is None) or val == ''):
                tmp_err_list.append(create_err_msg('CAN','chCFG-'+self.Name,'RTR is en but no freq defined'))
            elif attr == 'calc_Scalar' and (self.calc_Scalar == 0):
                tmp_err_list.append(create_err_msg('CAN','chCFG-'+self.Name,'Scalar is 0 - will not be a valid value'))
        return tmp_err_list #return error list
    
    def upd_calc_dec(self):
        """function calcualtes the current decimal value based on the
        current rawCAN data frame"""
        tmpval = 0
        msb_indx = 0        #temp most-sig byte index for decimal conversion
        for frm_indx in self.calc_frames:                       #loop through the defined frames to calcualte
            tmpval += self.val_rawCAN[frm_indx]*(256**msb_indx)  #convert the frame to decimal from LSB to MSB
            msb_indx += 1   #increment index
        tmpval *= self.calc_Scalar  #scale raw decimal result
        tmpval += self.calc_Offset  #apply final offset
        self.val_dec.set(round(tmpval,5))    #update doublevar - limit to 5 sigdigs
        
    def start_monitoring(self, start_time=None):
        """Sets the initial monitoring start time for timeout calculations."""
        if start_time is None:
            start_time = time.time()
        self.start_time = start_time
        self.last_RX = None

    def on_message_rx(self, rx_time=None):
        """Handles message reception timestamping, pick-up detection, and flapping warning."""
        if rx_time is None:
            rx_time = time.time()
        was_err = self.err
        self.last_RX = rx_time
        if was_err:
            self.err = False
            self.pick_up_count += 1
            self._check_flapping()
            self._notify_elements()

    def check_timeout(self, current_time=None):
        """Checks if 3*t cycle has elapsed with no data for this channel.
        If timeout occurs, sets self.err = True, updates linked elements, and logs error."""
        if current_time is None:
            current_time = time.time()

        ref_time = self.last_RX if self.last_RX is not None else self.start_time
        elapsed = current_time - ref_time
        timeout_threshold = self.timeout if self.timeout is not None else (3 * self.time_base)

        if elapsed >= timeout_threshold:
            if not self.err:
                self.err = True
                self.drop_out_count += 1
                self._check_flapping()
                self._notify_elements()
                self._log_timeout()
            return True
        return False

    def _notify_elements(self):
        """Notifies all linked page elements to update their display states."""
        for ele in self.linked_elements:
            try:
                ele.update_state()
            except Exception:
                pass

    def _check_flapping(self):
        """Logs a warning if repeated pick-up and drop-out of a channel is detected."""
        if self.drop_out_count >= 2 and self.pick_up_count >= 1:
            warn_msg = create_err_msg(
                'CAN',
                f'chWarn-{self.Name}',
                f'Repeated pick-up and drop-out on {self.Name}; adjust expected time-base ({self.time_base}s)',
                clearable=True
            )
            self._log_error_dedup(warn_msg)

    def _log_timeout(self):
        """Logs channel timeout to the dash errors menu, keeping only the latest occurrence."""
        err_msg = create_err_msg(
            'CAN',
            f'chTimeout-{self.Name}',
            f'Channel {self.Name} timed out (missed message 3*t={round(3 * self.time_base, 2)}s)',
            clearable=True
        )
        self._log_error_dedup(err_msg)

    def _log_error_dedup(self, err_obj):
        """Logs an error to master_ref, ensuring only latest occurrence for this channel module is kept."""
        target = self.master_ref
        if target is None and self.CAN_core_ref is not None:
            target = getattr(self.CAN_core_ref, 'master_ref', None)

        if target is not None:
            if hasattr(target, 'log_channel_error'):
                target.log_channel_error(err_obj)
            elif hasattr(target, 'errors') and isinstance(target.errors, list):
                target.errors = [
                    e for e in target.errors
                    if not (getattr(e, 'sys', None) == err_obj.sys and getattr(e, 'mod', None) == err_obj.mod)
                ]
                target.errors.append(err_obj)
            elif hasattr(target, 'upd_errors'):
                target.upd_errors([err_obj])

    def CANch_RTR_init(self):
        """function initializes the RTR periodic send task for this data
        channel."""        
        msg = self.CANbus_ref.Message(  arbitration_id=self.PID,    #PID to request data from
                                        data=None,                  #RTR data field is empty
                                        is_extended_id=self.ext_PID,#CAN frame config - PID is extended ID
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
        self.PID = None             #CAN PID of this device
        self.RX_filter_en = False   #filter RX inputs to only the defined channels
        self.CANchs = {}            #dictonary of CAN data channel definitions, in format {ch_name:CAN_ch instance}

        #--data handling
        self.RX_filter = []         #iterable of dictionaries for the message RX filter
        self.RX_allData = {152:[0,1,2,3,4,5,6,7]}   #dictionary of all RX'd can data, in format {PID:[data,frames,rx,....,n=8]}
        self.CAN_notifier = None    #instance of the CAN notifier for RX'd messages

    def set_cfg(self, **kwargs):
        """ function sets class attributes based on the passed KWARGs.
        All KWARGs have default values non-required core fields. IE, RTR
        has a default field, but PID does not.

        :param kwargs: dict of class inputs
        :type kwargs: any type that can be typecast to string
        """
        kwargs = {k.upper(): v for k, v in kwargs.items()}  #convert kwarg names to uppercase. Allows for use with XML and editor attributes

        self.PID = kwargs.get('BASE_PID', sys_default_PID)  #get PID
        self.PID = str2dec(self.PID, 16)                    #convert to dec
        self.RX_filter_en = kwargs.get('RX_FILTER', False)
    
    def CAN_add_channels(self, CANchs):
        """function adds the passed CAN channels to the class dictionary
        that stores all the required CAN channels that get remote data
        
        :param CANchs: dict of can channels
        :type CANchs: {'channel_name':`class` CANch}
        """
        for k,v in CANchs.items():      #cycle through passed channels
            v.CAN_core_ref = self
            v.master_ref = self.master_ref
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

    def reset_channel_monitoring(self, start_time=None):
        """Resets monitoring start times for all channels."""
        if start_time is None:
            start_time = time.time()
        for ch in self.CANchs.values():
            ch.start_monitoring(start_time)

    def check_timeouts(self, current_time=None):
        """Cycles through all CAN channels and checks for timeouts."""
        if current_time is None:
            current_time = time.time()
        timeouts = {}
        for name, ch in self.CANchs.items():
            if ch.check_timeout(current_time):
                timeouts[name] = ch
        return timeouts

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

        if self.PID is None or self.PID == '':
            tmp_err_list.append(create_err_msg('CAN','CFG','No base PID is defined and is required'))
        if self.RX_filter_en is None or self.RX_filter_en == '':
            tmp_err_list.append(create_err_msg('CAN','CFG','CAN RX msg filter enable undefined'))

        for v in self.CANchs.values():                          #cycle through all CAN channels
            ch_err = v.dashCFG_checkErrs()                      #and check for channel errors
            if ch_err:
                for err in ch_err: tmp_err_list.append(err)     #add any errors
            
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
            self.reset_channel_monitoring()                             #reset timeout monitoring clocks
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
        """Function TBD: function generates the requried RX filter based on the defined CANch PIDs
        pythonCAN documentation says its a "iterable of dictionaries" with the below information:        
            Format from docs: [{"can_id": 0x11, "can_mask": 0x21, "extended": False}]

        To let all SFF or EFF frames through, can use the sys_EFF_mask or sys_SFF_mask

        :param rxfilter_en: enable input filters when defining
        :type rxfilter_en: bool - True to enable when defining
        """
        for v in self.CANchs.values():                              #cycle through all defined channels
            tmp_mask = None                                             #temp mask var
            if v.ext_PID == True: tmp_mask = sys_EFF_mask               #if it's an extended PID, use EFF mask
            else: tmp_mask = sys_SFF_mask                               #otherwise use standard (SFF) mask
            self.RX_filter.append([{'can_id':v.PID, 'can_mask':tmp_mask, 'extended':v.ext_PID}])       #then append filter to list
        
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

    def CAN_rx_data_update(self, PID, data_frames):
        """function updates the all CAN data RX'd dictionary for the CAN sniffer"""
        self.RX_allData.update({PID:data_frames})
    
    def CAN_rx_data_clear(self):
        """function clears the all CAN data RX'd dictionary for the CAN sniffer"""
        self.RX_allData.clear()

    def CAN_msgRX_func(self, CAN_msg):
        """function processes any received CAN data packets and calls any associated
        supporting functions as required."""

        rxPID = CAN_msg.arbitration_id  #RX'd address
        rxMSG = CAN_msg.data            #data frames
        #CAN_msg.dlc                    #data length of the RX'd packet
        #True if rx_msg.is_extended_id == 'X' else False    #booloean for EFF data frame

        rx_time = getattr(CAN_msg, 'timestamp', None)
        if not rx_time:
            rx_time = time.time()

        self.CAN_rx_data_update(rxPID, rxMSG)       #update the raw can RX'd dict with the message
        for v in self.CANchs.values():              #cycle through all CAN channels
            if rxPID == v.PID:                      #if the PID corresponds to a data channel
                v.val_rawCAN = rxMSG                    #set raw CAN frame
                v.on_message_rx(rx_time=rx_time)        #record RX time and handle pick-up/recovery
                v.upd_calc_dec()                        #and update decimal value