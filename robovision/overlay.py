"""
Overlay borders, text, arrows, crosshairs on images

Author: Tim Poulsen
Web site: https://timpoulsen.com
Copyright 2019, Tim Poulsen, all rights reserved
License: MIT
"""
import cv2


def draw_border(image, color, thickness=4):
    bordered_image = image.copy()
    if color is None or type(color) is not tuple or len(color) != 3:
        color = (0, 0, 255)
    height, width = image.shape[:2]
    top_left = int(0 + thickness / 2), int(0 + thickness / 2)
    bottom_right = int(width - thickness / 2), int(height - thickness / 2)
    cv2.rectangle(bordered_image, top_left, bottom_right, color, thickness)
    return bordered_image


def draw_arrow(image, color, direction=90, thickness=4):
    arrowed_image = image.copy()
    if color is None or type(color) is not tuple or len(color) != 3:
        color = (0, 0, 255)
    if type(direction) is not int or direction not in [0, 90, 180, 270]:
        direction = 90
    height, width = image.shape[:2]
    if direction == 0:
        start = int(width * 0.15), int(height * 0.66)
        end = int(width * 0.15), int(height * 0.33)
    elif direction == 90:
        start = int(width * 0.33), int(height * 0.80)
        end = int(width * 0.66), int(height * 0.80)
    elif direction == 180:
        start = int(width * 0.85), int(height * 0.33)
        end = int(width * 0.85), int(height * 0.66)
    elif direction == 270:
        start = int(width * 0.66), int(height * 0.80)
        end = int(width * 0.33), int(height * 0.80)
    tip_length = .01 * thickness / 2
    arrowed_image = cv2.arrowedLine(arrowed_image, start, end, color, thickness, 8, 0, tip_length)
    return arrowed_image


def draw_text(image, color, text="3, 2, 1 Robots!", font=cv2.FONT_HERSHEY_SIMPLEX):
    text_image = image.copy()
    if color is None or type(color) is not tuple or len(color) != 3:
        color = (0, 0, 255)
    height, width = image.shape[:2]
    line_type = cv2.LINE_8
    font_size = 4
    line_thickness = 12
    # Center text taking into account its size
    textsize = cv2.getTextSize(text, font, font_size, line_thickness)[0]
    textX = (width - textsize[0]) // 2
    textY = (height + textsize[1]) // 2
    cv2.putText(text_image, text, (textX, textY), font, font_size, color, line_thickness, line_type)
    return text_image


def draw_crosshairs(image, color):
    xhairs_image = image.copy()
    if color is None or type(color) is not tuple or len(color) != 3:
        color = (0, 0, 255)
    height, width = image.shape[:2]
    x = width // 2
    y = height // 2
    length = height // 2
    line_thickness = 2
    marker_type = cv2.MARKER_CROSS
    cv2.drawMarker(xhairs_image, (x, y), color, marker_type, length, line_thickness)
    return xhairs_image

