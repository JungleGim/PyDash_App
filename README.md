# PyDash_App - Information
This readme covers the application or "App" portion of the PyDash. For the PCB design, Enclosure design, or OS design, see the below repositories:
- PyDash_PCB
- [PyDash_App](https://github.com/JungleGim/PyDash_App)
- [PyDash_OS](https://github.com/JungleGim/PyDash_OS)
- PyDash_Enclosure
- [PyDash_Builder](https://github.com/JungleGim/PyDash_Builder)

## Introduction
The PyDash_App is a python script that serves as an automotive dash display. The intended use is on a custom PCB utilizing a Raspberry Pi compute module that serves as the processor for a digital dash. Key features include:
- Easy to Read
- Configurable
- CANbus communication 

Additional details on the design considerations, required packages, and key features are included in the "Methodology" section of this readme.

# Project Status
## Revlog
- Rev 0: 06/02/2024
	- Initial issue
	- PyDash consists of 5 common engine parameters on a single screen
- Rev 1a: 05/19/2025
	- Added multi-frame (multi-view) capability
	- Added GPIO (button) interrupt capability
	- Can navigate between views with external buttons
	- Added secondary view for CAN sniffer (displays all RX'd CANbus data)
	- Added secondary views for settings and errors (partially populated)
	- Minor UI tweaks for new views
	- Minor file structure tweaks for new views
- Rev 2a: 02/08/2026
	- See Project_Tracker.md for current working notes/issues that are WIP
	- Re-built and re-structured application
	- Updated file structure for better organization
	- Focused on general code cleanup (I learned a lot, still a ways to go)
	- Application now uses a new method to read the dash configuration file and supporting file structure at runtime to build dash
	- Maintained views from previous revision
	- Added error tracking and supporting menu view to display issues
	- Created a "bad config" to test errors
	- Added RTR functionality to CAN channels
	- Updated how the "go back" functionality in windows works and just general window navigation
	
## Future Development
The below is a list of wants/needs for future revisions; loosely listed in order of importance.
* Documentation
	- Make a quick start and full user guide on the program, documenting what everything does - use the built-in help text when available to make it easier to update and maintain
* Code Cleanup
    - A lot of the various "constants" defined everywhere should be converted to a dictionary
    - Now that a better class structure and frames are being used, many of the high-level CAN functions should be placed into the main window class, not just as a global routine. This isn't super critical from an operation standpoint but would help make things more refined.
    - Some of the view functions like the "color update" for out-of-range values are going to be used across multiple view frames. These should be placed into the master class so they're able to be referenced by multiple views. I think it fits better into the master class object vs placing them into the `drawFuncs` or drawing function library, just because they are specific to the dash operation (vs a graphical drawing tool).
* Feature Request: Allow changing setting values in menu
	- things like backlight brightness, CAN PID, etc. should all be updatable
    - After updating, the local XML config should be updated to so settings persist
* Feature Request: Create method to track when last CAN message was RX'd for a PID
    - use the RTR frequency to determine minimum window - include a +1 cycle to determine if its "missed
        + aka, if a 4Hz RTR freq, if there's not a message in 0.5s (1/4 * 2) then assign a "missed" message
        + update the CANch "config error check" and can move the RTRen and RTRfreq into the "always check" category since now both should be defined, and the "freq" part of it is not a conditional check anymore
        + update the CANch "set config" method, because RTR freq is now always required
    - If a message is missed, then include an error in the main dict
        + these will be clearable messages
    - If a message is missed, the displayed value on the dash should indicate it somehow
        + Obvious issue with bar/bullet types, but still have the error tracking
        + Data values should go to a ERR
* Improvement: Updated CAN frame definition
    - Don't use "frames" anymore, change how CAN data is defined for use in the dash
    - Update to "start bit", "number of bits", and "Endian"
    - Endian will ensure the RX'd message is reconstructed correctly
    - "start bit" and "number of bits" will help simplify things and allow like, single big status messages to be used
    - Grayhill keypad and others use single bits so its worth updating
* New Structure: Enable/update USB communication
    - Currently use uSD to house the config settings and local data logs
    - Add local on board flash to house temp files
    - Update the OS to have a filesystem overlay for local files
    - Implement the "mass storage" gadget in the OS
	- would no longer need the uSD approach

## Repository Directory Map
The following information describes the folders found in the root directory of this repository
- (folder) Dash_Application
	- This is the main application folder
- (folder) Development
	- This folder contains some of the WIP or temp files used in testing
	- For example, the "bad config" for error testing and the "PyDash_Config" example archive

# Requirements
## Build Environment
Currently, VSCode on a windows environment is being used to develop the program. Ultimately any IDE that supports python should be applicable. Depending on the required python packages, additional installation steps may be required.

## Physical Hardware
While the app is a python script that could be run on any applicable hardware, there are some key pieces that are required or would require a re-design of the supporting PCB and/or application if omitted. The current hardware configuration consists of:
- Compute Module 4 (CM4) processor board
- Custom designed PCB (PyDash_PCB)
- Wavshare 7inch 1024x600 display
	- [link for display](https://www.waveshare.com/product/raspberry-pi/displays/lcd-oled/70h-1024600.htm?sku=22676)

## Dependent Packages
Below is a WIP list of the non-standard python packages used in the code. As a reminder, any listed dependent packages must be on both the developing OS and the Linux OS running the app (IE PyDash_OS must have the package)

### python-can
Python-can is used for the primary communication of the app.

To install:
	(windows):      "py -m pip install python-can"
  (Linux):        "sudo pip install python-can"


After installing the package, the config file on the Linux OS must be modified to support. Open a command line and use `sudo nano /boot/config.txt` to edit the config file. Comment out `dtparam=spi=on` and add lines `dtoverlay=mcp2515-can0`, and `oscillator=16000000, and `interrupt=12`

After doing the above, restart and use command `dmesg | grep -i can` to see if the CAN module has started. If it has not, use the command `sudo nano /etc/modules` and add `can` in a new line to add at system start.

the above modifications do the following:
- install the required python-can library
- enable SPI on a fresh Linux install
- adds the CAN overlay on spi0-0 (dtoverlay=mcp2515-can0) using the CS0 default pin for chip-sel
- sets "can0" at 16MHz with an interrupt on GPIO25.
- assigns the interrupt pin to GPIO #12

### Pillow
Pillow is used for some graphical tools and processing in the app

To install:
  (windows):      "pip install Pillow"
  (Linux):        "sudo apt-get install python3-pil python3-pil.imagetk"
		
### Compileall
The python "compileall" package is used in the current windows environment to provide a compiled python package. A compiled python package provides some overhead streamlining when running the program on the dash.
		(windows):			"pip install compileall2"
		
To compile, from command line in python program directory type `python -m compileall . -q`. Then copy files from the `pycache` folders into the desired deployment directory. Note that any file structure and dependent directories (like image file) need to be copied as well.

# Methodology
## Key Considerations and Constraints
WIP TODO: list out some of the key considerations when making the program

## Application and Codebase Features
The following sections describe the thought process behind some of the different key features in the code. This is not meant as a definitive list but is meant to help supplement the comments in the code and explain some of the various aspects of the code. As a disclaimer, I'm a hobbyist button masher so there likely are some "non-pythonic" things going on in the code which I apologize for in advance.

### Physical Interface
To preface the code comments and discussion, the actual physical lout of the hardware should be considered. This is handled by the class `menu_page_template` and any children that inherit it. The below is a simplistic layout of the I/O buttons on the PCB for this app.

[1]   |               |   [4]
			|               |
[2]   |    screen     |   [5]
			|               |
[3]   |               |   [6]

1- Page up
2- Settings
3- Page Down
4- Scroll up
5- Enter/select
6- Scroll Down

### Graphical Layout
The following points summarize the general methodology and considerations when adding graphical features to the app. These are not set in stone rules but are generic considerations.

- The intended graphical layout of the app should contain elements that are clearly visible at a glance.
- Important parameters like the values of various data channels should be easily identifiable
- Some less important icons like indicators that are non-critical should be less conspicuous: at the discretion of the end user
- Multiple frames or pages to display different information should be available to easily switch between, to prevent cluttering a singular main window
- Critical data channels should have the ability to visibly warn the user when they are out of range (IE, too low or too high) and differentiate between a "warning" vs a "danger" range as well.

### UI Flow
The following information gives some insight to the intended flow of the application. This is a little more of a holistic view on why the code is organized the way it is. This is not meant as a definitive guide or absolute structure but more of a supplement to the existing code comments.

- One primary TK object provides the main window and application in which all things operate
	- This is defined as a class that contains any high-level supporting functions or variables
- Individual frames that are children of this master TK object class should be used to display different information
	- These individual frames then are defined as their own children classes. This enables typical Tk operators for creating/destroying/packaging/etc. to organize the display and updating of the various views
	- Each frame generally has several key functions
		- an `elements` named function where all the various display elements are placed and organized.
		- an `update` named function that recursively performs any label/display updates on a refresh interval
		- remaining support functions specific to the current frame. A good example would be any "bar graph" style update functions that are only applicable to the current view.
- The physical buttons are used to navigate between views for the user
- The available views and displays consist of the following
	- Primary gauge display or `Gauge0` should be used for the default view with critical monitoring information.
	- Settings display will contain any configurable options like backlight PWM control or other global configurations.
	- CAN sniffer display will list any received CAN PIDs since a reset, along with the most recent value. AS A REMINDER this is also beholden to the overall CAN filter that is configured in the app setup. There is an option to toggle the filter when viewing.
	- Various additional views should be called `Gauge1`, `Gauge2`, etc. that display any other elements the user desires.

# Known bugs and bug fixes
No current known bugs

# FAQ section
No current FAQ

# Copyright and licensing information
TBD this section is a work in progress to list the correct, legal licensure information. However, as a generic disclaimer;
 
The information included is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and non-infringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software or tools included in this repository.

# General Notes and References
While I am an engineer by trade, my area of focus is not computer architecture or system engineering. Likely some people have already looked at various aspects of the codebase and just shook their heads. That being said, I've compiled a list of considerations and notes for the project that have helped me along the way. These are listed below, in no particular order.

## References
Throughout the project, I have used many references, related to various aspects/items of the project. These are all compiled in the list below, in no particular order
- [Tk and Frames - lots of sub-links](https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter)
- [rPi GPIO](https://learn.sparkfun.com/tutorials/raspberry-gpio/python-rpigpio-api)
- [rPi GPIO](https://roboticsbackend.com/raspberry-pi-gpio-interrupts-tutorial/)
