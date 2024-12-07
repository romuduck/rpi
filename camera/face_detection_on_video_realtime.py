#!/usr/bin/python3

# This version creates a lores YUV stream, extracts the Y channel and runs the face
# detector directly on that. We use the supplied OpenGL accelerated preview window
# and delegate the face box drawing to its callback function, thereby running the
# preview at the full rate with face updates as and when they are ready.


import time
import cv2

# the below is to be done after cv2 import to fix Qt platform plugin xcb error
import os
os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")

from picamera2 import MappedArray, Picamera2, Preview


# load face detector classifier
face_detector = cv2.CascadeClassifier("haarcascades/haarcascade_frontalface_default.xml")


def draw_faces(request):
    # MappedArray is a way to access camera buffer without using capture methods
    with MappedArray(request, "main") as m:
        for f in faces: # (x, y, w, h)
            # since faces coordinates are from low res buffer where size is different from main buffer
            # where we need to draw the rectange, we need to apply a factor
            # below is like (x * Rx, y * Ry, w * Rx, h * Ry) with Rx = w0/w1, Ry = h0/h1
            (x, y, w, h) = [c * n // d for c, n, d in zip(f, (w0, h0) * 2, (w1, h1) * 2)]
            cv2.rectangle(m.array, (x, y), (x + w, y + h), (0, 255, 0, 0))
 
 

picam2 = Picamera2()
picam2.start_preview(Preview.QTGL)
# configure main and lores (low res) streams. Lores stream will use YUV format (default format for lores)
# YUV420 is a special format where the first 'height' rows is for Y channel, which
# represents the luminance in grayscale, the next height/4 rows contain U channel
# and the next height/4 rows contain the V channel
config = picam2.create_preview_configuration(main={"size": (640, 480)},
                                             lores={"size": (320, 240), "format": "YUV420"})
picam2.configure(config)

# once we have loaded the configuration, we have access to some new info, like size or stride
# stride is the length of each row of the image in bytes
# since buffer are a one-dimension numpy array, stride allows to split buffer and 
# make it a 2D array
(w0, h0) = picam2.stream_configuration("main")["size"]
(w1, h1) = picam2.stream_configuration("lores")["size"]
s1 = picam2.stream_configuration("lores")["stride"]
faces = []
picam2.post_callback = draw_faces

picam2.start()

while True:
    buffer = picam2.capture_buffer("lores") # a 1D numpy array
    grey = buffer[:s1 * h1].reshape((h1, s1)) # we extract Y channel and make it a 2D array
    faces = face_detector.detectMultiScale(grey, 1.1, 3) # we look for face in the greyscale low res buffer
