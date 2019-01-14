"""
Get the HSV colors of a region you select from a live image
"""
import argparse
import cv2
import numpy as np
import os
import sys
import textwrap
from sklearn.cluster import KMeans

# If you've `git cloned` the repo and are running the examples locally
# you'll need the next line so that Python can find the robovision library
# Otherwise, comment out the sys.path... line
sys.path.append(os.path.dirname(os.path.realpath('.')))
import robovision as rv  # noqa: E402

coords = []
drawing = False


def main():
    ap = argparse.ArgumentParser(epilog=textwrap.dedent('''\
        Get the 5 most common colors of the area you select in the preview

        The source param can be any of the following:
        Integer       - Webcam with 0 typically the built-in webcam
        'picam'       - Raspberry Pi camera
        'http://...'  - URL to an IP cam, e.g. http://192.168.1.19/mjpg/video.mjpg

        Examples:
        python3 get_colors.py -s 0
        python3 get_colors.py -s picam
        python3 get_colors.py -s http://192.168.1.19/mjpg/video.mjpg
        '''),
        formatter_class=argparse.RawDescriptionHelpFormatter
        )  # noqa: E124
    ap.add_argument("-s", "--source", required=False,
                    help="Video source, e.g. the webcam number")
    args = vars(ap.parse_args())
    source = args["source"]
    vs = None
    try:
        webcam = int(source)
        vs = rv.VideoStream(source="webcam", cam_id=webcam)
    except ValueError:
        if source == "picam":
            vs = rv.VideoStream(source="picam")
        else:
            vs = rv.VideoStream(source="ipcam", ipcam_url=source)
    if source is None:
        print("Invalid source")
        exit()
    vs.start()
    cv2.namedWindow('CapturedImage', cv2.WINDOW_NORMAL)
    while True:
        frame = vs.read_frame()
        cv2.imshow('CapturedImage', frame)
        cv2.setMouseCallback('CapturedImage', click_and_crop, frame)
        # wait for Esc or q key and then exit
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord("q"):
            print('Colors measured at coordinates: {}'.format(coords))
            cv2.destroyAllWindows()
            vs.stop()
            break


def click_and_crop(event, x, y, flag, image):
    """
    Callback function, called by OpenCV when the user interacts
    with the window using the mouse. This function will be called
    repeatedly as the user interacts.
    """
    # get access to a couple of global variables we'll need
    global coords, drawing
    if event == cv2.EVENT_LBUTTONDOWN:
        # user has clicked the mouse's left button
        drawing = True
        # save those starting coordinates
        coords = [(x, y)]
    elif event == cv2.EVENT_MOUSEMOVE:
        # user is moving the mouse within the window
        if drawing is True:
            # if we're in drawing mode, we'll draw a green rectangle
            # from the starting x,y coords to our current coords
            clone = image.copy()
            cv2.rectangle(clone, coords[0], (x, y), (0, 255, 0), 2)
            cv2.imshow('CapturedImage', clone)
    elif event == cv2.EVENT_LBUTTONUP:
        # user has released the mouse button, leave drawing mode
        # and crop the photo
        drawing = False
        # save our ending coordinates
        coords.append((x, y))
        if len(coords) == 2:
            # calculate the four corners of our region of interest
            ty, by, tx, bx = coords[0][1], coords[1][1], coords[0][0], coords[1][0]
            # crop the image using array slicing
            roi = image[ty:by, tx:bx]
            height, width = roi.shape[:2]
            if width > 0 and height > 0:
                # make sure roi has height/width to prevent imshow error
                # and show the cropped image in a new window
                cv2.namedWindow("ROI", cv2.WINDOW_NORMAL)
                cv2.imshow("ROI", roi)
                height, width, _ = np.shape(roi)

                # reshape the image to be a simple list of RGB pixels
                reshaped_image = roi.reshape((height * width, 3))

                # we'll pick the 5 most common colors
                num_clusters = 5
                clusters = KMeans(n_clusters=num_clusters)
                clusters.fit(reshaped_image)

                # count the dominant colors and put them in "buckets"
                histogram = make_histogram(clusters)
                # then sort them, most-common first
                combined = zip(histogram, clusters.cluster_centers_)
                combined = sorted(combined, key=lambda x: x[0], reverse=True)

                # finally, we'll output a graphic showing the colors in order
                bars = []
                hsv_values = []
                for index, rows in enumerate(combined):
                    bar, rgb, hsv = make_bar(100, 100, rows[1])
                    print(f'Bar {index + 1}')
                    print(f'  RGB values: {rgb}')
                    print(f'  HSV values: {hsv}')
                    hsv_values.append(hsv)
                    bars.append(bar)

                # sort the bars[] list so that we can show the colored boxes sorted
                # by their HSV values -- sort by hue, then saturation
                sorted_bar_indexes = sort_hsvs(hsv_values)
                sorted_bars = [bars[idx] for idx in sorted_bar_indexes]
                cv2.imshow('Sorted by HSV values', np.hstack(sorted_bars))
                cv2.imshow(f'{num_clusters} Most Common Colors', np.hstack(bars))


def make_histogram(cluster):
    """
    Count the number of pixels in each cluster
    :param: KMeans cluster
    :return: numpy histogram
    """
    numLabels = np.arange(0, len(np.unique(cluster.labels_)) + 1)
    hist, _ = np.histogram(cluster.labels_, bins=numLabels)
    hist = hist.astype('float32')
    hist /= hist.sum()
    return hist


def make_bar(height, width, color):
    """
    Create an image of a given color
    :param: height of the image
    :param: width of the image
    :param: BGR pixel values of the color
    :return: tuple of bar, rgb values, and hsv values
    """
    bar = np.zeros((height, width, 3), np.uint8)
    bar[:] = color
    red, green, blue = int(color[2]), int(color[1]), int(color[0])
    hsv_bar = cv2.cvtColor(bar, cv2.COLOR_BGR2HSV)
    hue, sat, val = hsv_bar[0][0]
    return bar, (red, green, blue), (hue, sat, val)


def sort_hsvs(hsv_list):
    """
    Sort the list of HSV values
    :param hsv_list: List of HSV tuples
    :return: List of indexes, sorted by hue, then saturation, then value
    """
    bars_with_indexes = []
    for index, hsv_val in enumerate(hsv_list):
        bars_with_indexes.append((index, hsv_val[0], hsv_val[1], hsv_val[2]))
    bars_with_indexes.sort(key=lambda elem: (elem[1], elem[2], elem[3]))
    return [item[0] for item in bars_with_indexes]


if __name__ == "__main__":
    main()
