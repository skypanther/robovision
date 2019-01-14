"""
Multi-threaded video frame acquisition - one thread continuously grabs frames
while the other pulls individual frames from a queue

Examples:

from robovision import robovision as rv

vs_webcam = rv.VideoStream(cam_id=0)
vs_ipcam = rv.VideoStream(source="ipcam", ipcam_url="http://10.15.18.101/mjpg/video.mjpg")
vs_picam = rv.VideoStream(source="picam")
vs_jetson = rv.VideoStream(source="jetson", resolution=(1920, 1080))

# use any of the above in this way to continuously read frames from the camera
vs_webcam.start()
while some_condition is True:
    frame = vs_webcam.read_frame()
    # do stuff with the frame
vs_webcam.stop()

"""
import sys

# any platform could support a webcam or IP camera so
# include the source libraries here
from .video.webcam import Webcam
from .video.ipcam import IPcam

valid_sources = "webcam", "ipcam", "picam", "jetson"


class VideoStream:
    preprocessor = None

    def __init__(self, source="webcam", cam_id=0, resolution=(320, 240), ipcam_url=""):
        if source not in valid_sources:
            print("Valid sources are {}".format(", ".join(valid_sources)))
            raise "InvalidSource"

        if source == "ipcam":
            self.source = IPcam(ipcam_url=ipcam_url)
        if source == "picam":
            # include the picam library only if on a Pi
            # this is not a meaningful check of whether
            # the code is actually running on a RPi
            if not sys.platform.startswith("linux"):
                print("You're not on a Raspberry Pi")
                raise "InvalidSource"
            from .video.picam import Picam
            self.source = Picam(resolution=resolution)
        if source == "jetson":
            # include the jetson library only if on a Jetson
            # this is not a meaningful check of whether
            # the code is actually running on a Jetson board
            if not sys.platform.startswith("linux"):
                print("You're not on a Jetson")
                raise "InvalidSource"
            from .video.jetsoncam import Jetsoncam
            self.source = Jetsoncam()
        if source == "webcam":
            self.source = Webcam(cam_id=int(cam_id))

    def add_preprocessor(self, preprocessor=None):
        self.preprocessor = preprocessor

    def start(self):
        self.source.start()

    def stop(self):
        self.source.stop()

    def read_frame(self):
        """
        Reads a frame, optionally passing it through a Preprocessor if one
        is set. Will start the stream if it"s not running already.

        :return: A single video frame in a format specific to the source
        """
        if not self.source.running:
            self.source.start()
        if self.preprocessor is not None:
            return self.preprocessor(self.source.read_frame)
        return self.source.read_frame()
