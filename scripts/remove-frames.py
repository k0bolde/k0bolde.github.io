#!/usr/bin/env python3
# removes frames from gifs and retimes the leftover frames to run the same total length
# args: inputfile.gif skip_every_this_num_frames

from PIL import Image, ImageSequence
# cleanup temp files
import os
# calling imagemagick
import subprocess
# for direct argv access
# TODO change to https://docs.python.org/3/library/argparse.html
import sys

maxFrames = 0
avgMs = 0
tmpFolder = "/tmp/"

tmpFiles = []


def split_gif(image):
    with Image.open(image) as im:
        idx = 0
        for frame in ImageSequence.Iterator(im):
            tmpname = f"{tmpFolder}{image}_{idx}.gif"
            frame.save(tmpname)
            tmpFiles.append(tmpname)
            idx += 1


split_gif(sys.argv[1])

# need all this code just to get frame time avg (& frame count)
with Image.open(sys.argv[1]) as im:
    idx = 0
    for frame in ImageSequence.Iterator(im):
        idx += 1
        # only exists on gifs. input webp's don't have an accessible duration?
        if "duration" in frame.info:
            avgMs += frame.info["duration"]
        else:
            # TODO change this to an argument. default input ms per frame
            avgMs += 30.0
    if getattr(frame, "n_frames", 1) > maxFrames:
        maxFrames = getattr(frame, "n_frames", 1)
avgMs /= maxFrames

toremove = []
for i in range(len(tmpFiles)):
    if i % int(sys.argv[2]) == 0:
        # skip it and add its avg
        toremove.append(i)

losttime = 0
for i in range(len(toremove) - 1, 0, -1):
    if os.path.exists(tmpFiles[toremove[i]]):
        os.remove(tmpFiles[toremove[i]])
    # tmpFiles.remove(tmpFiles[i])
    tmpFiles.pop(toremove[i])
    losttime += avgMs

if losttime > 0:
    avgMs += losttime / len(tmpFiles)


def make_final_gif():
    """Outputs the final gif using imagemagick."""
    subprocess.run(
        ["convert", "-delay", f"{int(avgMs)}x1000", "-dispose", "Background"] + tmpFiles + ["+dither", "-colors",
                                                                                            "255", "+map",
                                                                                            "out.gif"])


make_final_gif()

# delete tmp files
# TODO do this on error catch too
for f in tmpFiles:
    if os.path.exists(f):
        os.remove(f)
