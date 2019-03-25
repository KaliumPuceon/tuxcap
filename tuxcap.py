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
    
    should_run = True      # Used to end thread gracefully
    save_requested = False # Current buffer will be saved when frames_remaining = 0
    frames_remaining = 0   # Countdown to save buffer when save_requested True
    lock_requested = False # Prevent new images being dequed when saving

    def take_pic(self):

        cam = VideoCapture(0)
        conf, img = cam.read()

        if conf:    # frame captured without any errors
            print("image taken")
            #imwrite(name+".jpg",img)
            return(img)


    def run(self):
        self.should_run = True
        self.count = 0
        self.frames_remaining = 0
        self.save_requested = False
        self.rock_requested = False

        while self.should_run:
            
            if not(self.lock_requested):
                image_ring.append(self.take_pic())
                time.sleep(frame_period) 

            if self.save_requested:
                self.frames_remaining = self.frames_remaining - 1
                if self.frames_remaining <= 0:
                    self.save_requested = False
                    self.save_buffer_now()



    def stop_thread(self):
        print("Ending capture thread!")
        self.should_run = False

    def request_buffer(self):
        if self.save_requested == False:
            print("start buffer")
            frames_remaining = post_buffer
            self.save_requested = True
        else:
            print("Buffering already in progress")

    def save_buffer_now(self):

        if self.lock_requested == False:
            self.lock_requested = True

            img_count = 0

            dirname = "/home/kalium/code/tuxcap/captures/"+str(int(time.time()))

            os.mkdir(dirname)

            for image in image_ring:
                print("saving image "+str(img_count))
                imwrite(dirname + "/" + str(img_count) + ".jpg",image)
                img_count = img_count + 1

            self.lock_requested = False
        else:
            print("Buffer presently saving")


def main():
    cam_loop = cam_thread()
    cam_loop.setDaemon(True)

    print("starting camera record loop")
    cam_loop.start()

    ans = ""

    while ans != 'q':

        ans = input("Tell me something new: ")

        if ans == "show":
            print(image_ring)
            print(len(image_ring))
        elif ans == "cap":
            cam_loop.request_buffer()
        else:
            print("huh, neat")

    cam_loop.stop_thread();

    print("threads have stopped")

    sys.exit()

if __name__ == "__main__":
    main()
