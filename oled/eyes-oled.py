import time
from datetime import datetime
import random


import board
import busio
import digitalio

from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

import subprocess


# Display Parameters
WIDTH = 128
HEIGHT = 64
BORDER = 5

# Display Refresh in s
FRAMEINTERVAL = 0.02  # 20ms, equivalent to 50fps
FRAMEINTERVAL = 0.01  # 10ms, equivalent to 100fps


class DynamicAttribute():
	list_attributes = []

	def __init__(self, default):
		self.default = self.current = self.target = default
		self.offset = 2  # when delta between current and target <= offset ==> we set current = target
		DynamicAttribute.list_attributes.append(self)

	def update(self):
		if abs(self.current - self.target) <= self.offset:
			self.current = self.target
		else:
			self.current = int((self.current + self.target)/2)

	@staticmethod
	def update_all():
		for attribute in DynamicAttribute.list_attributes:
			attribute.update()



class Eye():
	def __init__(self, width, height, radius, posX, posY):
		self.width = width
		self.borderRadius = radius
		self.positionX = posX
		self.positionY = posY
		self.height = DynamicAttribute(height)


	def updateDynamicAttributes(self):
		self.height.update()


	def open(self):
		if self.get_state() == "closed":
			self.height.target = self.height.default


	def close(self):
		if self.get_state() == "open":
			self.height.target = 1 


	def get_state(self):
		if self.height.current <= 1:  # + self.heightOffset:
			return "closed"
		if self.height.current >= self.height.default - 1:  # add offset
			return "open"


	def draw(self, drawingObject):
		drawingObject.rounded_rectangle([self.positionX, self.positionY, self.positionX + self.width, self.positionY + self.height.current], radius=self.borderRadius, fill=255, outline=255, width=1, corners=None)



class EyeBox():
	def __init__(self, posX, posY, width, height, maxWidth, maxHeight):
		self.width = DynamicAttribute(width)
		self.height = DynamicAttribute(height)
		self.positionX = DynamicAttribute(posX)
		self.positionY = DynamicAttribute(posY)
		self.maxWidth = maxWidth
		self.maxHeight = maxHeight


	def updateDynamicAttributes(self):
		self.width.update()
		self.height.update()
		self.positionX.update()
		self.positionY.update()


	# position against 3x3 columnxrow, [0,1,2]x[0,1,2]
	def move(self, column, row):
		self.positionX.target = int(column * (self.maxWidth - self.width.current)/2)
		self.positionY.target = int(row * (self.maxHeight - self.height.current)/2)


	def draw(self, drawingObject):
		drawingObject.rectangle([self.positionX.current, self.positionY.current, self.positionX.current + self.width.current, self.positionY.current + self.height.current], fill=0, outline=255)



class Face():
	def __init__(self, spaceBetweenEyes, screenWidth, screenHeight):
		eyeWidth = 36
		eyeHeight = 36
		eyeRadius = 8

		# we define the eye box perimeter
		eyeBoxWidth = 2*eyeWidth + spaceBetweenEyes
		eyeBoxHeight = eyeHeight

		self.eyeBox = EyeBox(int((screenWidth - eyeBoxWidth)/2), int((screenHeight - eyeBoxHeight)/2), eyeBoxWidth, eyeHeight, screenWidth, screenHeight)

		self.screenWidth = screenWidth
		self.screenHeight = screenHeight
		self.spaceBetweenEyes = DynamicAttribute(spaceBetweenEyes)

		self.leftEye = Eye(eyeWidth, eyeHeight, eyeRadius, 0, 0)
		self.rightEye = Eye(eyeWidth, eyeHeight, eyeRadius, 0, 0)
		self.centerEyesInEyeBox()


	def draw(self, drawingObject):
		# self.eyeBox.draw(drawingObject)
		self.leftEye.draw(drawingObject)
		self.rightEye.draw(drawingObject)


	def centerEyesInEyeBox(self):
		self.leftEye.positionY = self.eyeBox.positionY.current + int((self.eyeBox.height.current - self.leftEye.height.current)/2)
		self.rightEye.positionY = self.eyeBox.positionY.current + int((self.eyeBox.height.current - self.rightEye.height.current)/2)
		self.leftEye.positionX = self.eyeBox.positionX.current
		self.rightEye.positionX = self.eyeBox.positionX.current + self.spaceBetweenEyes.current + self.leftEye.width






# -------------------
# OLED + I2C set-up
# -------------------
# Define the Reset Pin
oled_reset = digitalio.DigitalInOut(board.D4)

# Use for I2C.
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=oled_reset)

# # Clear display.
oled.fill(0)
oled.show()




# -------------------
# Image handle
# -------------------
# define image size
image = Image.new("1", (WIDTH, HEIGHT))

# get a drawing object for this image
draw = ImageDraw.Draw(image)


# display the image, used when debugging without the oled screen
# image.show()





# build a face
face = Face(10, WIDTH, HEIGHT)




# -------------------
# Display loop: to be replaced by asyncio
# -------------------
origin_blink = datetime.now()
average_blink_period = 5
max_blink_period = 10
next_blink = random.randint(average_blink_period, max_blink_period)

origin_facemove = datetime.now()
average_facemove_period = 3
max_facemove_period = 7
next_facemove = random.randint(average_facemove_period, max_facemove_period)

origin_shaking = datetime.now()
average_shaking_period = 10
max_shaking_period = 15
next_shaking = random.randint(average_facemove_period, max_facemove_period)
shakingOn = 0
shakingAmplitude = 20
skakingDirection = 1
shakingDuration = 1


while True:

	# Draw a black filled box to clear the image.
	draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)

	# DEBUG - display a centered cross
	# draw.line(((64,30), (64,34)), fill=255, width=1)
	# draw.line(((62,32), (66,32)), fill=255, width=1)


	now  = datetime.now()

	#-----------
	# blinking 
	#-----------
	delta_blink = now - origin_blink
	# closing eyes from time to time
	if  delta_blink.total_seconds() > next_blink:
		origin_blink = datetime.now()
		next_blink = random.randint(average_blink_period, max_blink_period)

		# eye_choice = random.choice(["left", "right", "both"])
		eye_choice = random.choice(["both"])
		if eye_choice == "left":
			face.leftEye.close()
		elif eye_choice == "right":
			face.rightEye.close()
		elif eye_choice == "both":
			face.leftEye.close()
			face.rightEye.close()


	# re-opening closed eyes
	if face.leftEye.get_state() == "closed":
		face.leftEye.open()
	if face.rightEye.get_state() == "closed":
		face.rightEye.open()


	#-----------
	# moving 
	#-----------
	delta_facemove = now - origin_facemove
	# moving face
	if  delta_facemove.total_seconds() > next_facemove:
		origin_facemove = datetime.now()
		next_facemove = random.randint(average_facemove_period, max_facemove_period)

		move_choice_column = random.choice([0, 1, 2])
		move_choice_row = random.choice([0, 1, 2])
		face.eyeBox.move(move_choice_column, move_choice_row)



	# update eyes attributes
	DynamicAttribute.update_all()
	face.centerEyesInEyeBox()  # pb: il faut gerer ces positions differemment




	#-----------
	# shaking 
	#-----------
	# delta_shaking = now - origin_shaking
	# if shakingOn == 0 and delta_shaking.total_seconds() > next_shaking:
	# 	origin_shaking = datetime.now()
	# 	next_shaking = random.randint(average_shaking_period, max_shaking_period)
	# 	shakingOn = 1

	# elif shakingOn == 1 and delta_shaking.total_seconds() > shakingDuration:
	# 	origin_shaking = datetime.now()
	# 	shakingOn = 0

	# if shakingOn:
	# 	face.leftEye.positionX = face.leftEye.positionX + skakingDirection*shakingAmplitude
	# 	face.rightEye.positionX = face.rightEye.positionX + skakingDirection*shakingAmplitude
	# 	skakingDirection = skakingDirection * (-1)



	#-------------
	# Display
	#-------------
	face.draw(draw)


	# Display image
	oled.image(image)
	oled.show()
	time.sleep(FRAMEINTERVAL)










