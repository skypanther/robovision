"""
Preprocessor helper

Author: Tim Poulsen
Web site: https://timpoulsen.com
Copyright 2018, Tim Poulsen, all rights reserved
License: MIT
"""
import cv2
import logging


class Preprocessor():
    def __init__(self, image_size=None, log_level=logging.DEBUG):
        logging.basicConfig(level=log_level, format='%(levelname)s - %(message)s')
        self.image_size = self.set_image_size(image_size)
        self.processors = []

    def preprocess(self, image):
        """
        Process the given image, passing it sequentially through the functions,
        passing any arguments or named arguments if supplied. If an image_size
        is set, resizing will be the first operation performed on the image.

        :param image: Image to process
        :return: Processed image
        """
        img = image.copy()
        if self.image_size is not None:
            dim = (self.image_size, self.image_size)
            img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        for processor in self.processors:
            func, args, kwargs = processor
            if callable(func):
                # TODO: optimize this
                if args is not None and kwargs is not None:
                    img = func(img, *args, **kwargs)
                elif args is None and kwargs is not None:
                    img = func(img, **kwargs)
                elif args is not None and kwargs is None:
                    img = func(img, *args)
                else:
                    img = func(img)
        return img

    def add_processor(self, func, args=None, kwargs=None):
        """
        Add a processor function to the stack, optionally passing
        arguments that will be passed to the function when it's called

        :param func: A reference to the function to call. Must be `callable`
        :param args: Optional, tuple of unnamed arguments to pass in order to the function.
        :param kwargs: Optional, dictionary of named arguments to pass to the function
        """
        if callable(func):
            self.processors.append((func, args, kwargs))

    def set_image_size(self, image_size):
        """
        Simple setter function for the image_size property.
        """
        try:
            self.image_size = int(image_size)
        except (TypeError, ValueError):
            self.image_size = None
