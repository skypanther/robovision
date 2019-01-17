"""
Jetson gstreamer camera library. Generally, don't access this library directly.
Instead, use the video.py library.
"""
import cv2
import threading
import time
from .abstract_cam import AbstractCam


class Jetsoncam(AbstractCam):
    cameraString = ""

    def __init__(self, cam="usb", ip_address="", cam_num=0, resolution=(1920, 1080)):
        self.running = False
        self.current_frame = None
        w, h = resolution
        if cam == "usb":
            self.cameraString = self._get_usb_string(cam_num, resolution[0], resolution[1])
        elif cam == "onboard":
            self.cameraString = self._get_onboard_string(resolution[0], resolution[1])
        elif cam == "ip_camera":
            self.cameraString = self._get_rtsp_string(ip_address, resolution[0], resolution[1])
        if self.cameraString == "":
            raise IOError("Invalid camera type")

    def start(self):
        self.cam = cv2.VideoCapture(self.cameraString, cv2.CAP_GSTREAMER)
        self.ct = threading.Thread(target=self._capture_image_thread,
                                   name="Jetsoncam")
        self.ct.daemon = True
        self.running = True
        self.ct.start()

    def stop(self):
        self.running = False
        self.ct.join()
        self.stream.close()
        self.rawCapture.close()
        self.cam.close()

    def read_frame(self):
        if self.running is True:
            return self.current_frame

    def _capture_image_thread(self):
        while self.running is True:
            success, frame = self.cam.read()
            if success:
                self.current_frame = frame
            time.sleep(0.005)

    def _get_rtsp_string(uri, width, height, latency=0):
        return ("rtspsrc location={} latency={} ! rtph264depay ! h264parse ! omxh264dec ! "
                "nvvidconv ! video/x-raw, width=(int){}, height=(int){}, format=(string)BGRx ! "
                "videoconvert ! appsink").format(uri, latency, width, height)

    def _get_usb_string(dev, width, height):
        # We want to set width and height here, otherwise we could just do:
        #     return cv2.VideoCapture(dev)
        pipeline = ("v4l2src device=/dev/video{} ! video/x-raw,width=(int){},height=(int){},"
                    "format=I420, framerate = 30/1  !  videoconvert ! video/x-raw,width=(int){}, "
                    "height=(int){},format=BGR ! appsink")
        return (pipeline).format(dev, width, height, width, height)

    def _get_onboard_string(width, height):
        # On versions of L4T previous to L4T 28.1, flip-method=2
        # Use Jetson onboard camera
        return ("nvcamerasrc ! video/x-raw(memory:NVMM), "
                "width=(int)2592, height=(int)1458, format=(string)I420, framerate=(fraction)30/1 ! "
                "nvvidconv ! video/x-raw, width=(int){}, height=(int){}, format=(string)BGRx ! "
                "videoconvert ! appsink").format(width, height)
