#! /usr/bin/python3 

import sys
import os
import time
import threading
import collections
from threading import Thread
from cv2 import *

num_captures = 200
frame_period = 0.1
post_buffer = 100

image_ring = collections.deque("",num_captures);

class cam_thread(Thread):   
    
    should_run = True
    count = 0
    frames_remaining = 0
    save_requested = False
    lock_requested = False

    def take_pic(self): # Returns a single frame

        cam = VideoCapture(0)  # Set up camera
        conf, img = cam.read() # Get image

        if conf:    # frame captured without any errors
            return(img)


    def run(self):
        self.should_run = True
        self.count = 0
        self.frames_remaining = 0
        self.save_requested = False
        self.lock_requested = False

        while self.should_run: # Allows graceful closeout
            
            if not(self.lock_requested): # Don't take pictures when saving
                image_ring.append(self.take_pic())
                time.sleep(frame_period) 

            if self.save_requested: # Munge counters when save requested

                print(self.frames_remaining)
                self.frames_remaining = self.frames_remaining - 1

                if self.frames_remaining <= 0: # Pass off to save_buffer
                    self.save_requested = False
                    self.save_buffer_now()


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

            self.lock_requested = True # prevent new images entering buffer

            img_count = 0
            
            dirname = "/home/kalium/code/tuxcap/captures/"+str(int(time.time()))
            os.mkdir(dirname)

            for image in image_ring:
                print("saving image "+str(img_count))
                imwrite(dirname + "/" + str(img_count) + ".jpg",image) # save
                img_count = img_count + 1

            self.lock_requested = False  # release lock on buffer
        else:
            print("Buffer presently saving")


def main():
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
        else:
            print("I don't understand. Enter ? for help")

    cam_loop.stop_thread();

    print("threads have stopped")

    sys.exit()

if __name__ == "__main__":
    main()
