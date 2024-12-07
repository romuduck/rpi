import cv2

img=cv2.imread("../resources/img/cat.jpg")
cv2.namedWindow("Cat", cv2.WINDOW_NORMAL)
cv2.imshow("cat", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
