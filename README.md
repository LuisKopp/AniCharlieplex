# AniCharlieplex

Animation for Adafruit Pro Trinket / Particle Photon / Espressif ESP32 devices when used with a IS31FL3731-driven Charlieplex 9x16 LED array. Loops an animation sequence on the display, in this case a flame

`data_pendant.h` is for the I/O-up orientation. `data_normal.h` is for the I/O-down orientation.

The sketch is comprised of the sketch and one of the data headers (which contain animation frames packed into PROGMEM array holding bounding rectangle + column-major pixel data for each frame) Note that this consumes most of the flash space on the ATmega328.

The `frames_flame.zip` archive contains the animation source PNG images originally generated via Adobe Premiere and Photoshop from Free Stock Video by user 'dietolog' on Videezy.com.

The Python script (works with Python >= 2.7), `convert_frames.py`, processes all the source images into the required data header format.

(For a more specific driver for the IS31FL3731 breakout, check out https://github.com/adafruit/Adafruit_IS31FL3731)

