import cv2
import matplotlib.pyplot as plt
import dlib
import os
import numpy as np
from skimage.measure import compare_ssim
import math
import dlib
import time

last_pos = []

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainner.yml')

test_dir = "person1"
result_dir = "result/" 
count = 0

def get_detector(choose):
    cascade_path = ""
    if(choose ==  1):
         #人脸检测器（默认）
        cascade_path = "data/face1.xml"
        # detector = cv2.CascadeClassifier(cascade_path)
    elif(choose == 2):
        #人脸检测器（快速Harr）：haarcascade_frontalface_alt2
        cascade_path = "data/haarcascades/haarcascade_frontalface_alt2.xml"
        # return cv2.CascadeClassifier(cascade_path)
    elif(choose == 3):
        cascade_path = "data/haarcascades/haarcascade_upperbody.xml"
        # return cv2.CascadeClassifier(cascade_path)
    elif(choose == 4):
        #use dlib
        detector = dlib.get_frontal_face_detector()
    elif(choose == 5):
        #use dlib cnn
        detector = dlib.cnn_face_detection_model_v1("data/dlib-models-master/mmod_human_face_detector.dat")
    
    if(choose < 4 ):
        detector = cv2.CascadeClassifier(cascade_path)
    
    return detector
def train_test_Haar(file_name):
    choose = 1
    global count
    count += 1
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainner/trainner.yml')
    detector = get_detector(choose)
    #字体
    font = cv2.FONT_HERSHEY_SIMPLEX
    im = cv2.imread(file_name)
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    faces = detector.detectMultiScale(gray, 1.2, 5)

    
    img_id = "Unknown"

    for (x, y, w, h) in faces:
        cv2.rectangle(im, (x - 50, y - 50), (x + w + 50, y + h + 50), (225, 0, 0), 2)
        id, conf = recognizer.predict(gray[y:y + h, x:x + w])
        if conf > 0:
            img_id = "person" + str(id)
        # else:
        #     img_id = "Unknown"
        cv2.putText(im, str(img_id), (x, y + h), font, 0.55, (0, 255, 0), 1)
        break
    cv2.imwrite(result_dir+test_dir+"_"+str(count)+".jpg",im)
    # cv2.destroyAllWindows()
    return img_id


def train_test_Dlib(gray):
    choose = 4
    detector = get_detector(choose)
    faces = detector(gray, 1)
    img_id = "Unknown"
    for (i, rect) in enumerate(faces):
        try:
            x1 = rect.left()
            y1 = rect.top()
            x2 = rect.right()
            y2 = rect.bottom()
            # Rectangle around the face
            # cv2.rectangle(gray, (x1, y1), (x2, y2), (255, 255, 255), 3)
            id, conf = recognizer.predict(gray[y1:y2, x1:x2])
            if conf > 0:
                img_id = "person" + str(id)
            # cv2.putText(gray, str(img_id), (x1, y2), font, 0.55, (0, 255, 0), 1)
        except:
            continue
    # return img_id , ((x1 + x2)/2 , (y1 + y2)/2)
    return img_id


def find_erwei(gray):
    (hight , width ) = gray.shape
    for i in range(0,hight):
        for j in range(0,width):
            if(gray[i,j] < 240):
                gray[i,j] = 0

    cv2.imshow("erwei",gray)
    cv2.waitKey(0)
    _, binary_img = cv2.threshold(gray,20,255,cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 30))
    erosion  = cv2.erode(binary_img, kernel)
    # cv2.imshow("erwei",erosion)
    # cv2.waitKey(0)

    pos = []
    contours, hier = cv2.findContours(erosion,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cidx,cnt in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(cnt)
        if(w == width and h == hight):
            continue
        pos.append([x,y,w,h])
        return [x,y,w,h]
    

def find_people(gray):
    (hight , width ) = gray.shape
    for i in range(0,hight):
        for j in range(0,width):
            if(gray[i,j] < 10):
                gray[i,j] = 255
    _, binary_img = cv2.threshold(gray,40,255,cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 40))
    erosion  = cv2.erode(binary_img, kernel)

    pos = []
    contours, hier = cv2.findContours(erosion,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cidx,cnt in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(cnt)
        if(w == width and h == hight):
            continue
        # print('RECT: x={}, y={}, w={}, h={}'.format(x, y, w, h))
        # cv2.rectangle(gray, pt1=(x, y), pt2=(x+w, y+h),color=(99,99,99), thickness=3)
        # id, conf = recognizer.predict(gray[y:y + h, x:x + w])
        # font = cv2.FONT_HERSHEY_SIMPLEX
        # img_id = "Unknown"
        # if conf > 0:
        #     img_id = "person" + str(id)
        # cv2.putText(gray, str(img_id), (x, y + h), font, 0.55, (0, 255, 0), 1)

        pos.append([x,y,w,h])
        # print(str((x+w/2,y+h/2))+ " : "+img_id +"   conf: " +str(conf) ) 
    # cv2.imshow("erosion1",gray )
    # cv2.waitKey(0)
    return pos

#从所有pos中找出离target  =  [640,480]最近的
def choose_near(pos,choose_pos = [640,480]):
    plane_pos = np.array(choose_pos)
    min_len = 1200.0
    size = [0,0]
    left_up = [0,0]
    for one_pos in pos:
        temp_lu = one_pos[0:2]
        temp_size = one_pos[2:4]
        one_pos = [one_pos[0]+one_pos[2]/2,one_pos[1]+one_pos[3]/2]
        temp_vector = np.array(one_pos)
        temp_len = np.linalg.norm(plane_pos-temp_vector)
        print(temp_len)
        if temp_len < min_len:
            left_up = temp_lu
            choose_pos = one_pos
            min_len = temp_len
            size = temp_size
    return choose_pos ,left_up, size

def get_body(gray):
    # 身体检测器：haarcascade_fullbody
    cascade_path = "haarcascades/haarcascade_fullbody.xml"
    detector = cv2.CascadeClassifier(cascade_path)
    bodys = detector.detectMultiScale(gray, 1.2, 5)
    for (x, y, w, h) in bodys:
        cv2.rectangle(gray, (x, y), (x + w , y + h ), (225, 0, 0), 2)
    cv2.imshow("bodys",gray )
    cv2.waitKey(0)

#比较两个图片的相似性
def compare_image( grayA, grayB):
    # imageA = cv2.imread(path_image1)
    # imageB = cv2.imread(path_image2)
    # grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    # grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
    croppedA = cv2.resize(grayA,(64,64),interpolation=cv2.INTER_CUBIC)
    croppedB = cv2.resize(grayB,(64,64),interpolation=cv2.INTER_CUBIC)
    (score, diff) = compare_ssim(croppedA, croppedB, full=True)
    print("SSIM: {}".format(score))
    return score

#给我图片中心的二维坐标得到我应该前进的角度
def get_angle(target):
    if(target[1] == 480.0):
        target[1] += 0.00001
    angle = math.atan((640.0-target[0])/(480.0 - target[1]))
    vec1 = np.array(target)
    vec2 = np.array([640,480])
    length = np.linalg.norm(vec1-vec2)
    if(target[1] > 480.0):
        angle += 3.1415926
    print("angle = " +str(angle))
    return angle,length


# gray = cv2.imread("sjy.jpg",0)
# start = time.time()
# print(find_erwei(gray))
# end = time.time()
# print(end-start)

# def local_face(gray):
#     (hight , width ) = gray.shape

# print(180.0/3.14*get_angle([0,480]))
# print(180.0/3.14*get_angle([641,480]))
# print(180.0/3.14*get_angle([0,480]))
# print(180.0/3.14*get_angle([1280,480]))
# compare_image = CompareImage()
# compare_image.compare_image("pic/0.jpg", "pic/1.jpg")