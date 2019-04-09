#! /usr/bin/python3 

import sys
import os
import time
import collections
from threading import Thread
from cv2 import *
import tux_config as tc

pre_buffer = tc.pre_buffer
frame_period = tc.frame_period
post_buffer = tc.post_buffer

trigger_pin = tc.trigger_pin
gpio_edge = tc.gpio_edge

capture_dir=tc.capture_dir
image_dir=tc.image_dir

image_ring = collections.deque("",pre_buffer+post_buffer) 

class cam_thread(Thread):  # An enormous pile of state dressed like a thread
    
    should_run = None
    count = None
    frames_remaining = None
    save_requested = None
    lock_requested = None
    
    def run(self):

        self.cam = VideoCapture(0)  # Set up camera

        self.cam.set(CAP_PROP_FRAME_WIDTH,tc.image_width)
        self.cam.set(CAP_PROP_FRAME_HEIGHT,tc.image_height)
        self.cam.set(CAP_PROP_AUTOFOCUS,1)
        self.cam.set(CAP_PROP_AUTO_EXPOSURE,1)

        # Camera Setup Done

        self.should_run = True
        self.count = 0
        self.frames_remaining = 0
        self.save_requested = False
        self.lock_requested = False

        try:
            while self.should_run: # Allows graceful closeout
                
                if not(self.lock_requested): # Don't take pictures when saving
                    image_ring.append(self.take_pic())
                    time.sleep(frame_period) 

                if self.save_requested: # Munge counters when save requested

                    self.frames_remaining = self.frames_remaining - 1

                    if self.frames_remaining <= 0: # Pass off to save_buffer
                        self.save_requested = False
                        self.save_buffer_now()

        except Exception as e:
            print(e)
            os._exit(1)


    def take_pic(self): # Returns a single frame

        conf, img = self.cam.read() # Get image

        if conf: # frame captured without any errors
            return(img)


    def stop_thread(self): # Flip thread maintenance variable
        print("Ending capture thread!")
        self.should_run = False

    def request_buffer(self): # Create countdown to save buffer
        if self.save_requested == False:
            print("start buffer")
            self.frames_remaining = post_buffer
            self.save_requested = True
        else:
            print("Buffering already in progress")



    def save_buffer_now(self): # Create locks and mark buffer for saving

        if self.lock_requested == False:

            print("Start saving buffer")
            self.lock_requested = True # prevent new images entering buffer

            img_count = 0
            
            dirname = capture_dir+"/"+str(int(time.time()))
            bkfilename = image_dir+"/"+str(int(time.time()))+".jpg"
            os.mkdir(dirname)

            imwrite(bkfilename, image_ring[pre_buffer])

            for image in image_ring:

                imwrite(dirname + "/" + str(img_count) + ".jpg",image) # save
                img_count = img_count + 1

            self.lock_requested = False  # release lock on buffer
            print("Buffer saved, lock released")

            # make a call to ffmpeg to video-ify the images
            print("Video-ifying images")
            os.system("ffmpeg -r 10 -f image2 -i "+dirname+"/\%d.jpg "+dirname+"/capture.mp4 2> /dev/null 1> /dev/null")

            # make a call to delete source images
            print("Video done, Removing source images")
            
            os.system("rm " + dirname +"/*.jpg")

        else:
            print("Buffer presently saving")

def main():

    print("Creating capture dirs")

    try:
        os.makedirs(capture_dir)
        print("Capture dir created at "+capture_dir)
    except FileExistsError:
        print("Capture dir already exists at "+ capture_dir)
    except PermissionError:
        print("Permissions insufficient to create capture dir: Try something else")
        sys.exit()

    try:
        os.makedirs(image_dir)
        print("Image dir created at "+image_dir)
    except FileExistsError:
        print("Image dir already exists at "+ image_dir)
    except PermissionError:
        print("Permissions insufficient to create image dir: Try something else")
        sys.exit()

    cam_loop = cam_thread() 
    cam_loop.setDaemon(True)

    print("starting camera record loop")
    cam_loop.start()

    ans = ""

    while ans != 'q': # command console loop

        ans = input("Enter Command >  ")

        if ans == "show":
            print("there are " + str(len(image_ring)) + " items in the ring")

        elif ans == "cap":
            cam_loop.request_buffer()

        elif ans in ["help","h","?","wat"]:
            print("?, h, help, wat: Show this page")
            print("cap: mark current buffer for capture")
            print("show: show how many items are currently in buffer")
            print("q: quit")

        elif ans in ["q"]:
            print("That's a wrap")

        else:
            print("I don't understand. Enter ? for help")

    cam_loop.stop_thread();

    print("threads have been stopped")

    sys.exit()

if __name__ == "__main__":
    main()
