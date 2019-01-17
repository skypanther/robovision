"""
Auto-calibrate: Camera calibration utility

1. Takes a still image every X seconds. Prompts you with a countdown between each.
2. From the resulting images, selects N images, checking each in turn that it shows
   the checkboard.
3. From that set of stills, it calculates camera parameters and saves them to a
   pickled object for later use in undistortion operations.
4. Optionally, shows a preview of unwarping a random calibration photo using the
   calculated lens parameters

Params:
i = interval between captures, default 3
t = total number of photos to capture, default 40
n = min number of checkerboard photos to process, default 15
o = output dir for calibration images and pickled props, default './auto_calibrate/*'
c = camera source, default is built-in webcam
p = Dewarp a test image and display a preview, default True
z = Skip image capture, just process previously captured calibration images, default False

"""

import argparse
import numpy as np
import cv2
import glob
import imutils
import os
import pickle
import random
from time import sleep

cam = None
messages = {
    'intro': 'Beginning image capture',
    'move': 'Move the checkerboard elsewhere in the field of view',
    'no_calibration': 'No valid calibration images found',
    'capture_done': 'Done capturing. Beginning calibration...'
}

# Count of INNER CORNERS of target grid
checkerboard_rows = 6
checkerboard_colummns = 9


def main():
    global cam
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--interval', default=3,
                    help='Interval in seconds between image captures')
    ap.add_argument('-t', '--total', default=40,
                    help='Total number of photos to capture')
    ap.add_argument('-n', '--num', default=5,
                    help='Number of images to use in calibration')
    ap.add_argument('-o', '--output', default='auto_calibrate',
                    help='Path to where captured images and results should be saved')
    ap.add_argument('-c', '--camera', default='default',
                    help='Camera source, default is built-in webcam')
    ap.add_argument('-p', '--preview', default=True, type=str2bool,
                    help='Dewarp test image and display a preview')
    ap.add_argument('-z', '--skip', default=False, type=str2bool,
                    help='Skip image capture, just calibrate from existing set')
    args = vars(ap.parse_args())
    num_images = int(args['num'])
    total = int(args['total'])
    output_dir = get_output_dir(args['output'], args['skip'])
    source = 0 if args['camera'] is 'default' else args['camera']
    if args['skip'] is False:
        cam = cv2.VideoCapture(source)
        countdown()
        show_message('intro')
        sleep(3)
        for i in range(total):
            take_photo(source, output_dir, i, total)
            show_message('move')
            sleep(args['interval'])
            clear_screen()
        show_message('capture_done')
    calibrate(output_dir, num_images, args['preview'])


class Object(object):
    """
    Generic / ad-hoc object constructor
    """
    pass


def show_message(key):
    # shows a message from the messages dict
    if key in messages:
        print(messages[key])
    sleep(1)


def countdown():
    clear_screen()
    print('Taking a picture in:')
    print('3... ')
    sleep(1)
    print('2... ')
    sleep(1)
    print('1')
    sleep(1)
    clear_screen()


def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')


def take_photo(source, dirname, image_num, total):
    # TODO: handle source other than 0/webcam
    global cam
    image_captured, image = cam.read()
    if (image_captured):
        fname = os.path.join(dirname, 'image_{}'.format(image_num)) + '.jpg'
        cv2.imwrite(fname, image)
        print('Captured image {} of {}'.format(image_num, total))


def get_output_dir(dirname, skip_image_capture):
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

    if skip_image_capture:
        return full_path

    if os.path.isdir(full_path) is True:
        print('Output directory already exists. Please use a different directory.')
        exit(1)
    os.mkdir(full_path)
    return full_path


def get_calibration_imageset(dirname, num_images):
    """
    Return num_images calibration images from dirname that show the checkerboard

    :@param dirname: Path to images
    :@param num_images: Num images to select
    :return: List of tuples of (image, corners)
    """
    images = glob.glob('{}/*.jpg'.format(dirname))
    selected_images = []
    iteration = 0
    max_iterations = num_images * 4
    while len(selected_images) < num_images:
        if iteration >= max_iterations:
            break
        iteration += 1
        candidate = random.choice(images)
        img = cv2.imread(candidate)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, (checkerboard_colummns, checkerboard_rows), None)
        if ret is True:
            selected_images.append((candidate, corners))
    return selected_images


def str2bool(v):
    """
    From https://stackoverflow.com/a/43357954/292947
    Converts the argparse true/false to actual booleans
    """
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def calibrate(dirname, min_images, preview):
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

    image_set = get_calibration_imageset(dirname, min_images)
    if len(image_set) == 0:
        show_message('no_calibration')
        exit()

    for calibration_set in image_set:
        # calibration_set is a tuple of (image, corners)
        img = cv2.imread(calibration_set[0])
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray, calibration_set[1], (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)

    if not objpoints:
        print('Target not detected in any of the photos')
        exit()

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    # print(ret, mtx, dist, rvecs, tvecs)

    h, w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

    if preview:
        # Show original and corrected image
        candidate = random.choice(image_set)
        img = cv2.imread(candidate[0])
        cv2.imshow('Original', imutils.resize(img, height=320))
        corrected = cv2.undistort(img, mtx, dist, None, newcameramtx)
        cv2.imshow('Remapped Image', imutils.resize(corrected, height=320))
        cv2.waitKey(0)

    total_error = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
        total_error += error

    mean_accuracy = 100 - (100 * (total_error / len(objpoints)))
    print('Mean accuracy: {}'.format(mean_accuracy))

    # Save the params for future re-use
    camera_params = Object()
    camera_params.mtx = mtx
    camera_params.dist = dist
    camera_params.img_size = (w, h)
    camera_params.newcameramtx = newcameramtx
    camera_params.mean_accuracy = mean_accuracy

    param_file_name = os.path.join(dirname, 'params.pickle')
    with open(param_file_name, 'wb') as param_file:
        pickle.dump(camera_params, param_file)
        print('Camera params saved to {}'.format(param_file_name))


if __name__ == '__main__':
    main()
