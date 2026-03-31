# PyDash Application - Project Tracker
project tracker for WIP issues, what's currently being worked on, and anything that may need to move to the actual README file

## Version
Version: 2.0 - TBD
Build Date: N/A

# WIP Version TODO list
* CANch scalars
	- should not allow for a scalar of 0. Should be some non-zero value (even a negative decimal is OK just not zero)
	- add a config check to make sure its not zero
* Test the gen can bus filter function
	- Intent is that the various defined data channels should be associated with an CANbus PID, so only let through those messages. This shouldn't have to be hard-coded and can be programmatically generated at the start of the program.
* Add uSD detect
	- Need to incorporate the uSD detect pin into the app
	- if the uSD det is open, then:
		+ logging shouldn't be allowed to be enabled (log err message)
		+ check for error condition on start/load
		+ re-loading config from menu shouldn't be allowed
* Add option to re-load dash (or rather check for new config zip) in menu
	- inserting the uSD card doesn't auto-trigger a dash config check/reload (and i don't want it to) but should add an option in the menu to check/reload so that it doesn't require a power-cycle to reload the dash config.

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