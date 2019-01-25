# Extras

Scripts and tools that are not part of the robovision library that you install from PyPI. These are useful as a basis for your actual scripts for FRC vision tasks.

### auto_calibrate.py

Measure camera / lens parameters automatically, creating a pickled object that can be later used to remove lens distortions from captured images. See the [auto calibration](autocalibrate.md) doc for more info.

### get_colors.py

Determine the 5 most common colors (in both RGB and HSV spaces) in an image within the region selected by the user. Run `python3 get_colors.py -h` for basic usage info.

### distance_calibration.py

Determine the camera's perceived focal length, which is needed to calculate the distance to objects in captured images. See [distances.md](distances.md) for more information.

### distance_finder.py

Using the perceived focal length determined with distance_calibration.py, measure the distances to a reference retroreflective tape. See [distances.md](distances.md) for more information.

### jetson_test.py

Quick script for testing access to the Jetson development board's camera, a USB camera, or an IP camera.

# License

MIT License

Copyright (c) 2018, Tim Poulsen, All rights reserved.
