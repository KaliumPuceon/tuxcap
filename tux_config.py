# Config file help for tuxcap.py
# Please set ALL of these to your desired values
# pre_buffer   : number of images to capture before trigger (integer)
# post_buffer  : number of images to capture after trigger (integer)
# frame_period : number of seconds between frames (float)
# save_video   : Should captures be converted to a video? (True/False)
# save_images  : Should original images be saved if a video is made? (True/False)
# capture_dir  : Path to store captures in (string)
# image_width  : capture image resolution width (integer)
# image_height : capture image resolution height (integer)
# trigger_pin  : which pin is used for the signal (integer)
# gpio_edge    : Trigger on rising or falling edge (0: rising, 1:falling)

pre_buffer   = 100
post_buffer  = 100
frame_period = 0.1
save_video   = True
save_images  = False
capture_dir  = "/home/kalium/code/tuxcap/captures/"
image_width  = 1280
image_height = 720
trigger_pin  = 10
gpio_edge    = 1

