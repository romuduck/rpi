import cv2

img = cv2.imread("person.jpeg")
face_cascade = cv2.CascadeClassifier("haarcascades/haarcascade_frontalface_default.xml")
coords = face_cascade.detectMultiScale(img)

x = coords[0][0]
y = coords[0][1]
w = coords[0][2]
h = coords[0][3]
cv2.rectangle(img, (x,y), (x+w, y+h), (255,255,255), 5)
cv2.imshow("preview", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
