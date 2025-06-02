# PyDash_App - Information
This readme covers the application or "App" portion of the PyDash. For the PCB design, Enclosure design, or OS design, see the below repositories:
- PyDash_PCB
- [PyDash_OS](https://github.com/JungleGim/PyDash_OS)
- PyDash_Enclosure

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
 - Rev1a: 05/19/2025
   	- Added multi-frame (multi-view) capability
   	- Added GPIO (button) interrupt capability
   	- Can navigate between views with external buttons
   	- Added secondary view for CAN sniffer (displays all RX'd CANbus data)
   	- Added secondary views for settings and errors (partially populated)
   	- Minor UI tweaks for new views
   	- Minor file structure tweaks for new views
	
## Future Development
The below is a list of wants/needs for future revisions; loosely listed in order of importance.

### Critical items for immediate development 
- Current display channels are based on a broadcast network architecture. Update/enable remote request
	- For the current system, all CAN related params are broadcast on individual intervals. This is fixed to the remote module and the dash simply displays the RX'd information
   	- This doesn't work well for OE ECU's that have remote requests for the applciable PIDs and also, generally, a broadcast network can easily be saturated
   	- Update the dash display channel configuration class to have a boolean for "remote_req" and then "req_interval" to set the control params for remote request channels
- Implement a configuration XML file that is read on boot
	- Intent is to store all the display parameters into a XML file that can be externally edited.
	- This includes things like the base CAN PID, the various gauge vies, color themes, etc.
- Implement config file read on boot
- Enable/update USB communication related features
	- Overall intent would be to load a new settings file that has been sent to the PyDash. The main part of this is largely a hardware consideration where the PyDash_OS needs to be set up for USB device operation. Not much in the PyDash_App needs to be done.
- Create desktop multi-platform app as a display editor (not required for PyDash_App but would make it a much better user experience)
- Implement data logging of all RX'd CAN channels

### Additional future development
- A lot of the various "constants" defined everywhere should be converted to a dictionary
- Currently, the screen navigation has a "back" function to go to the previous screen. Since the 
    "previous frame" variable that controls this only works with a single "back" its more of a 
    "go to previous" than a true "go back" function. If there were multiple levels to go "back" to it
    would break in it's current implementation.

    Update the functionality of the "previous frame" var to a list of frames instead. Each time the user
    goes to the "next" frame level, it'll append to the list. Then each time the user selects the "back"
    button in an appropriate frame, a function can use the .pop() command to pull it off the list and
    navigate to the previous frame.
    
    for this to work properly, would have to track if a frame is a "subscreen" or not. If the frame is
    not a "subscreen", then it should NOT be appended to the list (e.g. if just navigating around the 
    home screens). The "settings" screen would be a great example of a sub-screen.

    EXAMPLE:
    At the home screen on initial start it should be a blank list. navigating to different
    gauge windows should stay blank. Going into "settings" the list would be whatever window the user
    came from, say [Gauge0]. Then if theres another settings sub-window it would be 
    [Gauge0, settings] (when in the settings_sub1 window), etc. Then clicking the "back" button
    would pop "settings" off and return from "setttings_sub1" to "settings". The list then would be
    [Gauge0]. Clicking the "back" button again would pop "Gauge0" off and return from "settings" to
    "Gauge0".

    - make a "goto_prev_frame" type function to handle this.

- Create a new "errors" view
    - need a class and frame for "current error"
        *class could be used globally for tracking errors (what/where/severity, etc.)
        *view would show any logged/resolved issues.

- Organize the main code 
    - as an example, the "update stringvars" function could be easily placed in the main window class, this doesn't
        have to be a "global" by any means.
    - think about moving the CAN instancing and values into the "CAN defines" file. Alternatively, this could
        also be in the main window class instead of a "global"
    - the "update listbox" function should be moved to the "draw funcs" class. Do similar to others where the
        object, data to include, and reference are passed
    - move the "goto_frames", and "frame_switch" functions to the "SCRNdefines" file in the "scrn" struct. 
        will need a "scope" var passed to them so when instancing the frames they're referenced correctly back 
        to the master window. Maybe not since the frame (As instanced/stored in the dict) already
        has that information?
    - after moving the "goto_frames" and "frame_Switch" funcs, it would also subsume the need for updating the
        callback in the main window (since it would exist in the instanced screen class 
        in that file already) which would make things much cleaner.
- Now that a better class structure and frames are being used, many of the high-level CAN functions should be placed into the main window class, not just as a global routine. This isn't super critical from an operation standpoint but would help make things more refined.
- Some of the view functions like the "color update" for out-of-range values are going to be used across multiple view frames. These should be placed into the master class so they're able to be referenced by multiple views. I think it fits better into the master class object vs placing them into the `drawFuncs` or drawing function library, just because they are specific to the dash operation (vs a graphical drawing tool).
- Implement multiple views with window switching on GPIO button presses
- Implement a "Settings" window to adjust common values like screen brightness
	- Also, eventually allow for value configuration of the various on-dash items. This should be storable/updatable via something like a local XML file
- See above point; create the functionality for the program to read/load a configuration from file on start\
	- potentially use something like an XML file
	- File will need to have ALL vars and positions and data in the data_info struct then
  - Implementing will allow for the config file to dictate what's stored where and how. Essentially, this will take place of the static variable definition that's currently being used.
  - having an external config file also allows the user to manipulate/upload it separately. This has the potential to transition into a display configurator app
  - Trying to allocate all variables dynamically may cause an issue. However, could basically handle it like things are now, where the function will just "append" another entry to an array for every variable in the XML file. The code would simply just be a blank instance of the dash data class until the config file is read.
	- Potentially could limit dynamic loading to 24-32 vars per screen to help ensure that no strangely large array is created.
- Test the gen can bus filter function
	- Intent is that the various defined data channels should be associated with an CANbus PID, so only let through those messages. This shouldn't have to be hard-coded and can be programmatically generated at the start of the program.
- Add in the data channel timeout function.
	- If data not rx'd every given period for a channel, then display "NO DAT" or some other warning on the display
- Simplify the RPM bar graph to be just a plain rectangle. Currently a transparency window is used to give it a "shape" but that's not needed and causes some extra work to make a new background image.
	- Ideally, could figure out how to make an alpha-channel mask for custom shapes
- Make a compile script to package the compiled/completed app into a target directory.

## Repository Directory Map
The following information describes the folders found in the root directory of this repository
- (folder) App
	- This is the main application folder
	- (folder) archive
		- Contains previous versions of the application. TBD will be superseded with the full implementation of GIT
- (folder) Dev-Testing
	- This folder contains some of the WIP or simplified applications used to develop the app. Usually the intent is to create smaller, focused elements that can be integrated into the main program later.
	- For example, initially the app had only one page, so a simplified "multi frame" app was used to test GPIO interrupts and multiple frame navigation separate from the main app.

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
TBD: Include dependent packages/includes in the code

As a reminder, any listed dependent packages must be on both the developing OS and the Linux OS running the app (IE PyDash_OS must have the package)

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

## Application and Codebase Features
The following sections describe the thought process behind some of the different key features in the code. This is not meant as a definitive list but is meant to help supplement the comments in the code and explain some of the various aspects of the code. As a disclaimer, I'm a hobbyist button masher so there likely are some "non-pythonic" things going on in the code which I apologize for in advance.

### Physical Interface
To preface the code comments and discussion, the actual physical lout of the hardware should be considered. This information is contained in the screen defines or `SCRNdefines.py` library but is listed here again for discussion. The below is a simplistic layout of the I/O buttons on the PCB for this app.
```
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
```

### Graphical Layout
The following points summarize the general methodology and considerations when adding graphical features to the app. These are not set in stone rules but are generic considerations.

- The intended graphical layout of the app should contain elements that are clearly visible at a glance.
- Important parameters like the values of various data channels should be easily identifiable
- Some less important icons like indicators that are non-critical should be less conspicuous: at the discretion of the end user
- Multiple frames or pages to display different information should be available to easily switch between, to prevent cluttering a singular main window
- Critical data channels should have the ability to visibly warn the user when they are out of range (IE, too low or too high) and differentiate between a "warning" vs a "danger" range as well.

### Application Flow
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
	- Primary gauge display or `Gauge0` should be used for the default view with critical monitoring information
	- Settings display will contain any configurable options. TBD completion, but will eventually contain options like backlight PWM control or other global configurations
	- CAN sniffer display will list any received CAN PIDs since a reset, along with the most recent value. AS A REMINDER this is also beholden to the overall CAN filter that is configured in the app setup.
	- TBD then various additional views should be called `Gauge1`, `Gauge2` etc that display any other elements the user desires.

### Application code elements and files
The following discusses some of the code elements and library files along with the intent of their operation/existence. Again, this is not meant as a complete definitive guide but should supplement the existing code comments.

#### Files and Libraries
- py_dash
	- Primary script that gets called to run the program
- Library files
	- CANdefines
		- This file is intended to contain all of the CAN related control information
		- The `dash_info` class that contains all the channels to display is defined here
		- Any limits like indicator on/off CAN packet values or bar graph max values are defined here
		- Currently, the displayed values and their associated limits, positioning information, etc. are hard-coded here. Future revision work should hopefully remove this in favor of an externally defined config file
	- dash_defines
		- This file is intended to contain any of the miscellaneous high-level dash information. This includes screen size resolution, any file paths used throughout, refresh rate, etc.
	- dash_drawFuncs
		- This file is intended to contain any common graphical tools or defines. For example, text colors, warning limit colors, fonts, etc. are all defined here.
		- Additionally, common graphical display functions like rounded rectangle drawing, circle drawing, text labels, and image processing are defined here.
	- dash_SCRNdefines
		- This file is intended to contain any physical interface defines like the GPIO handling, as well as generic screen information like the graphical layout.
		- The `screen info` class that contains the available frames, as well as opening/closing/moving/updating frame functions is defined here.

#### Code Elements
- CAN bus
	- Once the CAN phsyical layer is established, generally the defined listener routine handles any processing of the data
	- Primarity, the `upd_CAN_data` function's job is to upate the values of any displayed labels/elements
	- Additionally, as second function (TBD) should just store all received CAN messages in a separate class or dictionary
	- The `upd_CAN_dec` function interprets and converts the recieved CAN frame into a decimal value.
	- A separate `gen_CAN_filters` function handles programatically generating the CANbus filter based on the defined data to display
		- Currently this is not implemented and all potential CAN messages Rx'd are processed by the app
- Display values / elements
	- Each display element should have a label, which indicates the data channel being displayed as well as a second stringvar for the actual data
	- Using a stringvar allows for the value to be continually updated based on the linked data field in the display data class
	- Furthermore, each pair of label and value has a background padding to provide several functions
		- the first is a visual separation from the background. This makes it easier to see when in use
		- the second is that when adjusting the "warning" and "danger" colors of the label, the background padding is also adjusted accordingly to yellow or red for a more prominent visual indicator that the associated channel has a potential range concern.
- Class: dash_info
	- found in the `CANdefines` library file
	- The intent of this class is to handle the display of the various data channels and indicators on the display
	- The class itself contains the information to set the graphical label, the data type, any potential offset that's in the CAN PID per its definition, position information for the label and value, hi/lo out of bounds warning information, a reference to the label scope (which canvas item it's displayed on) and a reference to any function that gets called when the value is updated (or when a CAN frame associated with that PID is received)
- Class: screen_info
	- found in the `SCRNdefines` library file
	- The intent of this class is to handle the display switching and various elements that go along with it.
	- Future use also includes a class to handle global definitions like backlight PWM control
	- The class itself tracks a list of all the available frames that contain different view information, the current frame displayed as a way of state handling, and also any functions related to switching views

- Class: dash_settings
	- found in the `dash_defines` library file
	- The intent of this class is to handle any of the high-level like, core system level settings
   	- Pretty sparse for now, but eventually will house any of the user-configurable settings like the backlight level, CAN base address, and others. 

- View switching
	- The indended function is to handle any user inputs from the GPIO physical buttons. This primarily focuses on display switching but also includes things like how various elements on the current view respond to a button push.
	- Initial attempt with this is handled in a "state machine" manner where the current view/frame being displayed dictates how the various button pushes are handled. This was chosen because the various buttons may have different actions depending on the current view.
	- A potential concern with this is that it can/could get rather large and honestly kind of gangly. I'm currently not sure what a best practice is for this type of thing and/or what a good approach would be.

# Known bugs and bug fixes
No current known bugs

# FAQ section
No current FAQ

# Copyright and licensing information
TBD this section is a work in progress to list the correct, legal licensure information. However, as a generic disclaimer;
 
The information included is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and non-infringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software or tools included in this repository.

# General Notes and References
While I am an engineer by trade, my area of focus is not computer architecture or system engineering. Likely some people have already looked at various aspects of the codebase and just shook their heads. That being said, I've compiled a list of considerations and notes for the project that have helped me along the way. These are listed below, in no particular order.

## Python Notes


## References
Throughout the project, I have used many references, related to various aspects/items of the project. These are all compiled in the list below, in no particular order
- TBD any notable references
