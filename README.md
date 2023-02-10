# Blender6DofMouseAddon
Addon for the 6 DOF mouse I'm building

I am building this addon to be able to read serial data from [my homemade 6DOF Mouse](https://github.com/NangiDev/6DofMouse).
It will take the serial data and transform it to translation and rotation inside Blender viewport.

## Dependencies
* Blender
* Pyserial

### Install Pyserial for Blender
* Download the [pyserial source code](https://pypi.org/project/pyserial/#files). The file you're looking for ends with .tar.gz
* Unzipp what you've downloaded
* Copy the serial folder, it is under PySerial\pyserial-3.2.1\serial (the version can change)
* Paste the folder in your blender modules folder, 2.83\scripts\modules,
and now you should be able to use import serial
