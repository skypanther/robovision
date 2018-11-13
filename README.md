# Robovision

Vision processing scripts useful for FIRST robotics teams and probably other purposes.

License: MIT

Author: Tim Poulsen, mentor for Team 1518 Raider Robotics

## Overview

The robovision library includes these functions:

* image resizing, either proportionally (maintaining aspect ratio) or to a fixed/square size
* image equalization
* brightness and contrast adjustments
* a preprocessor class, which enables you to set up a pipeline of functions that will be applied in series to an image.
* edge detection
* removing lens distortions based on the camera calibrations created with autocalibrate.py

Separately, the autocalibrate script is a camera calibration utility, which uses the OpenCV chessboard technique to determine lens parameters to be used for dewarping operations.

## Installation / Usage

TBD

<!--
To install use pip:

    $ pip install robovision


Or clone the repo:

    $ git clone https://github.com/skypanther/robovision.git
    $ python setup.py install

-->

## Contributing

TBD

## Example

TBD

## License

MIT License

Copyright (c) 2018, Tim Poulsen, All rights reserved.
