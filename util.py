import vrep
import time
import ctypes
import numpy as np
import math
import pdb
import cv2
import array
import QR_finder
from PIL import Image
import matplotlib.pyplot as plt
    
def save_pic(vision_name,clientID):
    if clientID!=-1:
        try:
            err, camera1 = vrep.simxGetObjectHandle(clientID, vision_name,
                                                        vrep.simx_opmode_blocking )
            # res,resolution,image=vrep.simxGetVisionSensorImage(clientID,camera1,0,vrep.simx_opmode_remove)
            res,resolution,image=vrep.simxGetVisionSensorImage(clientID,camera1,0,vrep.simx_opmode_streaming)
            print("getting pic...")
            while (vrep.simxGetConnectionId(clientID)!=-1):
                res,resolution,image=vrep.simxGetVisionSensorImage(clientID,camera1,0,vrep.simx_opmode_buffer)
                if res==vrep.simx_return_ok:
                    img = np.array(image, dtype = np.uint8)
                    img.resize([resolution[1],resolution[0],3])
                    img = cv2.flip(img,0)
                    print('ok')
                    # cv2.imshow("name",img)
                    # cv2.waitKey(0)
                    return img
                # time.sleep(1)
        except:
            return None


def drawRect(img, pt1, pt2, pt3, pt4, color, lineWidth):
    cv2.line(img, tuple(pt1), tuple(pt2), color, lineWidth)
    cv2.line(img, tuple(pt2), tuple(pt3), color, lineWidth)
    cv2.line(img, tuple(pt3), tuple(pt4), color, lineWidth)
    cv2.line(img, tuple(pt1), tuple(pt4), color, lineWidth)
    cv2.imshow("img",img)
    cv2.waitKey(0)

def find_target(img):
    img_hsv = cv2.cvtColor(np.asarray(img),cv2.COLOR_RGB2HSV)
    img = np.asarray(img)
    lower_red = np.array([0, 43, 46])
    upper_red = np.array([10, 255, 255])
    mask_red = cv2.inRange(img_hsv, lower_red, upper_red)
    cnts = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    # lower_red = np.array([156, 43, 46])
    # upper_red = np.array([180, 255, 255])
    # mask_red = cv2.inRange(img_hsv, lower_red, upper_red)
    # cnts += cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    if len(cnts) > 0: 
        c = max(cnts, key = cv2.contourArea)
        min_rect = cv2.minAreaRect(c)
        center = min_rect[0]
        w = min_rect[1][0]
        l = min_rect[1][1]
        if l < w:
            l,w = w,l
        return center,[l,w]
    else:
        return None,None


def find_landing_platform(image):
    image = np.asarray(image)

    # 由于霍夫圆检测对噪声敏感，这里用 均值偏移滤波 移除噪声
    # pyrMeanShiftFiltering(src, sp, sr[, dst[, maxLevel[, termcrit]]]) -> dst
    # 1 data 2 空间窗半径 3 色彩窗半径
    dst = cv2.pyrMeanShiftFiltering(image, 10, 100)
    #kernel = np.ones([5, 5], np.float32)/25   #除以25是防止数值溢出 
    #dst = cv.filter2D(image, -1, kernel)
    gaussian_blur = cv2.GaussianBlur(dst,(3,3),0) # 该算法对噪声敏感，必须降噪
    # cv2.imshow('0', gaussian_blur)
    cimage = cv2.cvtColor(gaussian_blur, cv2.COLOR_BGR2GRAY)  
    # cv2.imshow('1', cimage)
    edges = cv2.Canny(cimage, 70, 220)
    # cv2.imshow('2', edges)

    circles = cv2.HoughCircles(cimage, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=0, maxRadius=0)
    # if circles is None:
    #     return None,None
    circles = np.uint16(np.around(circles)) # 把类型换成整数
    max = 0
    x = -1
    y = -1
    for i in circles[0, :]: # return (a,b,r)
        cv2.circle(image, (i[0], i[1]), i[2], (0, 0, 255), 2)
        cv2.circle(image, (i[0], i[1]), 2, (255, 0, 255), 2) # 画出小圆心
        if (i[2] > max):
            max = i[2]
            x = i[0]
            y = i[1]
    # cv2.imshow("Result", image)
    # cv2.waitKey(0)
    # print(i[0],[1])
    return x,y

#err = -2:a corner detected
#err = -1:not found
#err = 0:QR found
def find_QR(image):
    image = np.asarray(image)
    image=QR_finder.reshape_image(image)
    image,contours,hierachy=QR_finder.detecte(image)
    err,box = QR_finder.find(image,contours,np.squeeze(hierachy))
    if box is None:
        center = None
    else:
        center = [(box[0][0] + box[1][0]) / 2, (box[1][1] + box[2][1]) / 2]
    return err,center,box


    # pix = img.load()
    # width = img.size[0]
    # height = img.size[1]
    # maxx=0
    # minx=100000
    # maxy=0
    # miny=100000
    # maxd=0
    # for x in range(width):
    #     maxy2 = 0
    #     miny2 = 100000
    #     for y in range(height):
    #         r, g, b = pix[x, y]
    #         if r <= 0 and g <= 0 and b <= 0:
    #                 maxx = max(maxx,x)
    #                 minx = min(minx,x)
    #                 maxy2 = max(maxy2,y)
    #                 miny2 = min(miny2,y)
    #     if maxy2 - miny2 < 10000 and maxy2 - miny2 > maxd :
    #         maxd = maxy2 - miny2
    #         maxy = maxy2
    #         miny = miny2
    # print(minx,maxx,miny,maxy)
    # if (maxx + minx) / 2 > width or  (maxy + miny) / 2 > height:
    #     return None
    # else:
    #     return [(maxx + minx) / 2, (maxy + miny) / 2]

def calculate_height(delta_t):
    return 1280.0*0.12/delta_t/2.0/math.tan(42.5/180.0*math.pi)