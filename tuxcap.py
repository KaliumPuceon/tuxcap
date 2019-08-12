#! /usr/bin/python3 -u

import sys
import os
import time
from datetime import datetime
import collections
from threading import Thread
from cv2 import *
import RPi.GPIO as GPIO
import tux_config as tc

pre_buffer = tc.pre_buffer
frame_period = tc.frame_period
post_buffer = tc.post_buffer

trigger_pin = tc.trigger_pin
gpio_edge = tc.gpio_edge

pit_capture_dir=tc.pit_capture_dir
apms_capture_dir=tc.apms_capture_dir
pit_image_dir=tc.pit_image_dir
apms_image_dir=tc.apms_image_dir
debug=tc.debug

image_ring_0 = collections.deque("",pre_buffer+post_buffer) 
#image_ring_1 = collections.deque("",pre_buffer+post_buffer) 

class cam_thread(Thread):  # An enormous pile of state dressed like a thread
    
    should_run = None
    count = None
    frames_remaining = None
    save_requested = None
    lock_requested = None
    cam_id = None
    imname = None
    ispit = None

    def __init__(self, cam_id):
        super(cam_thread, self).__init__() 
        self.cam_id = cam_id

        self.cam = VideoCapture(cam_id)  # Set up camera

        self.cam.set(CAP_PROP_FRAME_WIDTH,tc.image_width)
        self.cam.set(CAP_PROP_FRAME_HEIGHT,tc.image_height)
        self.cam.set(CAP_PROP_AUTOFOCUS,1)
        self.cam.set(CAP_PROP_AUTO_EXPOSURE,1)
        self.ispit = False
        # Camera Setup Done

    def setPit(self, b): # Set ispit variable
        self.ispit = b;
   
    def run(self):

        self.should_run = True
        self.count = 0
        self.frames_remaining = 0
        self.save_requested = False
        self.lock_requested = False

        print("Camera "+str(self.cam_id)+" Running")

        try:
            while self.should_run: # Allows graceful closeout
                
                if not(self.lock_requested): # Don't take pictures when saving
                    if self.cam_id == 0:
                        image_ring_0.append(self.take_pic())
                    else:
                        image_ring_1.append(self.take_pic())
                    time.sleep(frame_period) 

                if self.save_requested: # Munge counters when save requested

                    self.frames_remaining = self.frames_remaining - 1

                    if self.frames_remaining <= 0: # Pass off to save_buffer
                        self.save_requested = False
                        self.save_buffer_now()
                        
            self.cam.release()
            
        except Exception as e:
            print(e)
            self.cam.release()
            os._exit(1)


    def take_pic(self): # Returns a single frame

        conf, img = self.cam.read() # Get image

        if conf: # frame captured without any errors
            return(img)


    def stop_thread(self): # Flip thread maintenance variable
        print("Ending capture thread!")
        self.should_run = False

    def request_buffer(self, filename, channel): # Create countdown to save buffer
        if self.save_requested == False:
            print("start buffer")
            self.imname = filename
            self.frames_remaining = post_buffer
            self.save_requested = True
        else:
            print("Buffering already in progress")



    def save_buffer_now(self): # Create locks and mark buffer for saving

        if self.lock_requested == False:

            print("Start saving buffer")
            self.lock_requested = True # prevent new images entering buffer

            img_count = 0
            
            if self.ispit:
                dirname = apms_capture_dir+"/"+self.imname
                bkfilename = apms_image_dir+"/"+self.imname+".jpg"
            else:
                dirname = pit_capture_dir+"/"+self.imname
                bkfilename = pit_image_dir+"/"+self.imname+".jpg"

            try:
                os.makedirs(dirname)
            except FileExistsError:
                os.system("rm -rf "+dirname)
                print("Replacing Existing File")

                

            if self.cam_id==0:

                imwrite(bkfilename, image_ring_0[pre_buffer])

                for image in image_ring_0:

                    imwrite(dirname + "/" + str(img_count) + ".jpg",image) # save
                    img_count = img_count + 1

            else:

                imwrite(bkfilename, image_ring_1[pre_buffer])

                for image in image_ring_1:

                    imwrite(dirname + "/" + str(img_count) + ".jpg",image) # save
                    img_count = img_count + 1

            # endif

            # make a call to ffmpeg to video-ify the images
            print("Video-ifying images")
            os.system("ffmpeg -threads 2 -r 10 -f image2 -i "+dirname+"/\%d.jpg "+dirname+"/"+"capture.mp4 2> /dev/null > /dev/null && rm "+ dirname + "/*.jpg")
            print("Video Happening")

            self.lock_requested = False  # release lock on buffer
            print("Buffer saved, lock released")


            # make a call to delete source images
            print("Video done")
            
        else:
            print("Buffer presently saving")

def main():

    import time

    os.system("stty -F /dev/ttyAMA0 115200")
    os.system("stty -F /dev/ttyUSB0 115200")
    #os.system("stty -F /dev/ttyACM0 115200")
    os.system("/home/pi/scripts/mount_disk.sh")

    time.sleep(1)

    print("Creating capture dirs")

    try:
        print("Capture dir created at "+pit_capture_dir + " and " + apms_capture_dir)
        os.makedirs(pit_capture_dir)
        os.makedirs(apms_capture_dir)
    except FileExistsError:
        print("Capture dir already exists at")
    except PermissionError:
        print("Permissions insufficient to create capture dir: Try something else")
        sys.exit()

    try:
        os.makedirs(pit_image_dir)
        os.makedirs(apms_image_dir)
        print("Image dir created at "+ pit_image_dir +" and " +apms_image_dir)
    except FileExistsError:
        print("Image dir already exists at")
    except PermissionError:
        print("Permissions insufficient to create image dir: Try something else")
        sys.exit()

    cam0_loop = cam_thread(0) 
    #cam1_loop = cam_thread(1)
    cam0_loop.setDaemon(True)
    #cam1_loop.setDaemon(True)

    print("starting camera record loop")
    cam0_loop.start()
    #cam1_loop.start()

    # GPIO Setup

    GPIO.setmode(GPIO.BCM)

    GPIO.setup(trigger_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    edge = 0
    
    if gpio_edge == 0:
        edge = GPIO.RISING
    else:
        edge = GPIO.FALLING

    def collect_images(arg):
        print("GPIO Fired")
        cam0_loop.setPit(True)
        now = datetime.now()
        timestring = now.strftime("%d%b%Y_%H%M%S")
        cam0_loop.request_buffer(timestring, arg)
        #cam1_loop.request_buffer(arg)

    GPIO.add_event_detect(trigger_pin, edge, callback=collect_images, bouncetime=200)

    ans = ""

    if debug:

        while ans != 'q': # command console loop

            ans = input("Enter Command >  ")

            if ans == "show":
                print("there are " + str(len(image_ring_0)) + " items in the ring 0")
                #print("there are " + str(len(image_ring_1)) + " items in the ring 1")

            elif ans == "cap":
                cam0_loop.request_buffer(1)
                #cam1_loop.request_buffer(1)

            elif ans in ["help","h","?","wat"]:
                print("?, h, help, wat: Show this page")
                print("cap: mark current buffer for capture")
                print("show: show how many items are currently in buffer")
                print("q: quit")

            elif ans in ["q"]:
                print("That's a wrap")

            else:
                print("I don't understand. Enter ? for help")

    while True and ans != "q":
        ser_in = input()
        ser_array = ser_in.split(" ")

        if ser_array[0] == "TAG:":
            date = ser_array[2].replace("/", "-")
            time = ser_array[3].replace(":", "-")
            time = time.replace(".", "-")
            tag = date+"_"+time+"_"+ser_array[4]
            tag_data = ser_array[4]

            cam0_loop.setPit(False)
            cam0_loop.request_buffer(tag, 0)

            print(tag_data) 
            with open("/dev/ttyAMA0", "w") as f:
                print(tag_data, file=f)

        else:
            print("Busted Serial Signal")

    while True and ans != 'q':
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            break

    cam0_loop.stop_thread()
    #cam1_loop.stop_thread()
    GPIO.cleanup()

    print("threads have been stopped")

    sys.exit()

if __name__ == "__main__":
    main()
