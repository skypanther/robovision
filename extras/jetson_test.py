"""
Script for viewing live camera output from a network (RTSP), USB, or onboard
camera with a Jetson board.
"""
import cv2


def main():
    cam = open_cam_usb(0, 1024, 768)
    # cam = open_cam_onboard(1024, 768)  # Use Jetson onboard camera
    if cam.isOpened() is False:
        print('failed to open camera')
        exit()
    while True:
        _, img = cam.read()
        cv2.imshow("frame", img)
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord("q"):
            cv2.destroyAllWindows()
            break


def open_cam_rtsp(uri, width, height, latency):
    gst_str = ("rtspsrc location={} latency={} ! rtph264depay ! h264parse ! omxh264dec ! "
               "nvvidconv ! video/x-raw, width=(int){}, height=(int){}, format=(string)BGRx ! "
               "videoconvert ! appsink").format(uri, latency, width, height)
    return cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)


def open_cam_usb_default(dev_number):
    return cv2.VideoCapture(dev_number)


def open_cam_usb(dev, width, height):
    # We want to set width and height here, otherwise we could just do:
    #     return cv2.VideoCapture(dev)
    pipeline = ("v4l2src device=/dev/video{} ! video/x-raw,width=(int){},height=(int){},"
                "format=I420, framerate = 30/1  !  videoconvert ! video/x-raw,width=(int){}, "
                "height=(int){},format=BGR ! appsink")
    gst_str = (pipeline).format(dev, width, height, width, height)
    return cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)


def open_cam_onboard(width, height):
    # On versions of L4T previous to L4T 28.1, flip-method=2
    # Use Jetson onboard camera
    gst_str = ("nvcamerasrc ! video/x-raw(memory:NVMM), "
               "width=(int)2592, height=(int)1458, format=(string)I420, framerate=(fraction)30/1 ! "
               "nvvidconv ! video/x-raw, width=(int){}, height=(int){}, format=(string)BGRx ! "
               "videoconvert ! appsink").format(width, height)
    return cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)


if __name__ == "__main__":
    main()