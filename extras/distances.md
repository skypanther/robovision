# Distance finding scripts

Finding distances to the retroreflective tape is a common need in an FRC competition. Provided here are two scripts you can use as a basis for calculating such distances.

## Camera calibration

First, you must calibrate by determining your camera's perceived focal length. Do that using the `distance_calibration.py` script as follows:

1. Cut and mount a 12-inch strip (be as precise as you can) of retroreflective tape onto a piece of cardboard
2. Place it a carefully measured 36-inches from your camera (be as precise as you can).
3. Run `distance_calibration.py`
4. In the camera preview, drag to select the area in the preview window where the tape is shown. The height and width of the selected area in pixels will be output. Repeat a few times, average the results and plug them into the following formula to get your camera's apparent focal length.

`F = (P x  D) / W`

Where P is the width in pixels, D is the distance, and W is the actual width.

## Distance calculations

After calibrating using distance_calibration.py, use the `distance_finder.py` script to find the distance to the 12" strip of retroreflective tape. For example, move it to an arbitrary distance between roughly a few inches to ten or so feet, then run this script to calculate its distance from your camera.

You must provide two arguments to `distance_finder.py`:

* `-s source` - the source, such as a the webcam number, 'picam', or an IP camera's URL
* `-f focallength` - the perceived focal length you calculated with the calibration script

Examples:

`python3 distance_finder.py -s 0 -f 550.0`

(Using webcam 0, calculate the distance for a camera with a perceived focal length of 550.0)

`python3 distance_finder.py -s http://10.15.18.100/mjpg/video.mjpg -f 550.0`

(Do the same, for an Axis IP camera at that address)
