import os
import sys
import time
import pytest
import can
import tkinter as tk
import xml.etree.ElementTree as ET

@pytest.fixture(scope='session', autouse=True)
def tk_root():
    root = tk.Tk()
    root.withdraw()
    yield root
    try:
        root.destroy()
    except Exception:
        pass

# Add Dash_Application to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Dash_Application')))

from lib import (
    CANch, CAN_core, Label_Data, Indicator_Bullet, Indicator_Bar,
    dash_theme_user, create_err_msg, sys_RTR_freq_dflt, parseXML_CAN
)

class MockCanvas:
    def __init__(self):
        self.items = {}
        self.coords_map = {}
        self._next_id = 1

    def create_text(self, x, y, **kwargs):
        item_id = self._next_id
        self._next_id += 1
        self.items[item_id] = kwargs
        self.coords_map[item_id] = [x, y]
        return item_id

    def create_oval(self, x0, y0, x1, y1, **kwargs):
        item_id = self._next_id
        self._next_id += 1
        self.items[item_id] = kwargs
        self.coords_map[item_id] = [x0, y0, x1, y1]
        return item_id

    def create_rectangle(self, x0, y0, x1, y1, **kwargs):
        item_id = self._next_id
        self._next_id += 1
        self.items[item_id] = kwargs
        self.coords_map[item_id] = [x0, y0, x1, y1]
        return item_id

    def itemconfigure(self, item_id, kwargs=None, **extra_kwargs):
        if kwargs is None:
            kwargs = {}
        kwargs.update(extra_kwargs)
        if item_id in self.items:
            self.items[item_id].update(kwargs)

    def coords(self, item_id, *args):
        if args:
            self.coords_map[item_id] = list(args)
        return self.coords_map.get(item_id, [])

class MockDashControl:
    def elePad_update(self, canv, obj_id, pad_id, kwargs):
        pass

class MockMaster:
    def __init__(self):
        self.errors = []
        self.dash_theme = dash_theme_user()
        self.dash_theme.colors = {
            'BG': '#636363',
            'FG': '#FFFFFF',
            'IND_ON': '#00FF00',
            'IND_OFF': '#636363',
            'ALERT_FG': '#000000',
            'ALERT_WARN': '#FFFF00',
            'ALERT_DNGR': '#FF0000',
        }
        self.dash_ctl = MockDashControl()
        self.dash_CAN = CAN_core(self)

    def upd_errors(self, err_msgs):
        for e in err_msgs:
            self.errors.append(e)

    def log_channel_error(self, err_msg):
        self.errors = [e for e in self.errors if not (e.sys == err_msg.sys and e.mod == err_msg.mod)]
        self.errors.append(err_msg)

    def clear_errs(self):
        self.errors = [e for e in self.errors if not getattr(e, 'clr', False)]


def test_canch_time_base_configuration():
    """Verify that CANch configures time_base and timeout (3*t) for RTR and non-RTR channels."""
    ch = CANch(None)

    # Default fallback
    ch.set_cfg(NAME='RPM', PID='0x63', DLC=2)
    assert ch.time_base == sys_RTR_freq_dflt
    assert ch.timeout == 3 * sys_RTR_freq_dflt

    # Explicit TIME_BASE
    ch.set_cfg(NAME='RPM', PID='0x63', TIME_BASE=0.2)
    assert ch.time_base == 0.2
    assert abs(ch.timeout - 0.6) < 1e-6

    # Alternative CYCLE_TIME kwarg
    ch.set_cfg(NAME='ECT', PID='0x43', CYCLE_TIME=1.0)
    assert ch.time_base == 1.0
    assert ch.timeout == 3.0

    # RTR channel with REQ_FREQ inherits as time_base
    ch.set_cfg(NAME='OILP', PID='0x44', REM_REQ=True, REQ_FREQ=0.5)
    assert ch.RTR is True
    assert ch.RTR_freq == 0.5
    assert ch.time_base == 0.5
    assert abs(ch.timeout - 1.5) < 1e-6


def test_channel_timeout_detection():
    """Verify that timeout triggers after 3*t elapsed without data."""
    master = MockMaster()
    can_core = CAN_core(master)
    ch = CANch(None)
    ch.set_cfg(NAME='RPM', PID='0x63', TIME_BASE=1.0)
    can_core.CAN_add_channels({'RPM': ch})

    t0 = 1000.0
    ch.start_monitoring(start_time=t0)
    assert ch.err is False

    # Check at t0 + 2.0s (< 3.0s) -> no timeout
    assert ch.check_timeout(current_time=t0 + 2.0) is False
    assert ch.err is False
    assert len(master.errors) == 0

    # Check at t0 + 3.0s (>= 3*t) -> timeout triggers!
    assert ch.check_timeout(current_time=t0 + 3.0) is True
    assert ch.err is True
    assert len(master.errors) == 1
    assert master.errors[0].mod == 'chTimeout-RPM'
    assert 'timed out' in master.errors[0].msg


def test_data_label_shows_err_on_timeout():
    """Verify that Label_Data shows 'ERR' when its linked CAN channel times out."""
    master = MockMaster()
    can_core = CAN_core(master)
    ch = CANch(None)
    ch.set_cfg(NAME='RPM', PID='0x63', TIME_BASE=0.5, FRAMES='1,2', SCALAR=1, OFFSET=0)
    can_core.CAN_add_channels({'RPM': ch})

    canv = MockCanvas()
    lbl = Label_Data()
    lbl.init_config({'NAME': 'rpm_lbl', 'DATA_CH': 'RPM', 'FILL': 'FG', 'CLR_BG': 'BG', 'SIGDIG': 0})
    lbl.master_ref = master
    lbl.canv_ref = canv
    lbl.objID = canv.create_text(50, 50, text='0')

    # Link channel to label with trace (as done in dash_control.page_ele_CANref_set)
    lbl.CAN_ch_ref = ch
    lbl.CAN_dec_ref = ch.val_dec
    ch.linked_elements.append(lbl)
    lbl.CAN_dec_ref.trace_add('write', lbl.update_state)

    # Initial data arrives at t0
    t0 = 1000.0
    msg = can.Message(arbitration_id=0x63, data=[0xE8, 0x03], timestamp=t0) # 1000 RPM (0x03E8 = 1000)
    can_core.CAN_msgRX_func(msg)
    assert ch.err is False
    assert canv.items[lbl.objID]['text'] == '1000'

    # Advance time past 3*t (3 * 0.5 = 1.5s -> t0 + 2.0s)
    can_core.check_timeouts(current_time=t0 + 2.0)
    assert ch.err is True
    # Canvas text must now be "ERR"
    assert canv.items[lbl.objID]['text'] == 'ERR'

    # When new message arrives, channel recovers and displays new value
    msg2 = can.Message(arbitration_id=0x63, data=[0xDC, 0x05], timestamp=t0 + 2.5) # 1500 RPM (0x05DC = 1500)
    can_core.CAN_msgRX_func(msg2)
    assert ch.err is False
    assert canv.items[lbl.objID]['text'] == '1500'


def test_bullet_and_bar_default_off_zero_on_timeout():
    """Verify that buttons/bullets default to 'off' and bars default to 'zero' on timeout."""
    master = MockMaster()
    can_core = CAN_core(master)
    ch = CANch(None)
    ch.set_cfg(NAME='TPS', PID='0x50', TIME_BASE=0.5, FRAMES='1', SCALAR=1, OFFSET=0)
    can_core.CAN_add_channels({'TPS': ch})

    canv = MockCanvas()

    # Bullet
    blt = Indicator_Bullet()
    blt.init_config({
        'NAME': 'tps_blt', 'DATA_CH': 'TPS', 'CLR_LO': 'IND_OFF', 'CLR_HI': 'IND_ON',
        'OUTLN': 'FG', 'LIM_LO': 20, 'LIM_HI': 50, 'SIZE': 20, 'X0': 10, 'Y0': 10
    })
    blt.master_ref = master
    blt.canv_ref = canv
    blt.objID = canv.create_oval(10, 10, 30, 30, fill=master.dash_theme.colors['IND_OFF'])
    blt.CAN_ch_ref = ch
    blt.CAN_dec_ref = ch.val_dec
    ch.linked_elements.append(blt)
    blt.CAN_dec_ref.trace_add('write', blt.update_state)

    # Bar
    bar = Indicator_Bar()
    bar.init_config({
        'NAME': 'tps_bar', 'DATA_CH': 'TPS', 'FILL': 'FG', 'OUTLN': 'FG',
        'SCALE_LO': 0, 'SCALE_HI': 100, 'WIDTH': 200, 'HEIGHT': 20, 'X0': 50, 'Y0': 50
    })
    bar.master_ref = master
    bar.canv_ref = canv
    bar.objID = canv.create_rectangle(50, 50, 50, 70, fill=master.dash_theme.colors['FG'])
    bar.CAN_ch_ref = ch
    bar.CAN_dec_ref = ch.val_dec
    ch.linked_elements.append(bar)
    bar.CAN_dec_ref.trace_add('write', bar.update_state)

    # Receive data: TPS = 80 (active) at t0
    t0 = 2000.0
    msg = can.Message(arbitration_id=0x50, data=[80], timestamp=t0)
    can_core.CAN_msgRX_func(msg)

    # Bullet is ON (IND_ON = #00FF00)
    assert canv.items[blt.objID]['fill'] == master.dash_theme.colors['IND_ON']
    # Bar is scaled to 80% (50 + 0.8 * 200 = 210)
    coords = canv.coords(bar.objID)
    assert coords[2] == 210.0

    # Advance time past 3*t (t0 + 2.0s >= 3 * 0.5s)
    can_core.check_timeouts(current_time=t0 + 2.0)
    assert ch.err is True

    # Bullet must default to off state (IND_OFF = #636363)
    assert canv.items[blt.objID]['fill'] == master.dash_theme.colors['IND_OFF']
    # Bar must default to zero state (new_x1 = x0 = 50)
    coords = canv.coords(bar.objID)
    assert coords[2] == 50.0


def test_errors_menu_deduplication():
    """Verify that only the latest occurrence for a channel is logged in the errors menu."""
    master = MockMaster()
    can_core = CAN_core(master)
    ch = CANch(None)
    ch.set_cfg(NAME='MAP', PID='0x45', TIME_BASE=0.2)
    can_core.CAN_add_channels({'MAP': ch})

    t = 1000.0
    ch.start_monitoring(t)

    # Timeout 1
    t += 1.0 # > 3*0.2
    ch.check_timeout(t)
    assert ch.err is True
    assert len(master.errors) == 1

    # Channel recovers
    t += 0.5
    msg = can.Message(arbitration_id=0x45, data=[10], timestamp=t)
    can_core.CAN_msgRX_func(msg)
    assert ch.err is False

    # Simulate 5 more timeout-recovery cycles (6 timeouts total)
    for _ in range(5):
        t += 1.0
        ch.check_timeout(t)
        assert ch.err is True
        # Must still only be ONE timeout entry for MAP in master.errors!
        map_errors = [e for e in master.errors if e.mod == 'chTimeout-MAP']
        assert len(map_errors) == 1

        t += 0.5
        msg = can.Message(arbitration_id=0x45, data=[10], timestamp=t)
        can_core.CAN_msgRX_func(msg)
        assert ch.err is False

    # Final check: total timeout entries for MAP is exactly 1 (the latest)
    map_errors = [e for e in master.errors if e.mod == 'chTimeout-MAP']
    assert len(map_errors) == 1


def test_repeated_pickup_and_dropout_warning():
    """Verify that a warning is logged when repeated pick-up and drop-out (flapping) occurs."""
    master = MockMaster()
    can_core = CAN_core(master)
    ch = CANch(None)
    ch.set_cfg(NAME='WBO2', PID='0x73', TIME_BASE=0.1)
    can_core.CAN_add_channels({'WBO2': ch})

    t = 100.0
    ch.start_monitoring(t)

    # 1st drop-out
    t += 0.5
    ch.check_timeout(t)
    assert ch.err is True
    assert ch.drop_out_count == 1
    # No flapping warning yet
    assert not any(e.mod == 'chWarn-WBO2' for e in master.errors)

    # 1st pick-up
    t += 0.2
    msg = can.Message(arbitration_id=0x73, data=[14, 7], timestamp=t)
    can_core.CAN_msgRX_func(msg)
    assert ch.err is False
    assert ch.pick_up_count == 1
    # Still no flapping warning yet
    assert not any(e.mod == 'chWarn-WBO2' for e in master.errors)

    # 2nd drop-out (repeated drop-out/pick-up!)
    t += 0.5
    ch.check_timeout(t)
    assert ch.err is True
    assert ch.drop_out_count == 2

    # Now the flapping warning MUST be logged!
    warn_errors = [e for e in master.errors if e.mod == 'chWarn-WBO2']
    assert len(warn_errors) == 1
    assert 'Repeated pick-up' in warn_errors[0].msg or 'adjust expected time-base' in warn_errors[0].msg


def test_xml_parsing_with_time_base():
    """Verify that parseXML_CAN correctly reads TIME_BASE from XML block."""
    xml_data = """
    <CAN>
      <CORE>
        <BASE_PID>0x9A</BASE_PID>
        <RX_FILTER>False</RX_FILTER>
      </CORE>
      <CHANNELS>
        <CH NAME="RPM">
          <PID>0x63</PID>
          <EXT>False</EXT>
          <DLC>2</DLC>
          <REM_REQ>False</REM_REQ>
          <REQ_FREQ />
          <TIME_BASE>0.25</TIME_BASE>
          <FRAMES>1,2</FRAMES>
          <SCALAR>1</SCALAR>
          <OFFSET>0</OFFSET>
        </CH>
      </CHANNELS>
    </CAN>
    """
    master = MockMaster()
    root = ET.fromstring(xml_data)
    parseXML_CAN(master, root)

    assert 'RPM' in master.dash_CAN.CANchs
    rpm_ch = master.dash_CAN.CANchs['RPM']
    assert rpm_ch.time_base == 0.25
    assert abs(rpm_ch.timeout - 0.75) < 1e-6
    # dashCFG_checkErrs must report no configuration errors
    errs = rpm_ch.dashCFG_checkErrs()
    assert len(errs) == 0


def test_clear_errs_removes_only_clearable():
    """Verify that master.clear_errs clears clearable errors without affecting non-clearable ones."""
    master = MockMaster()
    e_clearable = create_err_msg('CAN', 'chTimeout-RPM', 'RPM timeout', clearable=True)
    e_critical = create_err_msg('Core', 'CFG', 'Fatal XML error', clearable=False)
    master.upd_errors([e_clearable, e_critical])

    assert len(master.errors) == 2
    master.clear_errs()
    assert len(master.errors) == 1
    assert master.errors[0].mod == 'CFG'
    assert master.errors[0].clr is False

def test_full_dash_cfg_loading_and_errchk(tk_root):
    """Verify that actual PyDash_Config.xml and BAD_test_CFG.xml work with dashCFG_ErrChk."""
    from PyDash import wndw_Main
    from lib import XML_open, parseXML, dashCFG_ErrChk, dash_config, dash_theme_user, sys_config_file, sys_root_dir
    import pathlib

    # Test good config
    m_good = wndw_Main.__new__(wndw_Main)
    m_good.prnt_frame = tk.Frame(tk_root)
    m_good.errors = []
    m_good.dash_settings = dash_config()
    m_good.dash_CAN = CAN_core(m_good)
    m_good.dash_theme = dash_theme_user()
    m_good.dash_pages_user = {}
    m_good.dash_pages_menu = {}

    xml_tree = XML_open(m_good, sys_config_file)
    parseXML(m_good, xml_tree)
    dashCFG_ErrChk(m_good)
    assert len(m_good.errors) == 0

    # Test bad config
    m_bad = wndw_Main.__new__(wndw_Main)
    m_bad.prnt_frame = tk.Frame(tk_root)
    m_bad.errors = []
    m_bad.dash_settings = dash_config()
    m_bad.dash_CAN = CAN_core(m_bad)
    m_bad.dash_theme = dash_theme_user()
    m_bad.dash_pages_user = {}
    m_bad.dash_pages_menu = {}

    bad_xml_file = str(pathlib.Path(sys_root_dir).parents[0]) + '/BAD_test_CFG.xml'
    xml_tree_bad = XML_open(m_bad, bad_xml_file)
    parseXML(m_bad, xml_tree_bad)
    dashCFG_ErrChk(m_bad)
    assert len(m_bad.errors) > 0
