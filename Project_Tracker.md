# PyDash Application - Project Tracker
project tracker for WIP issues, what's currently being worked on, and anything that may need to move to the actual README file

## Version
Version: 2.0 - TBD
Build Date: N/A

# WIP Version TODO list
* Test the gen can bus filter function
	- Intent is that the various defined data channels should be associated with an CANbus PID, so only let through those messages. This shouldn't have to be hard-coded and can be programmatically generated at the start of the program.
    - Quick/easy way to do this would be limit the config.XML to only a couple channels and then toggle on/off in the CAN sniffer view

* Need to update the "builder" app for new config information
    - Remember there will be a few aspects to include/change/update
        + the actual UI for entering/changing these
        + the builder config file for making/saving dashes
        + the exported App config
        + error checks
    - Updated fields
        + old "PID" changed to "AID" - Arbitration ID (AID) more universal and less confusing with OBD2 PID
        + added ECU RX/TX IDs to CANcore
        + added OBD2 yes/no and PID fields to CANch

* Need to test a config file using thge new OBD2 data channel information

# Development Finishing
Things that were changed as a "debug mode" for development that should be reverted for final release
* sys.py file
	- remember to udpate "root_dir" for development vs final use
	- remember to include the rPIGPIO library for final use
* compile
	- run a compileall so that they're pyc files for the final use

# Future Updates
Include any items below in the appropriate README.md file section
(none)