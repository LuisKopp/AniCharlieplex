# Hasty conversion utility for flame pendant project.  Takes a bunch of
# images (filenames received on command line) and outputs a big C array
# to use with the accompanying Arduino sketch.
# Typical invocation: python convert.py *.png > data.h
# Inputs are assumed valid; this does NOT perform extensive checking to
# confirm all images are the same size, etc.
# Requires Python and Python Imaging Library.

from __future__ import print_function

from PIL import Image
import zipfile
import sys
import io

# --------------------------------------------------------------------------

MAX_COLS = 12
cols     = MAX_COLS # Current column number in output (force indent on first one)
byteNum  = 0
numBytes = 0
out_buffer = []

image_rotation = 180
flip_vertical = True
flip_horizontal = False
image_resize = True
image_tgt_size = (9,16)

def writeByte(n):
    global cols, byteNum, numBytes, out_buffer

    cols += 1                    # Increment column #
    if cols >= MAX_COLS:               # If max column exceeded...
        out_buffer.append("\n")  # end current line
        out_buffer.append("  ")  # and start new one
        cols = 0                 # Reset counter
    out_buffer.append("0x{:02X}".format(n))
    byteNum += 1
    if byteNum < numBytes:
        out_buffer.append(",")
        if cols < MAX_COLS-1:
            out_buffer.append(" ")

# --------------------------------------------------------------------------

prior    = None
bytes    = 0
numBytes = 0xFFFF
frames = {}

if len(sys.argv) < 2:
    print("! Not enough arguments, exiting...")
    sys.exit()
elif sys.argv[1].lower().endswith('.zip'):
    with zipfile.ZipFile(sys.argv[1], 'r') as myzip:
        for frame_file in sorted(myzip.namelist()):
            if frame_file.endswith('/'):
                continue
            with myzip.open(frame_file) as frame_file_unzipped:
                frame_data = frame_file_unzipped.read()
            if frame_file.lower() == 'about.txt':
                for line in frame_data.split('\n'):
                    out_buffer.append("// {:s}\n".format(line))
            else:
                frames[frame_file] = {'data': frame_data}
else:
    for frame_file in sys.argv[1:]:
        with open(frame_file, 'rb') as myfile:
            frames[frame_file] = {'data': myfile.read()}

if len(out_buffer) > 0 and out_buffer[-1] == "// \n":
    out_buffer.pop(-1)
if len(out_buffer) > 0:
    out_buffer.append("\n")
out_buffer.append("const uint8_t PROGMEM anim[] = {")

for name in sorted(frames):
    image = Image.open(io.BytesIO(frames[name]['data']))
    if image.mode != 'L': # Not grayscale? Convert it
        image = image.convert("L")
    if image_rotation > 0:
        image = image.rotate(image_rotation)
    if flip_vertical:
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
    if flip_horizontal:
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
    if image_resize:
        image = image.resize(image_tgt_size, Image.BICUBIC)
    ### To make the flame a bit higher and narrower...:
    #image = image.resize((9,20), Image.BICUBIC)
    #image = image.crop((0, 4, 9, 20))
    ### To make the flame a bit higher and fatter...:
    #image = image.resize((9,22), Image.BICUBIC)
    #image = image.crop((2, 6, 11, 22))
    image.pixels = image.load()

    # Gamma correction:
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            image.pixels[x, y] = int(
                pow((image.pixels[x, y] / 255.0), 2.7) * 255.0 + 0.5)

    if prior:
        # Determine bounds of changed area
        x1 = image.size[0]
        y1 = image.size[1]
        x2 = y2 = -1
        for y in range(image.size[1]):
            for x in range(image.size[0]):
                if image.pixels[x, y] != prior.pixels[x, y]:
                    if x < x1: x1 = x
                    if x > x2: x2 = x
                    if y < y1: y1 = y
                    if y > y2: y2 = y
    else:
        # First image = full frame
        x1 = y1 = 0
        x2 = 8
        y2 = 15

    # Column major!
    writeByte((x1 << 4) | y1) # Top left corner
    writeByte((x2 << 4) | y2) # Bottom right corner
    bytes += 2
    for x in range(x1, x2 + 1):
        for y in range(y1, y2 + 1):
            writeByte(image.pixels[x, y])
            bytes += 1

    prior = image


writeByte(0xFF) # EOD marker
bytes += 1

out_buffer.append("\n}; // " + str(bytes) + " bytes")
out_buffer.append("\n")

for line in out_buffer:
    sys.stdout.write(line)
