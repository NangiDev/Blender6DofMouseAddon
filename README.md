# Blender6DofMouseAddon
Addon for the 6 DOF mouse I'm building

I am building this addon to be able to read serial data from [my homemade 6DOF Mouse](https://github.com/NangiDev/6DofMouse).
It will take the serial data and transform it to translation and rotation inside Blender viewport.

## Dependencies
* Blender 2.8 or greater
* Pyserial 3.2 or greater

### Install Pyserial for Blender
* Download the [pyserial source code](https://pypi.org/project/pyserial/#files). The file you're looking for ends with .tar.gz
* Unzipp what you've downloaded
* Copy the serial folder, it is under PySerial\pyserial-3.2.1\serial (the version can change)
* Paste the folder in your blender modules folder, 2.83\scripts\modules,
and now you should be able to use import serial

## Actuall Blender Add-on
### [viewport_control_no_thread.py](viewport_control_no_thread.py)
This is the actuall add-on to install

## Tests
### [Blender Minimal](tests/blender_minimal.py)
This is just a simpel small Blender add-on to prove that we can read fast enough

### [Read Simulator](tests/read_simulator.py)
This is a simple python program that reads from serial. Useful for testing and you don't want to do it through Blender add-on

### [Write Simulator](tests/write_similator.py)
This is a simple python program that writes to serial. Useful for testing and you don't have you Arduino hardware

## Screenshots
### Addon GUI
![Addon GUI](images/gui.png)
