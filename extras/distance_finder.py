"""
Distance finder script

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

lower = 60
upper = 100


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--source", required=False,
                    help="Video source, e.g. the webcam number")
    ap.add_argument("-f", "--FOCALLENGTH", required=False,
                    help="Calculated apparent focal length of your camera")
    args = vars(ap.parse_args())
    if args["source"] is None or args["source"] == "":
        print_help()
        exit()
    vs = rv.get_video_stream(args["source"])
    if vs is None:
        print("Invalid source")
        exit()
    fl = float(args["FOCALLENGTH"])
    vs.start()
    cv2.namedWindow('CapturedImage', cv2.WINDOW_NORMAL)
    target = rv.Target()
    # params = rv.load_camera_params('params.pickle')
    while True:
        frame = vs.read_frame()
        # frame = rv.flatten(frame, params)
        target.set_color_range(lower=(lower, 100, 100), upper=(upper, 255, 255))
        contours = target.get_contours(frame)
        if len(contours) > 0:
            cv2.drawContours(frame, contours, 0, (0, 0, 255), 3)
            _, _, w, _ = target.get_rectangle(for_contour=contours[0])
            # Distance from formula: D’ = (W x F) / P
            d = 12 * fl / w
            print("Assuming you're using a 12-inch retroreflective tape, the distance is {} inches".format(d))
        cv2.imshow('CapturedImage', frame)
        # wait for Esc or q key and then exit
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord("q"):
            cv2.destroyAllWindows()
            vs.stop()
            break


def set_lower(val):
    global lower
    lower = int(val)


def set_upper(val):
    global upper
    upper = int(val)


def print_help():
    print(textwrap.dedent('''\
        Calculate the distance to a target

        Arguments:
            -s SOURCE, --source SOURCE
            -f FOCALLENGTH, --focallength FOCALLENGTH

        The source param can be any of the following:
        Integer       - Webcam with 0 typically the built-in webcam
        'picam'       - Raspberry Pi camera
        'http://...'  - URL to an IP cam, e.g. http://10.15.18.100/mjpg/video.mjpg

        Examples:
        python3 distance_finder.py -s 0 -f 550
        python3 distance_finder.py -s picam  -f 550
        python3 distance_finder.py -s http://10.15.18.100/mjpg/video.mjpg  -f 550

        After calibrating using distance_calibration.py, use this script to find
        the distance to the 12" strip of retroreflective tape. For example, move
        it to an arbitrary distance between roughly a few inches to ten feet, then
        run this script to calculate its distance from your camera.
        '''))


if __name__ == "__main__":
    main()
