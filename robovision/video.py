"""
Multi-threaded video frame acquisition - one thread continuously grabs frames
while the other pulls individual frames from a queue
"""
from .video.webcam import Webcam
from .video.picam import Picam
from .video.ipcam import IPcam
from .video.jetsoncam import Jetsoncam

valid_sources = 'webcam', 'ipcam', 'picam', 'jetson'


class VideoStream:
    def __init__(self, source='webcam', cam_id=0, resolution=(320, 240), ip_address=''):
        if source not in valid_sources:
            print('Valid sources are {}'.format(', '.join(valid_sources)))
            raise 'InvalidSource'
        if source == 'webcam':
            self.source = Webcam(cam_id=cam_id)
        if source == 'ipcam':
            self.source = IPcam(ip_address=ip_address)
        elif source == 'picam':
            self.source = Picam(resolution=resolution)
        else:
            self.source = Jetsoncam()

    def start(self):
        self.source.start()

    def stop(self):
        self.source.stop()

    def read_frame(self):
        return self.source.read_frame()
