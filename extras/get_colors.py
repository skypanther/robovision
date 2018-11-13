import argparse
import cv2
import numpy as np
from sklearn.cluster import KMeans

coords = []
drawing = False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", help="Path to the image")
    args = vars(ap.parse_args())
    # load the image specified at the command line or capture
    # an image from the built-in webcam
    image_source = args["image"] if args["image"] else 0
    image = get_image(image_source)
    if image is not None:
        cv2.namedWindow('CapturedImage', cv2.WINDOW_NORMAL)
        cv2.imshow('CapturedImage', image)
        cv2.setMouseCallback('CapturedImage', click_and_crop, image)
        while True:
            # wait for Esc or q key and then exit
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord("q"):
                print('Colors measured at coordinates: {}'.format(coords))
                cv2.destroyAllWindows()
                break


def get_image(source):
    """
    Get an image from the given source, either from a file or webcam
    """
    image = None
    if isinstance(source, int):
        cam = cv2.VideoCapture(source)
        image_captured, image = cam.read()
        cam.release()
        if image_captured is False:
            return None
    else:
        image = cv2.imread(source, cv2.IMREAD_COLOR)
    return image


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
