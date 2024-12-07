import cv2
import time
from picamera2 import Picamera2


# load opencv classifier for face detection
face_cascade = cv2.CascadeClassifier("haarcascades/haarcascade_frontalface_default.xml")

# start a GUI window
cv2.startWindowThread()

# capture video, cam = cv2.VideoCapture(0) is replaced by picam capture
picam = Picamera2()
picam.configure(
	picam.create_preview_configuration(
		main={
			"format": "XRGB8888",
			"size": (640,480)
		}
	))

picam.start()


while True:
	img = picam.capture_array()
	
	# convert image from BGR to greyscale
	grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	
	# provide detected face coordinates
	coords = face_cascade.detectMultiScale(grey, 1.1, 5)
	
	# draw a rectangle with above coordinates
	for (x,y,w,h) in coords:
		cv2.rectangle(img, (x,y), (x+w, y+h), (255,255,255), 5)
	
	cv2.imshow("camera", img)
	if cv2.waitKey(1) & 0xFF == ord("q"):
		break
