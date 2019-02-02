"""
Convenience utility functions

Author: Tim Poulsen
Web site: https://timpoulsen.com
Copyright 2018, Tim Poulsen, all rights reserved
License: MIT

TODO: Add color extraction functions: average, dominant, top-five, etc colors
"""
import cv2
import pickle
import robovision as rv

clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))


def get_video_stream(source):
    vs = None
    try:
        webcam = int(source)
        vs = rv.VideoStream(source="webcam", cam_id=webcam)
    except ValueError:
        if source == "picam":
            vs = rv.VideoStream(source="picam")
        elif type(source) is str and source.startswith("http"):
            vs = rv.VideoStream(source="ipcam", ipcam_url=source)
    return vs


def resize(image, width=None, height=None):
    """
    Resize an image while maintaining its aspect ratio; specify either
    target width or height of the image (with width taking precedence).

    :param image: OpenCV BGR image
    :param width: Integer new width of the image
    :param height: Integer new height of the image
    :return: Resized BGR image
    """
    dim = None
    h, w = image.shape[:2]
    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))
    return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)


def resize_raw(image, width=None, height=None):
    """
    Resize an image ignoring aspect ratio; specifying either a target
    width or height (width takes precedence). Results in a square image
    that may look "squished" in one direction. Most useful for machine
    learning algorithms rather than display to a user.

    :param image: OpenCV BGR image
    :param width: Integer new width of the image
    :param height: Integer new height of the image
    :return: Resized BGR image
    """
    dim = None
    if width is None and height is None:
        return image
    if width is None:
        dim = (height, height)
    elif height is None:
        dim = (width, width)
    else:
        dim = (height, width)
    return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)


def adjust_brightness_contrast(image, brightness=0., contrast=0.):
    """
    Adjust the brightness and/or contrast of an image

    :param image: OpenCV BGR image
    :param contrast: Float, contrast adjustment with 0 meaning no change
    :param brightness: Float, brightness adjustment with 0 meaning no change
    """
    beta = 0
    # See the OpenCV docs for more info on the `beta` parameter to addWeighted
    # https://docs.opencv.org/3.4.2/d2/de8/group__core__array.html#gafafb2513349db3bcff51f54ee5592a19
    return cv2.addWeighted(image,
                           1 + float(contrast) / 100.,
                           image,
                           beta,
                           float(brightness))


def adjust_brightness(image, brightness=0.):
    """
    Adjust the brightness of an image

    :param image: OpenCV BGR image
    :param brightness: Float value where positive increases image brightness
    :return: Adjusted BGR image
    """
    return adjust_brightness_contrast(image, brightness=brightness, contrast=0.)


def adjust_contrast(image, contrast=0.):
    """
    Adjust the contrast of an image

    :param image: OpenCV BGR image
    :param contrast: Float value where positive increases image contrast
    :return: Adjusted BGR image
    """
    return adjust_brightness_contrast(image, brightness=0., contrast=contrast)


def equalize(image):
    """
    Image equalization function of the lAB representation of the image.

    :param image: OpenCV BGR image
    :return: Equalized BGR image
    """
    image_lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    lab_planes = cv2.split(image_lab)
    lab_planes[0] = clahe.apply(lab_planes[0])
    image_lab = cv2.merge(lab_planes)
    return cv2.cvtColor(image_lab, cv2.COLOR_LAB2BGR)


def detect_edges(image,
                 min_val=0,
                 max_val=100,
                 aperture_size=100,
                 blur_matrix=(3, 3)):
    '''
    Create an edge-detected version of an image. See the following for further
    explanation and a way to tune the input values
    https://www.timpoulsen.com/2018/getting-user-input-with-opencv-trackbars.html
    :param image: Source image in which to detect edges
    :param min_val: Minimum threshold value
    :param max_val: Maximum threshold value
    :param aperture_size: Sobel filter aperture size
    :blur_matrix: Tuple used for GuassianBlur matrix
    :return: Edge-detected image
    '''
    image = cv2.GaussianBlur(image, blur_matrix, 0)
    return cv2.Canny(image, min_val, max_val, aperture_size)


def load_camera_params(params_file):
    '''
    Loads the camera parameters (determined by auto_calibrate.py) in
    the instance for use for flatten() operations

    :param params_file: pickle file created by auto_calibrate.py
    '''
    params = pickle.load(open(params_file, "rb"))
    if isinstance(params, Object) and hasattr(params, 'mtx'):
        # looks to be a valid camera parameters pickle file
        return params
    return None


def flatten(image, cam_matrix, dist_coeff):
    '''
    Removes lens distortions using the camera/lens parameters and
    distortion coefficients

    :param image: OpenCV BGR image to flatten
    :return: Undistorted BGR image
    '''
    h, w = image.shape[:2]
    newcameramtx, _ = \
        cv2.getOptimalNewCameraMatrix(cam_matrix,
                                      dist_coeff,
                                      (w, h),
                                      1,
                                      (w, h))
    return cv2.undistort(image,
                         cam_matrix,
                         dist_coeff,
                         None,
                         newcameramtx)


class Object(object):
    """
    An empty, generic object constructor required for de-pickling
    the camera parameters file
    """
    pass
