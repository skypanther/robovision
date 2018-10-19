import cv2
import pickle


class ImageTools(object):
    '''
    Image adjustment and manipulation tools

    Example use:
        from imagetools import *
        image_tools = ImageTools('camera_params.pickle')
        image = cv2.imread('bot_picture.jpg')
        flattened = image_tools.flatten(image)
    '''
    camera_params = None
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    def __init__(self, camera_params=None):
        if camera_params is not None:
            self.set_camera_params(camera_params)

    def set_camera_params(self, camera_params):
        '''
        Caches the camera parameters (determined by auto_calibrate.py) in
        the instance for use for flatten() operations

        :param camera_params: pickle file created by auto_calibrate.py
        '''
        params = pickle.load(open(camera_params, "rb"))
        if isinstance(params, Object) and hasattr(params, 'mtx'):
            # looks to be a valid camera parameters pickle file
            self.camera_params = params

    def flatten(self, image):
        '''
        Removes lens distortions using the camera/lens parameters cached
        in the instanc

        :param image: OpenCV BGR image to flatten
        :return: Undistorted BGR image
        '''
        h, w = image.shape[:2]
        newcameramtx, roi = \
            cv2.getOptimalNewCameraMatrix(self.camera_params.mtx,
                                          self.camera_params.dist,
                                          (w, h),
                                          1,
                                          (w, h))
        return cv2.undistort(image,
                             self.camera_params.mtx,
                             self.camera_params.dist,
                             None,
                             newcameramtx)

    def equalize_lab(self, image):
        '''
        Image equalization function which is useful for adjusting contrast
        prior to other image processing operations. This function uses the
        Clahe image equalizition on the L channel of the LAB representation
        of the image. See the following link for more info
        https://docs.opencv.org/3.4.2/d5/daf/tutorial_py_histogram_equalization.html

        :param image: BGR image to equalize
        :return: Contrast adjusted / equalized image
        '''
        image_lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        lab_planes = cv2.split(image_lab)
        lab_planes[0] = self.clahe.apply(lab_planes[0])
        image_lab = cv2.merge(lab_planes)
        return cv2.cvtColor(image_lab, cv2.COLOR_LAB2BGR)

    def equalize_yuv(self, image):
        '''
        Image equalization function which is useful for adjusting contrast
        prior to other image processing operations. This function uses the
        Clahe image equalizition on the V channel of the YUV representation
        of the image. See the following link for more info
        https://docs.opencv.org/3.4.2/d5/daf/tutorial_py_histogram_equalization.html

        :param image: BGR image to equalize
        :return: Contrast adjusted / equalized image
        '''
        image_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        image_yuv[:, :, 0] = self.clahe.apply(image_yuv[:, :, 0])
        return cv2.cvtColor(image_yuv, cv2.COLOR_YUV2BGR)

    @staticmethod
    def adjust_contrast(image, contrast=64., brightness=0.):
        '''
        Adjust the brightness and contrast of an image by adding a weighted
        value to its pixels

        :param image: BGR image to adjust
        :param contrast: A float value, default 64.0
        :param brightness: A float value, default 0.0 (i.e. don't increase the
        brightness)
        :return: Contrast-adjusted image
        '''
        return cv2.addWeighted(image,
                               1. + float(contrast) / 127.,
                               image, 0,
                               float(brightness) - float(contrast))

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


class Object(object):
    """
    Generic / ad-hoc object constructor required for de-pickling
    the camera parameters
    """
    pass
