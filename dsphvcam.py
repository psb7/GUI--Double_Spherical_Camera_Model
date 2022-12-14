import cv2
import numpy as np
import math


class DSCM:

	def __init__(self,H=400,W=400):
		"""
		H : Desired height of the frame of output video
		W : Desired width of the frame of output
		"""
		self.H = H
		self.W = W
		self.ox = W//2
		self.oy = H//2
		self.alpha = math.radians(0)
		self.beta =  math.radians(0)
		self.gamma = math.radians(0)
		self.Tx = 0
		self.Ty = 0
		self.Tz = 0
		self.K = 0
		self.R = 0
		self.sh = 0 # Shere factor
		self.P = 0
		self.dist_alpha=0 # alpha
		self.dist_xi = 0
		self.focus = 100 # Focal length of camera in mm
		self.sx = 1 # Effective size of a pixel in mm
		self.sy = 1 # Effective size of a pixel in mm
		self.set_tvec(0,0,-self.focus)
		self.update_M()

	def update_M(self):
		# Matrix for converting the 2D matrix to 3D matrix
		Rx = np.array([[1, 0, 0], [0, math.cos(self.alpha), -math.sin(self.alpha)], [0, math.sin(self.alpha), math.cos(self.alpha)]])
		Ry = np.array([[math.cos(self.beta), 0, -math.sin(self.beta)], [0, 1, 0], [math.sin(self.beta), 0, math.cos(self.beta)]])
		Rz = np.array([[math.cos(self.gamma), -math.sin(self.gamma), 0], [math.sin(self.gamma), math.cos(self.gamma), 0], [0, 0, 1]])
		self.R = np.matmul(Rx, np.matmul(Ry, Rz))
		self.K = np.array([[self.focus/self.sx,self.sh,self.ox],[0,self.focus/self.sy,self.oy],[0,0,1]])
		self.M1 = np.array([[1,0,0,-self.Tx],[0,1,0,-self.Ty],[0,0,1,-self.Tz]])
		self.RT = np.matmul(self.R,self.M1)

	def project(self,src):
		self.update_M()
		pts2d = np.matmul(self.RT,src)
		print(pts2d[0,:])

		try:
			x_1 = pts2d[0,:]*1.0/(pts2d[2,:]+0.0000000001)
			y_1 = pts2d[1,:]*1.0/(pts2d[2,:]+0.0000000001)
			r= np.sqrt(x_1**2+y_1**2)
			mz_n=(1-((self.dist_alpha**2)*(r**2)))
			mz_d=(self.dist_alpha)*(np.sqrt(1-((2*self.dist_alpha-1)*r**2)))+1-self.dist_alpha
			mz=mz_n/mz_d
			multiple= ((mz*self.dist_xi)+np.sqrt(mz**2+((1-self.dist_xi**2)*(r**2))))/(mz**2+r**2)
			x_2 = x_1 * multiple
			y_2 = y_1 * multiple
			z_2= multiple - self.dist_xi
			x_2= x_2/z_2
			y_2= y_2/z_2
			x = self.K[0,0]*x_2 + self.K[0,2]
			y = self.K[1,1]*y_2 + self.K[1,2]

		except:
			print("Division by zero!")
			x = pts2d[0,:]*0
			y = pts2d[1,:]*0

		return np.concatenate(([x],[y]))

	def set_tvec(self,x,y,z):
		self.Tx = x
		self.Ty = y
		self.Tz = z
		self.update_M()

	def set_rvec(self,alpha,beta,gamma):
		self.alpha = (alpha/180.0)*np.pi
		self.beta = (beta/180.0)*np.pi
		self.gamma = (gamma/180.0)*np.pi
		self.update_M()

	def renderMesh(self,src):
		"""
		Renders the mesh grid points to get better visual understanding
		"""
		self.update_M()
		pts = self.project(src)
		canvas = np.zeros((self.H,self.W,3),dtype=np.uint8)
		pts = (pts.T).reshape(-1,1,2).astype(np.int32)
		cv2.drawContours(canvas,pts,-1,(0,255,0),3)
		return canvas

	def applyMesh(self,img,meshPts):
		pts1,pts2 = np.split(self.project(meshPts),2)
		x = pts1.reshape(self.H,self.W)
		y = pts2.reshape(self.H,self.W)
		return cv2.remap(img,x.astype(np.float32),y.astype(np.float32),interpolation=cv2.INTER_LINEAR)

	def getMaps(self,pts2d):
		pts1,pts2 = np.split(pts2d,2)
		x = pts1.reshape(self.H,self.W)
		y = pts2.reshape(self.H,self.W)

		return x.astype(np.float32),y.astype(np.float32)


class meshGen:

	def __init__(self,H,W):

		self.H = H
		self.W = W

		x = np.linspace(-self.W/2, self.W/2, self.W)
		y = np.linspace(-self.H/2, self.H/2, self.H)

		xv,yv = np.meshgrid(x,y)

		self.X = xv.reshape(-1,1)
		self.Y = yv.reshape(-1,1)
		self.Z = self.X*0+1 # The mesh will be located on Z = 1 plane

	def getPlane(self):

		return np.concatenate(([self.X],[self.Y],[self.Z],[self.X*0+1]))[:,:,0]
