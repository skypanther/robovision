"""
Distance calibration script

Author: Tim Poulsen
Web site: https://timpoulsen.com
Copyright 2019, Tim Poulsen, all rights reserved
License: MIT
"""
import argparse
import cv2
import os
import sys
import textwrap

# If you've `git cloned` the repo and are running the examples locally
# you'll need the next line so that Python can find the robovision library
# Otherwise, comment out the sys.path... line
sys.path.append(os.path.dirname(os.path.realpath('.')))
import robovision as rv  # noqa: E402

coords = []
drawing = False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--source", required=False,
                    help="Video source, e.g. the webcam number")
    args = vars(ap.parse_args())
    if args["source"] is None or args["source"] == "":
        print_help()
        exit()
    vs = rv.get_video_stream(args["source"])
    if vs is None:
        print("Invalid source")
        exit()
    vs.start()
    # params = rv.load_camera_params('params.pickle')
    cv2.namedWindow('CapturedImage', cv2.WINDOW_NORMAL)
    while True:
        frame = vs.read_frame()
        # frame = rv.flatten(frame, params)
        cv2.imshow('CapturedImage', frame)
        cv2.setMouseCallback('CapturedImage', click_and_measure, frame)
        # wait for Esc or q key and then exit
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord("q"):
            cv2.destroyAllWindows()
            vs.stop()
            break


def click_and_measure(event, x, y, flag, image):
    """
    Callback function, called by OpenCV when the user interacts
    with the window using the mouse. This function will be called
    repeatedly as the user interacts.
    """
    # get access to a couple of global variables we'll need
    global coords, drawing
    if event == cv2.EVENT_LBUTTONDOWN:
        # user has clicked the mouse's left button
        drawing = True
        # save those starting coordinates
        coords = [(x, y)]
    elif event == cv2.EVENT_MOUSEMOVE:
        # user is moving the mouse within the window
        if drawing is True:
            # if we're in drawing mode, we'll draw a green rectangle
            # from the starting x,y coords to our current coords
            clone = image.copy()
            cv2.rectangle(clone, coords[0], (x, y), (0, 255, 0), 2)
            cv2.imshow('CapturedImage', clone)
    elif event == cv2.EVENT_LBUTTONUP:
        # user has released the mouse button, leave drawing mode
        # and crop the photo
        drawing = False
        # save our ending coordinates
        coords.append((x, y))
        if len(coords) == 2:
            # calculate the four corners of our region of interest
            ty, by, tx, bx = coords[0][1], coords[1][1], coords[0][0], coords[1][0]
            # crop the image using array slicing
            roi = image[ty:by, tx:bx]
            height, width = roi.shape[:2]
            if width > 0 and height > 0:
                # make sure roi has height/width to prevent imshow error
                # and show the cropped image in a new window
                print("Height: {}".format(height))
                print("Width: {}".format(width))
                f = width * 36 / 12
                print("Assuming a 12-inch script at 36 inches from your camera,"
                      "your camera's apparent focal length is {}".format(f))


def print_help():
    print(textwrap.dedent('''\
        Calibrate distance measurements to your camera

        Arguments:
            -s SOURCE, --source SOURCE

        The source param can be any of the following:
        Integer       - Webcam with 0 typically the built-in webcam
        'picam'       - Raspberry Pi camera
        'http://...'  - URL to an IP cam, e.g. http://10.15.18.100/mjpg/video.mjpg

        Examples:
        python3 distance_calibration.py -s 0
        python3 distance_calibration.py -s picam
        python3 distance_calibration.py -s http://10.15.18.100/mjpg/video.mjpg

        Place a 12" strip of retroreflective tape at a known distance (for example,
        3 feet) from your camera. Run this script. Drag to select the area in the
        preview window where the tape is shown. The height and width of the selected
        area in pixels will be output. Repeat a few times, average the results and
        plug them into the following formula to get your camera's apparent focal length.

        F = (P x  D) / W

        Where P is the width in pixels, D is the distance, and W is the actual
        width.
        '''))


if __name__ == "__main__":
    main()
