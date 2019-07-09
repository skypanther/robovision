
Robovision
==========

Vision processing scripts useful for FIRST robotics teams and probably other purposes.

|licence| |pythonver| |opencvver|

.. |licence| image:: https://img.shields.io/badge/license-MIT-green.svg
.. |pythonver| image:: https://img.shields.io/badge/Python-3.5%2B-blue.svg
.. |opencvver| image:: https://img.shields.io/badge/OpenCV-3.4%2B-blue.svg

|version|

.. |version| image:: https://img.shields.io/badge/Version-0.1.4-orange.svg

Author: Tim Poulsen, mentor for Team 1518 Raider Robotics

Overview
--------

The robovision library includes functions useful for the types of vision tasks typically involved in a FIRST robotics competition. The goal of this library is to reduce (and hide) some of the complexity involved with target identification, measuring, field orienteering, etc.

Some of the functions included:

* Image acquisition from a web cam, IP cam (i.e. Axis cam), Raspberry Pi camera, or Jetson onboard gstreamer camera
* Lens distortion removal based on the camera calibrations created with the provided autocalibrate.py script
* Retroreflective target identification, contour finding, and geometry finding functions
* Image resizing, equalization, brightness and contrast adjustments, and more
* A preprocessor class, which enables you to set up a pipeline of functions that will be applied in series to an image.
* Overlay arrows, text, borders, or crosshairs on images

The autocalibrate script is a camera calibration utility, which uses the OpenCV chessboard technique to determine lens parameters to be used for dewarping operations. If you prefer, there's a manual_lens_calibration.py script that lets you adjust the various lens parameters until the image is visually correct.

Installation / Usage
--------------------

The best way to install this is with ``pip``:

.. code-block::

    $ pip install robovision


You can also clone the repo and install locally:

.. code-block::

    $ git clone https://github.com/skypanther/robovision.git
    $ cd robovision
    $ pip install -e .


Target environment
------------------

Our primary vision system is a Jetson TX2 board. I've done most of the development on a Mac OS X system, with some testing on an Ubuntu laptop. The scripts should work on a Raspberry Pi, but we haven't tested that yet. We don't intend to use or test on Windows systems, so your guess is as good as ours whether it will work there. (But feel free to make a pull request to add Windows compatibility.)

Our environment is:

* Python 3.5.x (newer versions, and Anaconda works too)
* OpenCV 3.4.x
* Jetson TX2 running Ubuntu 16.04 and JetPack 3.2.1
* Axis 206 IP camera
* Onboard Jetson gstreamer camera
* Microsoft Lifecam USB camera

Python 2.x is **not** supported.

Example
-------

.. code-block::

    import cv2
    import robovision as rv

    # create a video stream to our IP camera
    source = "http://10.15.18.100/mjpg/video.mjpg"
    vs = rv.VideoStream(source="ipcam", ipcam_url=source)

    # instantiate the targeting class and set the color range of
    # the retroreflective tape
    target = rv.Target()
    target.set_color_range(lower=(80, 100, 100), upper=(90, 255, 255))

    # start the video stream
    vs.start()

    cv2.namedWindow('CapturedImage', cv2.WINDOW_NORMAL)

    while True:
        frame = vs.read_frame()
        contours = target.find_contours(frame)
        if len(contours) > 0:
            cv2.drawContours(frame, contours, -1, (0, 0, 255), 3)
            print('angle {}'.format(target.get_skew_angle(contours[0])))
        cv2.imshow('CapturedImage', frame)
        # wait for Esc or q key and then exit
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord("q"):
            cv2.destroyAllWindows()
            vs.stop()
            break


See the `wiki <https://github.com/skypanther/robovision/wiki>`_ for more information.

Contributing
------------

Contributions are welcome! Feel free to open a pull request. Or, open an issue if you find something that doesn't work (which is probably a lot!).

License
-------

MIT License

Copyright (c) 2019, Tim Poulsen, All rights reserved.
