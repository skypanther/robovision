"""
Determine the camera's apparent field of view.
"""
import argparse
import cv2
import numpy as np
import os
import sys
import textwrap

# If you've `git cloned` the repo and are running the examples locally
# you'll need the next line so that Python can find the robovision library
# Otherwise, comment out the sys.path... line
sys.path.append(os.path.dirname(os.path.realpath('.')))
import robovision as rv  # noqa: E402

leftpoint = None
rightpoint = None
fov = 0
distance = 36


def main():
    global fov
    ap = argparse.ArgumentParser(epilog=textwrap.dedent("""\
        Determine the camera's apparent field of view. 

        The input param can be any of the following:
        Integer       - Webcam with 0 typically the built-in webcam
        'picam'       - Raspberry Pi camera
        'http://...'  - URL to an IP cam, e.g. http://192.168.1.19/mjpg/video.mjpg

        Examples:
        python3 get_apparent_fov.py -s 0
        python3 get_apparent_fov.py -s picam
        python3 get_apparent_fov.py -s http://192.168.1.19/mjpg/video.mjpg
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter
        )  # noqa: E124
    ap.add_argument("-s", "--source", required=False,
                    help="Video input source, e.g. the webcam number")
    args = vars(ap.parse_args())
    source = args["source"]
    vs = None
    try:
        webcam = int(source)
        vs = rv.VideoStream(source="webcam", cam_id=webcam)
    except ValueError:
        if source == "picam":
            vs = rv.VideoStream(source="picam")
        else:
            vs = rv.VideoStream(source="ipcam", ipcam_url=source)
    if source is None:
        print("Invalid source")
        exit()

    fov_input = input("What is your camera's FOV in DEGREES? ")
    try:
        fov = float(fov_input)
    except ValueError:
        print("Invalid FOV, must be a number")
        exit()

    vs.start()
    cv2.namedWindow('CapturedImage', cv2.WINDOW_NORMAL)
    while True:
        frame = vs.read_frame()
        cv2.imshow("CapturedImage", frame)
        cv2.setMouseCallback("CapturedImage", click_handler, frame)
        # wait for Esc or q key and then exit
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord("q"):
            cv2.destroyAllWindows()
            vs.stop()
            break


def click_handler(event, x, y, _, image):
    """
    Callback function, called by OpenCV when the user interacts
    with the window using the mouse. This function will be called
    repeatedly as the user interacts.
    """
    # get access to a couple of global variables we'll need
    global leftpoint, rightpoint
    if event == cv2.EVENT_LBUTTONDOWN:
        # user has clicked the mouse's left button
        if leftpoint is None:
            leftpoint = (x, y)
        else:
            rightpoint = (x, y)
            clone = image.copy()
            cv2.line(clone, leftpoint, rightpoint, (0, 255, 0), 2)
            cv2.imshow("Measured distance", clone)
            do_calculations()


def do_calculations():
    global leftpoint, rightpoint
    print(leftpoint, rightpoint)


if __name__ == "__main__":
    main()
