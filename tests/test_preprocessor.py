"""
pylint tests, run from main robovision directory with `pytest`
"""
import cv2
import sys
from os import path
from unittest.mock import MagicMock
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from robovision import robovision as rv

kitten = cv2.imread('tests/kitten.jpg')
h, w = kitten.shape[:2]
pp = rv.Preprocessor()


def test_set_size():
    pp.set_image_size(100)
    assert pp.image_size == 100


def test_preprocessor_list_is_empty():
    pp.set_image_size(100)
    assert len(pp.processors) == 0


def test_processed_image():
    pp.set_image_size(100)
    img = pp.preprocess(kitten)
    h, w = img.shape[:2]
    assert h == 100


def test_preprocessor():
    kitty = rv.resize_raw(kitten, width=100)
    foo = MagicMock(return_value=kitty)
    pp.add_processor(foo)
    img = pp.preprocess(kitty)
    foo.assert_called
    h, w = img.shape[:2]
    assert h == 100
