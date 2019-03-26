# TuxCap 🐧

TuxCap is a program for buffering a series of photos and capturing the time
before, during and after some trigger event using a raspberry pi and a USB
webcam. This particular variant stores the captures as an mp4 video to save
space, given that it does not have network storage.

At the moment it is in very very development status, configuration being a
number of variables floating around inside the tuxcap.py file.

The command line interface is basic, and accepts the following commands:

* h, help, ?: Show Help
* q: quit
* show: Show number of images in buffer
* cap: save current buffer to disk when the time comes

This was developed at the request of the University of Cape Town for a penguin
conservancy project, in order to provide a large amount of photo data on
penguins. With some adaptation it could really be useful for any situation where
you have a trigger line and the need to capture buffered still images.

# Dependencies and Installation

TuxCap is written for Python 3. Requirements are updated and can be found in the
requirements.txt file. It depends on OpenCV for camera handling and Numpy
because OpenCV depends on it. You can install all dependencies on x86-64 debian
with:

```
pip3 install -r requirements.txt
sudo apt install ffmpeg
```

On the Raspbian, dependencies are not all available through pip. Instead, run
the following to install the relevant packages:

```
pip3 install opencv-python
sudo apt install ffmpeg libatlas3-base libcblas3 libjasper1 libqt4-test libgstreamer1.0-0 libqt4-dev-bin
```

You may need to add the user running the program to the `video` group, using
`usermod -aG video <user>`

# Usage

The program will automatically identify the first Video Input device attached to
the system, on the Pi this will correspond to a webcam that is plugged in.

Running tuxcap.py will start buffering video on the first available video input
device found, and present a command line interface. This can be used to test the
system, by triggering captures. As of writing there is no configuration file or
interface.

Please check the code if you are using it now, as the capture path is hardcoded
and will not self-generate.

