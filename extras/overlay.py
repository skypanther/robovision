"""
Show overlays atop streaming video

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
        exit("Invalid source")
    vs.start()
    cv2.namedWindow("Video With Overlay")
    while True:
        image = vs.read_frame()
        # Add a red border
        image = rv.draw_border(image, (0, 0, 255), thickness=20)
        # draw a blue border pointing left
        image = rv.draw_arrow(image, (255, 0, 0), direction=270, thickness=40)
        # draw green text, centered on screen
        image = rv.draw_text(image, (0, 255, 0), text="Raider Robotics")
        # draw a white crosshair centered on screen
        image = rv.draw_crosshairs(image, (255, 255, 255))
        cv2.imshow("Video With Overlay", rv.resize(image, height=480))
        key = cv2.waitKey(10) & 0xFF
        if key == 27 or key == ord("q"):
            cv2.destroyAllWindows()
            exit()


def print_help():
    print(textwrap.dedent('''\
        Show overlays atop a video stream

        Arguments:
            -s SOURCE, --source SOURCE

        The source param can be any of the following:
        Integer       - Webcam with 0 typically the built-in webcam
        'picam'       - Raspberry Pi camera
        'http://...'  - URL to an IP cam, e.g. http://10.15.18.100/mjpg/video.mjpg

        Examples:
        python3 overlay.py -s 0
        python3 overlay.py -s picam
        python3 overlay.py -s http://10.15.18.100/mjpg/video.mjpg

        '''))


if __name__ == "__main__":
    main()
