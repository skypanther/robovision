"""
Line finder and interrogator script

Author: Tim Poulsen
Web site: https://timpoulsen.com
Copyright 2019, Tim Poulsen, all rights reserved
License: MIT
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
sys.path.append(os.path.dirname(os.path.realpath(".")))
import robovision as rv  # noqa: E402

TARGET_ASPECT_RATIO_MIN = 3
TARGET_ASPECT_RATIO_MAX = 5


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
    cv2.namedWindow("CapturedImage", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Thresholded", cv2.WINDOW_NORMAL)
    target = rv.Target()
    target.set_color_range(lower=(0, 0, 255), upper=(0, 0, 255))
    # params = rv.load_camera_params("params.pickle")
    while True:
        frame = vs.read_frame()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        # frame = rv.flatten(frame, params)
        contours = target.get_contours(thresh)
        if len(contours) > 0:
            for i, cnt in enumerate(contours):
                area = cv2.contourArea(cnt)
                if area > 4000:
                    hull = cv2.convexHull(cnt)
                    hullArea = cv2.contourArea(hull)
                    solidity = area / float(hullArea)
                    if solidity < 0.75:
                        print("solidity: {}".format(solidity))
                        continue
                    rrect = target.get_rotated_rectangle(for_contour=cnt)
                    height, width = rrect[1]
                    angle = rrect[2]
                    if width < height:
                        angle += 90
                    if abs(angle) > 60:
                        continue
                    print(angle)
                    boxpoints = cv2.boxPoints(rrect)
                    boxpoints = np.int0(boxpoints)
                    if i % 2 == 0:
                        cv2.drawContours(frame, [boxpoints], 0, (0, 255, 0), 3)
                    else:
                        cv2.drawContours(frame, [boxpoints], 0, (255, 0, 0), 3)
        cv2.imshow("CapturedImage", frame)
        cv2.imshow("Thresholded", thresh)
        # wait for Esc or q key and then exit
        key = cv2.waitKey(100) & 0xFF
        if key == 27 or key == ord("q"):
            cv2.destroyAllWindows()
            vs.stop()
            break


def print_help():
    print(textwrap.dedent("""\
        Calculate the distance to a target

        Arguments:
            -s SOURCE, --source SOURCE
            -f FOCALLENGTH, --focallength FOCALLENGTH

        The source param can be any of the following:
        Integer       - Webcam with 0 typically the built-in webcam
        "picam"       - Raspberry Pi camera
        "http://..."  - URL to an IP cam, e.g. http://10.15.18.100/mjpg/video.mjpg

        Examples:
        python3 distance_finder.py -s 0 -f 550
        python3 distance_finder.py -s picam  -f 550
        python3 distance_finder.py -s http://10.15.18.100/mjpg/video.mjpg  -f 550

        After calibrating using distance_calibration.py, use this script to find
        the distance to the 12" strip of retroreflective tape. For example, move
        it to an arbitrary distance between roughly a few inches to ten feet, then
        run this script to calculate its distance from your camera.
        """))


if __name__ == "__main__":
    main()
