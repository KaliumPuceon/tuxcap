#! /usr/bin/python3 

import sys
import time
import threading
import collections
from threading import Thread
from cv2 import *

image_ring = collections.deque("",20);

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
        should_run = True
        count = 0
        frames_remaining = 0
        save_requested = False
        lock_requested = False

        while should_run:
            
            if not lock_requested:
                image_ring.append(self.take_pic())
                time.sleep(0.1) 

            if save_requested:
                frames_remaining = frames_remaining - 1
                if frames_remaining <= 0:
                    self.save_buffer_now()



    def stop_thread(self):
        print("Ending capture thread!")
        should_run = False

    def request_buffer(self):
        if save_requested == False:
            frames_remaining = 10
            save_requested = True
        else:
            print("Buffering already in progress")

    def save_buffer_now(self):

        if lock_requested == False:
            lock_requested = True

            count = 0
            for image in image_ring:
                os.mkdir("./captures/"+str(int(time.time())))
                print("saving image "+str(count))
                imwrite(str(count) + ".jpg",image)

            lock_requested = False
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
        elif ans == "cap":
            cam_loop.request_buffer()
        else:
            print("huh, neat")

    cam_loop.stop_thread();

    print("threads have stopped")

    sys.exit()

if __name__ == "__main__":
    main()
