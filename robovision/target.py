"""

Determine target characteristics




"""
import cv2
import math
import numpy as np


def _noop():
    pass


class Target():
    def __init__(self):
        pass

    def set_color_range(self, lower=(100, 100, 100), upper=(255, 255, 255)):
        self.lower = lower
        self.upper = upper

    @staticmethod
    def get_countours(image=None, thresh_lower=127, thresh_upper=255):
        if image is None:
            return []
        img = image.copy()
        if len(img.shape) == 3:
            # a grayscale image will return a 2-tuple, not a 3-tuple
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(img, thresh_lower, thresh_upper, cv2.THRESH_BINARY)
        # get the countours (only outermost/external, no nested contours)
        _, cnts, _ = cv2.findContours(thresh,
                                      cv2.RETR_EXTERNAL,
                                      cv2.CHAIN_APPROX_SIMPLE)
        # sort by area, largest to smallest
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
        return cnts

    @staticmethod
    def get_rectangle(for_contour=None):
        """
        Returns the bounding rectangle for a contour, without
        considering the rotation of the enclosed object.
        """
        if for_contour is None:
            return None, None, None, None
        x, y, w, h = cv2.boundingRect(for_contour)
        return x, y, w, h

    @staticmethod
    def get_rotated_rectangle(for_contour=None):
        """
        Returns the box points for a rotated rectangle that
        encloses an object contained within the contour.
        """
        if for_contour is None:
            return None
        rect = cv2.minAreaRect(for_contour)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        return box

    @staticmethod
    def get_skew_angle(for_contour=None):
        """
        Returns the angle in degrees at which a contour is canted

        An alternate technique according to the OpenCV docs would be
        (x,y),(MA,ma),angle = cv.fitEllipse(cnt)
        """
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
        if for_contour is None:
            return None, None, None, None
        leftmost = tuple(for_contour[for_contour[:, :, 0].argmin()][0])
        rightmost = tuple(for_contour[for_contour[:, :, 0].argmax()][0])
        topmost = tuple(for_contour[for_contour[:, :, 1].argmin()][0])
        bottommost = tuple(for_contour[for_contour[:, :, 1].argmax()][0])
        return leftmost, rightmost, topmost, bottommost

    @staticmethod
    def do_shapes_match(contour_1=None, contour_2=None, tolerance=0.1):
        if contour_1 is None or contour_2 is None:
            return False
        diff = cv2.matchShapes(contour_1, contour_2, 1, 0.0)
        return math.isclose(0, diff, abs_tol=tolerance)
