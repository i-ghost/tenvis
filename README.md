Tenvis python tools
=====================
This is a collection of tools for manipulating output from Tenvis IP cameras. Works fine on Windows and GNU/Linux with Python 2.6.x-2.7.x

camsort
---------------------
Takes JPEGs dumped by an IP camera and sorts them into subdirectories in the following format:
```camera name/year/month/day/timestamp.jpg```

_camsort_ will also embed the timestamp into the bottom left-hand corner of the image using the ```droid sans mono``` font (this can be changed if this font is unavailable). JPEGs are compressed if ```jpegtran``` is available.

cam2mpg
---------------------
Takes the output of _camsort_ and stitches the images into an MPEG-4 video file (1 frame per second). _cam2mpg_ also creates backups before operating on a directory. These backups are stored in a _.backup_ subdirectory of a given month. _cam2mpg_ operates on yesterdays set of images by default, although it can be made to operate on an arbitrary directory. Run ```python cam2mpg --help``` for full usage instructions.

Requirements
---------------------

* ffmpeg (compiled with libjpeg and x264 support)
* jpegtran (typically bundled with libjpeg-turbo)

You should probably have a read of _camsort_ before running it, as you might want to change the font used when timestamping files. Default is Google DroidSansMono.ttf (assumed to be living in /usr/share/fonts/truetype/DroidSansMono.ttf).

Recommended usage
=====================
_camsort_ and _cam2mpg_ should be placed in the directory where the IP camera uploads its images to.
I personally recommend setting up two [cronjobs] as such:

```
@hourly cd path/to/toplevel/camera/dir; python camsort.py &> /dev/null
10 0 * * * cd path/to/toplevel/camera/dir; python cam2mpg.py &> /dev/null
```

The first entry runs _camsort_ every hour, and the second runs _cam2mpg_ ten minutes after midnight allowing it to operate on the previous day.

License
=====================
This toolset, with the exception of _progressmeter.py_, is licensed under the [3-clause BSD license]. _progressmeter.py_ is licensed under the [PSF] license.


Disclaimer
======================
This toolset has only been tested with one model of camera: the [JPT3815W]. While _cam2mpg_ was recently rewritten to be conservative about what it does, _camsort_ is still a little rough around the edges. I am not responsible for any data loss that may occur through the use of this toolset. __Always__ test against a small sample of images first before deploying, and read the output of ```python cam2mpg --help```.


[cronjobs]: https://en.wikipedia.org/wiki/Cron
[JPT3815W]: http://www.tenvis.com/jpt3815w-hot-pantilt-ip-camera-night-vsion-iphone-view-p-193.html
[3-clause BSD license]: http://opensource.org/licenses/BSD-3-Clause
[PSF]: http://docs.python.org/2/license.html