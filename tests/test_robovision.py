"""
pylint tests, run from main robovision directory with `pytest`
"""
import cv2
import numpy as np
import sys
from os import path
from unittest.mock import MagicMock
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from robovision import robovision as rv

kitten = cv2.imread('tests/kitten.jpg')
h, w = kitten.shape[:2]
bw = cv2.imread('tests/bw.png', 0)


def test_resize():
    small_kitten = rv.resize(kitten, width=100)
    sh, sw = small_kitten.shape[:2]
    assert sw == 100
    assert sh == 100


def resize_raw():
    small_kitten = rv.resize_raw(kitten, width=100)
    sh, sw = small_kitten.shape[:2]
    ratio = w / sw
    test_height = h * ratio
    assert sw == 100
    assert sh == test_height


def test_contrast():
    con = rv.adjust_contrast(bw, contrast=-10.)
    black_pixel = con[1][10]
    white_pixel = con[1][60]
    assert black_pixel == 0
    assert white_pixel == 230


def test_brightness():
    con = rv.adjust_brightness(bw, brightness=100.)
    black_pixel = con[1][10]
    white_pixel = con[1][60]
    assert black_pixel == 100
    assert white_pixel == 255


def test_brightness_contrast():
    con = rv.adjust_brightness_contrast(bw, brightness=100., contrast=-100)
    black_pixel = con[1][10]
    white_pixel = con[1][60]
    assert black_pixel == 100
    assert white_pixel == 100


def test_equalize():
    rv.equalize = MagicMock(return_value=kitten)
    kitty = rv.equalize(kitten)
    assert kitten.shape[:2] == kitty.shape[:2]
