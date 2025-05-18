#-----------------------------imports
#remdinder to use the relative "." here otherwise it's not "part of the package"
from .py_dash_defines import *           #import values from defines file using other namespace

#-----------------------------CAN and Display data
class dash_info:
    def __init__(self,  capt, var_value, CAN_addr, dec_ofst, fxd_pt,
                        warn_en, dngr_lo, warn_lo, warn_hi, dngr_hi, 
                        lbl_typ, lbl_x0, lbl_y0, lbl_w, lbl_h,
                        capt_x0, capt_y0, capt_w, capt_h):
        #-----CAN data values
        self.CAN_addr = CAN_addr        #CANbus address
        self.var_value = var_value      #data value
        self.dec_ofst = dec_ofst        #decimal offset used when converting from CANbus frames to actual decimal data
        self.fxd_pt = fxd_pt            #value is fixed point, 1 decimal place

        #-----display conditioning info
        self.warn_en = warn_en          #enable color changing warning/danger color coding
        self.dngr_lo = dngr_lo          #alert value; danger lo. For indicator type this is the "off" threshold
        self.warn_lo = warn_lo          #alert value; warning lo.
        self.warn_hi = warn_hi          #alert value; warning hi.
        self.dngr_hi = dngr_hi          #alert value; danger hi. For indicator type this is the "on" threshold

        #label caption information
        self.capt = capt                #value caption text
        self.capt_x0 = capt_x0          #label x-position
        self.capt_y0 = capt_y0          #label y-position
        self.capt_w = capt_w            #label width
        self.capt_h = capt_h            #label height

        #-----label information
        self.lbl_ref = None             #data labelID reference
        self.scope_ref = None           #data scope reference
        self.lbl_typ = lbl_typ          #label type, either "indication" or "data" type
        self.strvar = None              #stringvar to link to data label
        self.lbl_x0 = lbl_x0            #label x-position
        self.lbl_y0 = lbl_y0            #label y-position
        self.lbl_w = lbl_w              #label width
        self.lbl_h = lbl_h              #label height

        #-----additional functions
        self.alt_func = None            #alternate function call when updating      

#-----instance and define dash info list
'''
                    capt, var_value, CAN_addr, dec_ofst, fxd_pt,
                    warn_en, dngr_lo, warn_lo, warn_hi, dngr_hi, 
                    lbl_typ, lbl_x0, lbl_y0, lbl_w, lbl_h,
                    capt_x0, capt_y0, capt_w, capt_h
'''
di = []
#RPM data
di.append(dash_info('RPM', 800, 0x63, 0, False,
                    True, -1, -1, 4000, 4500,
                    lbl_type_data, 565, 150, 140, noPad_height,
                    370, 150, None, noPad_height))
#RPM bar graph
bar_rpm_x0 = 130
bar_rpm_y0 = 36
bar_rpm_x1 = 898
bar_rpm_y1 = 206
max_width = bar_rpm_x1 - bar_rpm_x0

#Engine coolant temp data
di.append(dash_info('ECT', 80, 0x43, -65, False,
                    True, 20, 50, 218, 225,
                    lbl_type_data, 294, 257, 110, noPad_height,
                    110, 257, None, noPad_height))
#wbO2 label
di.append(dash_info('O2', 14.5, 0x73, 0, True,
                    True, 11.0, 12.5, 15.0, 15.5,
                    lbl_type_data, 785, 257, 120, noPad_height,
                    614, 257, None, noPad_height))
#oilP label
di.append(dash_info('OILP', 5, 0x44, 0, False,
                    True, 30, 40, 70, 75,
                    lbl_type_data, 332, 367, 70, noPad_height,
                    110, 367, None, noPad_height))
#MAP label
di.append(dash_info('MAP', 29.6, 0x45, 0, True,
                    False, 9.0, 9.5, 29.5, 30.0,
                    lbl_type_data, 785, 367, 120, noPad_height,
                    614, 367, None, noPad_height))
#headlight lo beams
di.append(dash_info('LOBM', 0x0A, 0x2B, 0, False,
                    False, 0, 0, 0, 0,
                    lbl_type_ind, 105,  515, 65, 65,
                    0, 0, None, None))
#headlight hi beams
di.append(dash_info('HIBM', 0x0A, 0x27, 0, False, 
                    False, 0, 0, 0, 0,
                    lbl_type_ind, 105,  515, 65, 65,
                    0, 0, None, None))
#number of array values
di_sz = len(di)