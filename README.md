# TuxCap 🐧

TuxCap is a program for buffering a series of photos and capturing the time
before, during and after some trigger event using a raspberry pi and a USB
webcam.

At the moment it is in very very development status, configuration being a
number of variables floating around inside the tuxcap.py file.

The command line interface is basic, and accepts the following commands:

h, help, ?: Show Help
q: quit
show: Show number of images in buffer
cap: save current buffer to disk when the time comes

This was developed at the request of the University of Cape Town for a penguin
conservancy project, in order to provide a large amount of photo data on
penguins. With some adaptation it could really be useful for any situation where
you have a trigger line and the need to capture buffered still images.

# Dependencies and Installation

TuxCap is written for Python 3. Requirements are updated and can be found in the
requirements.txt file. It depends on OpenCV for camera handling and Numpy
because OpenCV depends on it.

# Usage

Running tuxcap.py will start buffering video on the first available video input
device found, and present a command line interface. This can be used to test the
system, by triggering captures. As of writing there is no configuration file or
interface.
