"""
Example of multiprocessing (parallel processing)

CamGrabber runs on one core
FrameProcessor runs on another
__main__ runs on a third core

This example intends to show how you could run multiple vision processing
routines across the cores of a modern, multi-core CPU. For example, one
process could run a targeting routine, while another streams a camera feed
(possibly with a target indicator or some other overlay superimposed) back
to the DriverStation. Typically, you'd need subprocesses to monitor the FMSInfo
NetworkTable for a signal from the FMS that the game has started or ended to
control the other subprocesses.
"""
import cv2
import imutils
import time
from multiprocessing import Process, Queue


class CamGrabber(Process):
    def __init__(self, queue=None, stop_queue=None, **kwargs):
        super(CamGrabber, self).__init__()
        self.queue = queue
        self.stop_queue = stop_queue
        self.kwargs = kwargs

    def run(self):
        cam = cv2.VideoCapture(0)
        keepGoing = True
        while keepGoing:
            success, frame = cam.read()
            if success:
                frame = imutils.resize(frame, width=320)
                self.queue.put(frame)
            else:
                print("frame fail {}".format(success))
            if self.stop_queue.empty() is False:
                stop = self.stop_queue.get()
                if stop == 1:
                    print("CamGrabber exiting")
                    cam.release()
                    keepGoing = False
                    break


class FrameProcessor(Process):
    def __init__(self, queue=None, stop_queue=None, **kwargs):
        super(FrameProcessor, self).__init__()
        self.queue = queue
        self.stop_queue = stop_queue
        self.kwargs = kwargs

    def run(self):
        keepGoing = True
        while keepGoing:
            if self.queue.empty() is False:
                f = self.queue.get()
                if f is not None:
                    adjusted = cv2.addWeighted(f,
                                               1. + float(40) / 127.,
                                               f,
                                               float(1),
                                               float(60) - float(40))

                    cv2.imshow("Adjusted", adjusted)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("FrameProcessor exiting")
                self.stop_queue.put(1)
                cv2.destroyAllWindows()
                keepGoing = False
                break


if __name__ == "__main__":
    q = Queue()
    cg_stop_queue = Queue()
    stop_queue = Queue()
    cg = CamGrabber(queue=q, stop_queue=cg_stop_queue)
    fp = FrameProcessor(queue=q, stop_queue=stop_queue)
    cg.start()
    fp.start()
    while True:
        if stop_queue.empty() is False:
            stop = stop_queue.get()
            if stop == 1:
                print("Signaling CamGrabber to exit")
                cg.stop_queue.put(1)
                fp.terminate()
                time.sleep(2)
                cg.terminate()
                exit()
