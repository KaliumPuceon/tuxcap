# TuxCap 🐧

TuxCap is a program for buffering a series of photos and capturing the time
before, during and after some trigger event using a raspberry pi and a USB
webcam. The captures can be stored as a folder of jpegs or as an mp4 video,
depending on your size limitations and quality requirements.

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
because OpenCV depends on it. If you intend to create video captures, `ffmpeg`
should be installed. You can install all dependencies on x86-64 debian with:

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

the file `tux_config.py` serves to set up the system and contains the default
settings. You can set the number of images taken, the frame rate, whether they
are saved as video, images or both, where they are stored, and the image
resolution. The system does not yet support automatic triggering on a GPIO edge,
but that will be added soon.

Running tuxcap.py will start buffering video on the first available video input
device found, and present a command line interface. This can be used to test the
system, by triggering captures. As of writing there is no configuration file or
interface.

# License and Legal

This code licensed under the MIT License, meaning you're free to do almost
anything with it. Please see the `LICENSE` file for more details.
