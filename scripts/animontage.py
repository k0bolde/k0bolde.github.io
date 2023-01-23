#!/usr/bin/env python3
# takes a list of gifs/webps, splits all the frames, for each frame creates a montage, assemble montages into a correctly timed gif/webp
# requires imagemagick
# TODO http server/site
# TODO options I use often
#   tile resolution (usually 512x512 or 128x128)
#   match shortest gif or match longest gif options
#   manual ms per frame
#   support ../ in filenames by stripping the path part off

from PIL import Image, ImageSequence
# cleanup temp files
import os
# calling imagemagick
import subprocess
# for direct argv access
# TODO change to https://docs.python.org/3/library/argparse.html
import sys
# easy threading
from multiprocessing import Process


def make_webp():
    frames = [Image.open(image) for image in montageNames]
    frame_one = frames[0]
    frame_one.save("out.webp", format="WEBP", append_images=frames, save_all=True, duration=int(avgMs), loop=0)
    # almost works, but flashes black. Check back when pillow updates
    # TODO not saving gifs with pillow because it hates transparency
    # frame_one.save("out2.gif", format="GIF", append_images=frames, save_all=True, duration=int(avgMs), loop=0,
    #                disposal=2, transparency=0)
    # frames = [Image.open(image) for image in glob.glob(f"{frame_folder}/*.JPG")]


# for each arg (except 0)
inputImages = []
for arg in sys.argv[1:]:
    inputImages.append(arg)

maxFrames = 30
avgMs = 0
tmpFolder = "/tmp/"


def split_gif(image):
    """Splitting up the gifs is slow, so do it concurrently."""
    with Image.open(image) as im:
        idx = 0
        for frame in ImageSequence.Iterator(im):
            frame.save(f"{tmpFolder}{image}_{idx}.png")
            idx += 1


tasks = []
for img in inputImages:
    p = Process(target=split_gif, args=(img,))
    p.start()
    tasks.append(p)

# need all this code just to get frame time avg (& frame count)
for i in range(len(inputImages)):
    with Image.open(inputImages[i]) as im:
        idx = 0
        for frame in ImageSequence.Iterator(im):
            idx += 1
        if getattr(frame, "n_frames", 1) > maxFrames:
            maxFrames = getattr(frame, "n_frames", 1)
        # only exists on gifs. input webp's don't have an accessible duration?
        if "duration" in frame.info:
            avgMs += frame.info["duration"]
        else:
            # TODO change this to an argument. default input ms per frame
            avgMs += 30.0
avgMs /= len(inputImages)
#I just want 15fps
avgMs = 45

# join down here so we can do the above code while waiting too!
for task in tasks:
    task.join()


def make_montage_frame(num):
    """Makes a single montage frame with imagemagick. Used for threading."""
    frame_names = []
    for img in inputImages:
        # handle mismatched animation lengths. Just show first frame if we're short
        #TODO loop short gifs instead of stopping?
        if os.path.exists(f"{tmpFolder}{img}_{num}.png"):
            frame_names.append(f"{tmpFolder}{img}_{num}.png")
        else:
            frame_names.append(f"{tmpFolder}{img}_0.png")

    subprocess.run(
        ["montage"] + frame_names + ["-background", "none", "-geometry", "512x512+0+0", f"{tmpFolder}{num}.png"],
        check=True)


montageTasks = []
montageNames = []
for i in range(maxFrames):
    montageNames.append(f"{tmpFolder}{i}.png")
    p = Process(target=make_montage_frame, args=(i,))
    p.start()
    montageTasks.append(p)
for task in montageTasks:
    task.join()


def make_final_gif():
    """Outputs the final gif using imagemagick."""
    subprocess.run(
        ["convert", "-delay", f"{int(avgMs)}x1000", "-dispose", "Background"] + montageNames + ["+dither", "-colors",
                                                                                                "255", "+map",
                                                                                                "out.gif"])
def make_gifski():
    """Outputs the gif using gifski"""
    subprocess.run(
        ["gifski", "--fps", f"{1000 / int(avgMs)}", "-o", "out.gif"] + montageNames)


#gif_proc = Process(target=make_final_gif)
gif_proc = Process(target=make_gifski)
gif_proc.start()
webp_proc = Process(target=make_webp)
webp_proc.start()
gif_proc.join()
webp_proc.join()

# delete tmp files
# TODO do this on error catch too
for i in range(maxFrames):
    if os.path.exists(f"{tmpFolder}{i}.png"):
        os.remove(f"{tmpFolder}{i}.png")
    for img in inputImages:
        if os.path.exists(f"{tmpFolder}{img}_{i}.png"):
            os.remove(f"{tmpFolder}{img}_{i}.png")
