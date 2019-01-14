# Extras

Scripts and tools that are not part of the robovision library, yet still useful.

### auto_calibrate.py

Measure camera / lens parameters automatically, creating a pickled object that can be later used to remove lens distortions from captured images. See the [auto calibration](autocalibrate.md) doc for more info.

### get_colors.py

Determine the 5 most common colors (in both RGB and HSV spaces) in an image within the region selected by the user. Run `python3 get_colors.py -h` for basic usage info.

### get_apparent_fov.py

Determine the camera's apparent field of view, which is needed to calculate the distance to objects in captured images. *Incomplete*

# License

MIT License

Copyright (c) 2018, Tim Poulsen, All rights reserved.
