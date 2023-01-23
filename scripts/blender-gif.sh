#!/bin/bash
# usage: blender-gif.sh filename fps
#convert -delay 1x"$2" -dispose Background /tmp/*.png +dither -colors 255 +map "$1".gif
gifski --fps "$2" -o "$1".gif /tmp/*.png
#not needed after figuring out +map
#gifsicle --batch --colors 256 --dither=none $1.gif

#img2webp ONLY takes ms per frame, convert our fps to that
((timePerFrame=1000 / $2))
img2webp -loop 0 -lossy -d "$timePerFrame" /tmp/*.png -o "$1".webp

#calculate bitrate depending on fps
#we want a target of 256kb, which is 2048K at 30fps, 1024K at 15fps
#TODO account for number of frames, not just fps. Currently assumes 30 frames total (hardcoded in). Get count of *.png glob. Weird behavior at large counts, needded 180 for 90 frames
#TODO try constrained quality mode https://trac.ffmpeg.org/wiki/Encode/VP9
bitrate=$(bc -l <<< "$2 / 90 * 2048")
#scale to 512 on the x axis - doesn't handle portrait images right
#ffmpeg -f image2 -framerate "$2" -pattern_type glob -i '/tmp/*.png' -c:v libvpx-vp9 -b:v "${bitrate}K" -pass 1 -an -f null /dev/null && \
#ffmpeg -y -f image2 -framerate "$2" -pattern_type glob -i '/tmp/*.png' -c:v libvpx-vp9 -b:v "${bitrate}K" -pass 2 -vf "scale=512:-2" "$1".webm

#make a discord apng sticker
#TODO limit to 512kb via dropping quality
#ffmpeg -y -f image2 -framerate "$2" -pattern_type glob -i '/tmp/*.png' -plays 0 -vf "scale=320:320" -f apng "$1".png

#add a static bg without rerendering
#convert -delay 1x"$2" bg.png null: \( /tmp/*.png \) -layers Composite -layers Optimize "$1"bg.gif

#dithering for gifs
#need -append and +remap
convert -delay 1x"$2" -dispose Background /tmp/*.png -ordered-dither o8x8,8,8,4 +remap "$1"d.gif
#convert old-test.png -ordered-dither o8x8,8,8,4 old-test4.gif
#convert -delay 1x"$2" -dispose Background /tmp/*.png -dither Floyd-Steinberg "$1"fs.gif

#1bit bw dither
#convert old-test.png -dither Floyd-Steinberg -monochrome old-test-dithered1.png
convert -delay 1x"$2" -dispose Background /tmp/*.png -dither Floyd-Steinberg -monochrome "$1"1bit.gif
#convert -delay 1x"$2" -dispose Background /tmp/*.png -ordered-dither o8x8 -monochrome "$1"1bito.gif
