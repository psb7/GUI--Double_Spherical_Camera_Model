import cv2
import numpy as np
import math
from dsphvcam import vcam,meshGen

def nothing(x):
    pass

WINDOW_NAME = "output"
cv2.namedWindow(WINDOW_NAME,cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME,700,700)

# Creating the tracker bar for all the features
cv2.createTrackbar("X",WINDOW_NAME,500,1000,nothing)
cv2.createTrackbar("Y",WINDOW_NAME,500,1000,nothing)
cv2.createTrackbar("Z",WINDOW_NAME,0,1000,nothing)
cv2.createTrackbar("alpha",WINDOW_NAME,180,360,nothing)
cv2.createTrackbar("beta",WINDOW_NAME,180,360,nothing)
cv2.createTrackbar("gama",WINDOW_NAME,180,360,nothing)
cv2.createTrackbar("distortion_alpha",WINDOW_NAME,0,5,nothing)
cv2.createTrackbar("distortion_xi",WINDOW_NAME,0,10,nothing)
cv2.createTrackbar("focus",WINDOW_NAME,100,500,nothing)
cv2.createTrackbar("Sx",WINDOW_NAME,100,1000,nothing)
cv2.createTrackbar("Sy",WINDOW_NAME,100,1000,nothing)

# cap = cv2.VideoCapture(0)
# ret,img = cap.read()
img = cv2.imread("assets/chess.png")
H,W = img.shape[:2]

c1 = vcam(H=H,W=W)
plane = meshGen(H,W)

plane.Z = plane.X*0 + 1

pts3d = plane.getPlane()


while True:
	# ret, img = cap.read()
	img = cv2.imread("assets/chess.png")
	X = -cv2.getTrackbarPos("X",WINDOW_NAME) + 500
	Y = -cv2.getTrackbarPos("Y",WINDOW_NAME) + 500
	Z = -cv2.getTrackbarPos("Z",WINDOW_NAME)+50
	alpha = cv2.getTrackbarPos("alpha",WINDOW_NAME) - 180
	beta = cv2.getTrackbarPos("beta",WINDOW_NAME) - 180
	gamma = -cv2.getTrackbarPos("gama",WINDOW_NAME) - 180
	c1.focus = cv2.getTrackbarPos("focus",WINDOW_NAME) 
	c1.sx = (cv2.getTrackbarPos("Sx",WINDOW_NAME)+1)/100
	c1.sy = (cv2.getTrackbarPos("Sy",WINDOW_NAME)+1)/100
	dis1 = cv2.getTrackbarPos("distortion_xi",WINDOW_NAME)
	dis2 = cv2.getTrackbarPos("distortion_alpha",WINDOW_NAME)
	c1.dist_xi = dis1
	c1.dist_alpha=dis2

	c1.set_tvec(X,Y,Z)
	c1.set_rvec(alpha,beta,gamma)
	pts2d = c1.project(pts3d)
	map_x,map_y = c1.getMaps(pts2d)
	output = cv2.remap(img,map_x,map_y,interpolation=cv2.INTER_LINEAR)

	M = c1.RT
	print("\n\n############## Camera Matrix ##################")
	print(M)
	cv2.imshow("output",output)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break