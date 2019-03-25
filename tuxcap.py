#! /usr/bin/python3 

import sys
import time
import threading
import collections
from threading import Thread
from cv2 import *

image_ring = collections.deque("",200);

class cam_thread(Thread):   
    
    should_run = True

    def take_pic(self,name):

        cam = VideoCapture(0)
        conf, img = cam.read()

        if conf:    # frame captured without any errors
            namedWindow("cam-test")
            imshow("cam-test",img)
            print("image taken")
            waitKey(0)
            destroyWindow("cam-test")
            imwrite(name+".jpg",img)
            return(img)


    def run(self):
        should_run = True
        count = 0

        while should_run:

            image_ring.append(count)
            self.take_pic(str(count))
            count = count + 1
            time.sleep(1) 

    def stop_thread(self):
        print("Ending capture thread!")
        should_run = False


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
        else:
            print("huh, neat")

    cam_loop.stop_thread();

    print("threads have stopped")

    sys.exit()

if __name__ == "__main__":
    main()
