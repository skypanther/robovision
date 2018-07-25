"""
Auto-calibrate: Camera calibration utility

Take a still image every X seconds
Divide the resulting images into Y “buckets"
From each of the buckets, select Z images
Use that set of stills to calculate camera parameters
Save the intrinsic camera properties (pickled object?) for later use in undistortion operations

Params:
X = interval, default 2
Y = subsets, default 3
Z = images per subset, default 5
O = output dir for calibration images and pickled props, default './auto_calibrate/*'


"""

import argparse
import numpy as np
import cv2
import glob
import os
import pickle
from time import sleep

cam = None
subset_messages = [
    'the LEFT third of the field of view',
    'the CENTER third of the field of view',
    'the RIGHT third of the field of view',
    'ANOTHER section of the field of view'
]
# Count of INNER CORNERS of target grid
checkerboard_rows = 6
checkerboard_colummns = 9


def main():
    global cam
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--interval', default=3,
                    help='Interval in seconds between image captures')
    ap.add_argument('-s', '--subsets', default=3,
                    help='Subsets (divisions) of the captured images')
    ap.add_argument('-n', '--num', default=5,
                    help='Number of images per subset to use in calibration')
    ap.add_argument('-o', '--output', default='auto_calibrate',
                    help='Path to output folder')
    ap.add_argument('-c', '--camera', default='default',
                    help='Camera source, default is built-in webcam')
    ap.add_argument('-p', '--preview', default=True,
                    help='Dewarp test image and display a preview')
    args = vars(ap.parse_args())
    output_dir = get_output_dir(args['output'])
    source = 0 if args['camera'] is 'default' else args['camera']
    cam = cv2.VideoCapture(source)
    countdown()
    for i in range(args['subsets']):
        show_subset_message(i)
        for n in range(args['num']):
            take_photo(source, output_dir, i, n)
            sleep(args['interval'])
    print('Done capturing. Beginning calibration...')
    calibrate(output_dir, args['preview'])


class Object(object):
    """
    Generic / ad-hoc object constructor
    """
    pass


def show_subset_message(subset_index):
    if subset_index >= len(subset_messages):
        subset_index = 3
    print(f'MOVE the target to {subset_messages[subset_index]}')
    sleep(1)


def countdown():
    print('Taking a picture in:')
    print('3')
    sleep(1)
    print('2')
    sleep(1)
    print('1')
    sleep(1)


def take_photo(source, dirname, subset, image_num):
    # TODO: handle source other than 0/webcam
    global cam
    image_captured, image = cam.read()
    if (image_captured):
        fname = os.path.join(dirname, f'image_{subset}_{image_num}') + '.jpg'
        cv2.imwrite(fname, image)
        print(f'Photo saved to {dirname}/image_{subset}_{image_num}')
        print('Move the target to a new location & orientation')


def get_output_dir(dirname):
    full_path = ''
    if dirname[0:1] == '/':
        # looks like an absolute path already
        full_path = dirname
    elif dirname[0:1] == '~':
        # relative directory name
        full_path = os.path.expanduser(dirname)
    else:
        # just a bare name
        full_path = os.path.join(os.path.realpath('.'), dirname)

    if os.path.isdir(full_path) is True:
        print('Output directory already exists. Please use a different directory.')
        exit(1)
    os.mkdir(full_path)
    return full_path


def calibrate(dirname, preview):
    """
    Determine camera calibration parameters
    Based on https://docs.opencv.org/3.1.0/dc/dbb/tutorial_py_calibration.html

    :param dirname: Full path to location of calibration images
    """
    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((checkerboard_rows * checkerboard_colummns, 3), np.float32)
    objp[:, :2] = np.mgrid[0:checkerboard_colummns, 0:checkerboard_rows].T.reshape(-1, 2)

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.

    images = glob.glob(f'{dirname}/*.jpg')

    for absolute_filename in images:
        img = cv2.imread(absolute_filename)
        fname = absolute_filename.split(os.path.sep)[-1]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (checkerboard_colummns, checkerboard_rows), None)
        print(f'Found checkboard in {fname} -> {ret}')

        # If found, add object points, image points (after refining them)
        if ret is True:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

    if not objpoints:
        print('Target not detected in any of the photos')
        exit()

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    # print(ret, mtx, dist, rvecs, tvecs)

    img = cv2.imread(os.path.join(dirname, 'image_0_0.jpg'))
    cv2.imshow('Original', img)
    h, w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

    # undistort
    dst_one = cv2.undistort(img, mtx, dist, None, newcameramtx)
    cv2.imshow('Remapped Image', dst_one)

    total_error = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
        total_error += error

    mean_accuracy = 100 - (100 * (total_error / len(objpoints)))
    print(f'Mean accuracy: {mean_accuracy}')

    # Save the params for future re-use
    camera_params = Object()
    camera_params.mtx = mtx
    camera_params.dist = dist
    camera_params.img_size = (w, h)
    camera_params.newcameramtx = newcameramtx
    camera_params.mean_accuracy = mean_accuracy

    param_file_name = os.path.join(dirname, 'params.pickle')
    with open(param_file_name,'wb') as param_file:
        pickle.dump(camera_params, param_file)
        print(f'Camera params saved to {param_file_name}')


if __name__ == '__main__':
    main()
