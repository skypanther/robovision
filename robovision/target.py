"""
Determine target characteristics

Author: Tim Poulsen
Web site: https://timpoulsen.com
Copyright 2018, Tim Poulsen, all rights reserved
License: MIT
"""
import cv2
import math
import numpy as np


class Target():
    def __init__(self):
        self.kernelOpen = np.ones((5, 5))  # for drawing the "open" mask
        self.kernelClose = np.ones((20, 20))  # for draing the "closed" mask

    def set_color_range(self, lower=(100, 100, 100), upper=(255, 255, 255)):
        self.lower = lower
        self.upper = upper

    def get_contours(self, image, mode=cv2.RETR_EXTERNAL, sort_method="none"):
        '''
        Detect and return contours surrounding colors between the lower
        and upper bounds.
        :param image: full frame image containing the mirror
        :param mode: contour selection mode, see https://tinyurl.com/y8gx3w6w
        :param sort_method: options for sorting the contours
        :return: Sorted list of countours, largest first

        Contour sorting options: none, area (largest to smallest), area_asc (area
        smallest to largest), left-to-right, right-to-left, top-to-bottom, and
        bottom-to-top
        '''
        imgHSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(imgHSV, self.lower, self.upper)
        # remove noise with morphological "open"
        maskOpen = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernelOpen)
        # close up internal holes in contours with "close"
        maskClose = cv2.morphologyEx(maskOpen, cv2.MORPH_CLOSE, self.kernelClose)
        _, contours, _ = cv2.findContours(maskClose, mode, cv2.CHAIN_APPROX_SIMPLE)
        if sort_method == "none":
            return contours
        elif sort_method == "area":
            return sorted(contours, key=cv2.contourArea, reverse=True)
        elif sort_method == "area_asc":
            return sorted(contours, key=cv2.contourArea, reverse=False)
        else:
            return self.sort_contours(contours, method=sort_method)

    @staticmethod
    def get_rectangle(for_contour=None):
        """
        Returns the bounding rectangle for a contour, without
        considering the rotation of the enclosed object.
        :param for_contour: a CV2 contour (e.g. returned from get_contours)
        :return: Tuple of top-left corner coords and width, height
        """
        if for_contour is None:
            return None, None, None, None
        x, y, w, h = cv2.boundingRect(for_contour)
        return x, y, w, h

    @staticmethod
    def get_rotated_rectangle(for_contour=None):
        """
        Returns the rotated rectangle that encloses the provided contour.

        Note: the returned value is a 3-tuple of these values:
            [0] - x,y coordinates of the rectangle's center
            [1] - height, width of the rectangle
            [2] - rotation angle, if width < height add 90 to get "true" rotation
        :param for_contour: a CV2 contour (e.g. returned from get_contours)
        :return: cv2::minAreaRect
        """
        if for_contour is None:
            return None
        return cv2.minAreaRect(for_contour)

    @staticmethod
    def get_rotated_rectangle_as_boxpoints(for_contour=None):
        """
        Returns the box points for a rotated rectangle that
        encloses an object contained within the contour.
        :param for_contour: a CV2 contour (e.g. returned from get_contours)
        :return: box points
        """
        if for_contour is None:
            return None
        rect = cv2.minAreaRect(for_contour)
        box = cv2.boxPoints(rect)
        return np.int0(box)

    @staticmethod
    def get_skew_angle(for_contour=None):
        """
        Returns the angle in degrees at which a contour is canted
        :param for_contour: a CV2 contour (e.g. returned from get_contours)
        :return: angle, in degrees
        """
        # An alternate technique according to the OpenCV docs would be
        # (x,y),(MA,ma),angle = cv.fitEllipse(cnt)
        if for_contour is None:
            return None
        # get the min rotated bounding rect of the largest one
        rect = cv2.minAreaRect(for_contour)
        # grab the height, width, and angle of that rect
        height, width = rect[1]
        angle = rect[2]
        # The value of OpenCV's angle depends on the rect's
        # height/width ratio. https://stackoverflow.com/a/24085639/292947
        if width < height:
            angle += 90
        return angle

    @staticmethod
    def get_extreme_points(for_contour=None):
        """
        Get the leftmost, topmost, etc points of a contour
        :param for_contour: a CV2 contour (e.g. returned from get_contours)
        :return: leftmost, rightmost, topmost, bottommost coordinates
        """
        if for_contour is None:
            return None, None, None, None
        leftmost = tuple(for_contour[for_contour[:, :, 0].argmin()][0])
        rightmost = tuple(for_contour[for_contour[:, :, 0].argmax()][0])
        topmost = tuple(for_contour[for_contour[:, :, 1].argmin()][0])
        bottommost = tuple(for_contour[for_contour[:, :, 1].argmax()][0])
        return leftmost, rightmost, topmost, bottommost

    @staticmethod
    def do_shapes_match(contour_1=None, contour_2=None, tolerance=0.1):
        """
        Determines if shapes match, ignoring rotation and scaling
        :param contour_1: a CV2 contour (e.g. returned from get_contours)
        :param contour_2: a CV2 contour (e.g. returned from get_contours)
        :param tolerance: float, tolerance factor
        :return: boolean
        """
        if contour_1 is None or contour_2 is None:
            return False
        diff = cv2.matchShapes(contour_1, contour_2, 1, 0.0)
        return math.isclose(0, diff, abs_tol=tolerance)

    @staticmethod
    def sort_contours(contours, method="left-to-right"):
        reverse = False
        i = 0
        if method == "right-to-left" or method == "bottom-to-top":
            reverse = True
        if method == "top-bottom" or method == "bottom-to-top":
            i = 1
        bounding_boxes = [cv2.boundingRect(c) for c in contours]
        contours, boundingBoxes = zip(*sorted(zip(contours, bounding_boxes),
                                              key=lambda b: b[1][i],
                                              reverse=reverse))
        return contours, bounding_boxes
