"""
Distance finder script

Author: Tim Poulsen
Web site: https://timpoulsen.com
Copyright 2019, Tim Poulsen, all rights reserved
License: MIT
"""
import argparse
import cv2
import numpy as np
import os
import pickle
import sys
import textwrap
# If you've `git cloned` the repo and are running the examples locally
# you'll need the next line so that Python can find the robovision library
# Otherwise, comment out the sys.path... line
sys.path.append(os.path.dirname(os.path.realpath('.')))
import robovision as rv  # noqa: E402

# The Axis 206 IP cam commonly used by FRC teams has these characteristics:
# Lens: 4.0 mm, F2.0 fixed iris
# Horizontal angle of view: 54°
# Sensitivity: 4 – 10000 lux, F2.0
# Shutter speed: 1/10000 s to 1/2 s
# from https://www.axis.com/files/datasheet/ds_206_33168_en_0904_lo.pdf
cam_matrix = None
dist_coeff = None
barrel_params = {
    "k1": 0.0,
    "k2": 0.0,
    "p1": 0.0,
    "p2": 0.0,
    "fl": 2.,
    "center_x": 0.0,
    "center_y": 0.0
}
"""
distortion coefficients = k1, k2, p1, p2
Camera matrix is a 3x3 matrix:

 fx   0  cx
  0  fy  cy
  0   0   1
"""


def main():
    global barrel_params
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
    cv2.namedWindow("Original")
    cv2.namedWindow("De-warped")
    cv2.createTrackbar("K1", "Original", 100, 800, k1_change)
    cv2.createTrackbar("K2", "Original", 100, 800, k2_change)
    cv2.createTrackbar("P1", "Original", 100, 800, p1_change)
    cv2.createTrackbar("P2", "Original", 100, 800, p2_change)
    cv2.createTrackbar("FL", "Original", 1, 200, fl_change)

    while True:
        image = vs.read_frame()
        cv2.imshow("Original", rv.resize(image, height=480))
        height, width = image.shape[:2]
        barrel_params["center_x"] = width / 2.0    # center x
        barrel_params["center_y"] = height / 2.0    # center y
        de_barrel(image)
        key = cv2.waitKey(10) & 0xFF
        if key == 27 or key == ord("q"):
            cv2.destroyAllWindows()
            exit()
        if key == ord("p"):
            # print the params as text for copying into a script
            print_camera_params(cam_matrix, dist_coeff)
            cv2.destroyAllWindows()
            exit()
        if key == ord("s"):
            # Save the params to a pickle file
            camera_params = Object()
            camera_params.mtx = cam_matrix
            camera_params.dist = dist_coeff
            camera_params.img_size = (width, height)
            param_file_name = os.path.join(os.path.expanduser("~"), "params.pickle")
            with open(param_file_name, "wb") as param_file:
                pickle.dump(camera_params, param_file)
                print("Camera params saved to {}".format(param_file_name))
            cv2.destroyAllWindows()
            exit()


def k1_change(new_val):
    new_val = new_val - 100
    change_params("k1", new_val * 1.0e-6)


def k2_change(new_val):
    new_val = new_val - 100
    change_params("k2", new_val * 1.0e-10)


def p1_change(new_val):
    new_val = new_val - 100
    change_params("p1", new_val * 1.0e-5)


def p2_change(new_val):
    new_val = new_val - 100
    change_params("p2", new_val * 1.0e-6)


def fl_change(new_val):
    change_params("fl", new_val)


def change_params(name, value):
    global barrel_params
    barrel_params[name] = value
    print(barrel_params)


def de_barrel(image):
    global dist_coeff, cam_matrix

    dist_coeff = np.zeros((4, 1), np.float64)
    dist_coeff[0, 0] = barrel_params["k1"]
    dist_coeff[1, 0] = barrel_params["k2"]
    dist_coeff[2, 0] = barrel_params["p1"]
    dist_coeff[3, 0] = barrel_params["p2"]

    cam_matrix = np.eye(3, dtype=np.float32)
    cam_matrix[0, 2] = barrel_params["center_x"]
    cam_matrix[1, 2] = barrel_params["center_y"]
    cam_matrix[0, 0] = barrel_params["fl"]   # define focal length x
    cam_matrix[1, 1] = barrel_params["fl"]   # define focal length y

    dewarped = cv2.undistort(image, cam_matrix, dist_coeff)
    cv2.imshow("De-warped", rv.resize(dewarped, height=480))


def print_camera_params(mtx, dist):
    print("Copy and paste this code into your file:\n")
    print("dist_coeff = np.zeros((4, 1), np.float64)")
    print("dist_coeff[0, 0] = {}".format(dist[0, 0]))
    print("dist_coeff[1, 0] = {}".format(dist[1, 0]))
    print("dist_coeff[2, 0] = {}".format(dist[2, 0]))
    print("dist_coeff[3, 0] = {}".format(dist[3, 0]))
    print(" ")
    print("cam_matrix = np.eye(3, dtype=np.float32)")
    print("cam_matrix[0, 2] = {}".format(mtx[0, 2]))
    print("cam_matrix[1, 2] = {}".format(mtx[1, 2]))
    print("cam_matrix[1, 2] = {}".format(mtx[1, 2]))
    print("cam_matrix[1, 1] = {}".format(mtx[1, 1]))
    print(" ")
    print("Then, call flatten with:")
    print("frame = video_stream.read_frame()")
    print("frame = robovision.flatten(frame, cam_matrix, dist_coeff)\n")


def print_help():
    print(textwrap.dedent('''\
        Calculate lens characteristics manually

        Arguments:
            -s SOURCE, --source SOURCE

        The source param can be any of the following:
        Integer       - Webcam with 0 typically the built-in webcam
        'picam'       - Raspberry Pi camera
        'http://...'  - URL to an IP cam, e.g. http://10.15.18.100/mjpg/video.mjpg

        Examples:
        python3 manual_lens_calibration.py -s 0
        python3 manual_lens_calibration.py -s picam
        python3 manual_lens_calibration.py -s http://10.15.18.100/mjpg/video.mjpg

        Use this script to determine lens characteristics for removing distortions
        when the auto_calibrate script fails to properly detect those parameters.

        When you're satisfied with the dewarping, press "S" while one of the preview
        windows is active to save your lens parameters to a pickle file.

        Or, press "P" to print the lens parameters as code you can copy and paste
        into your script.
        '''))


class Object(object):
    """
    Generic / ad-hoc object constructor
    """
    pass


if __name__ == "__main__":
    main()
