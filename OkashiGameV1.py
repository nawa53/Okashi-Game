import cvzone
from cvzone.HandTrackingModule import HandDetector
import cv2
import numpy as np
import os
import random
import time

# Setting camera
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
hf = 720
wf = 1280
cap.set(3, wf)  # set new width
cap.set(4, hf)   # set new height

def create_imgObjects(pathFolderObject):
    global objectPoss, speedObjsX, speedObjsY, \
        imgObjectsFalling, imgObjectsFalling_org, objectPoss_org, ObjectsFallingPoint
    # Create variable "imgObjects" to keep all object images
    # Set initial values to them
    pathListObjectFolder = os.listdir(pathFolderObject)  # folder name of falling objects
    # print(pathListObjectFolder)
    imgObjects = []
    speedObjsX = []
    speedObjsY = []
    objectPoss = []
    points = []
    for folder_name in pathListObjectFolder:
        pathSubFolderObject = f"{pathFolderObject}/{folder_name}"
        # print(pathSubFolderObject)
        pathListObject = os.listdir(pathSubFolderObject)  # list of falling objects in subfolder
        # print(pathListObject)
        for path in pathListObject:
            object_filename = os.path.join(pathSubFolderObject, path)
            # print(object_filename)
            imgObject = cv2.imread(object_filename, cv2.IMREAD_UNCHANGED)
            # print(imgObject.shape)
            if imgObject.shape[0] < 150 or imgObject.shape[0] > 200:
                imgObject = cv2.resize(imgObject, ((imgObject.shape[1] * 150) // imgObject.shape[0], 150))  # (w,h)
            # print(imgObject.shape)
            imgObjects.append(imgObject)
            speedObjsX.append(0)
            speedObjsY.append(0)
            objectPoss.append([0, 2000])
            points.append(int(folder_name))     # point = folder name
            imgObjectsFalling = imgObjects.copy()
            imgObjectsFalling_org = imgObjects.copy()
            objectPoss_org = objectPoss.copy()
            ObjectsFallingPoint = points.copy()
    return imgObjects, points

def random_object(_num_object):
    global img, score, \
        objectPoss, speedObjsX, speedObjsY, points, \
        imgObjectsFalling, imgObjectsFalling_org, objectPoss_org, ObjectsFallingPoint
    for i in range(_num_object):
        if objectPoss[i][1] >= 720-imgObjectsFalling[i].shape[0]:   # object falls to the bottom
            new_idx = random.randint(0, len(imgObjects)-1)
            imgObjectsFalling_org[i] = imgObjects[new_idx]
            scaling_size = random.uniform(0.5, 1)
            imgObjectsFalling[i] = cv2.resize(imgObjectsFalling_org[i], (0, 0), fx=scaling_size, fy=scaling_size)
            hObj, wObj, _ = imgObjectsFalling[i].shape
            speedObjsY[i] = random.randint(15, 20)
            speedObjsX[i] = random.choice([0, speedObjsY[i]//4, speedObjsY[i]//5, -speedObjsY[i]//4, -speedObjsY[i]//5])
            objectPoss[i] = [random.randint(wObj//2, wf - wObj), 0]  # [x,y]
            ObjectsFallingPoint[i] = points[new_idx]

        # moving object
        hObj, wObj, _ = imgObjectsFalling[i].shape
        objectPoss[i][1] += speedObjsY[i]
        objectPoss[i][1] = np.clip(objectPoss[i][1], 10, 720-hObj)
        # objectPoss[i][0] += speedObjsX[i]
        # objectPoss[i][0] = np.clip(objectPoss[i][0], 0, 1280 - wObj)
        img = cvzone.overlayPNG(img, imgObjectsFalling[i], objectPoss[i])

        needle_area = blackBg.copy()
        needle_area[needlePos[1]:needlePos[1] + hN, needlePos[0]:needlePos[0] + wN] = imgNeedle[:, :, 3]
        if hands and needle_area.any() > 0:
            object_area = blackBg.copy()
            object_area[objectPoss[i][1]:objectPoss[i][1] + hObj, objectPoss[i][0]:objectPoss[i][0] + wObj] = imgObjectsFalling[i][:, :, 3]
            intersect_area = cv2.bitwise_and(object_area, needle_area, mask=None)
            if intersect_area.any() == 1:
                objectPoss[i][1] = 2000
                score += ObjectsFallingPoint[i]

def reset():
    global objectPoss, score, status, initialTime, imgObjects, points
    objectPoss = objectPoss_org
    score = 0
    status = "Playing"
    initialTime = time.time()
    imgObjects_S1, points_S1 = create_imgObjects("GameResources/fruit")
    imgObjects = imgObjects_S1
    points = points_S1

def resize2cframe(input_image):  # Resize to camera frame
   hIP, wIP, _ = input_image.shape
   # Resize to camera frame if necessary
   if hIP != hf or wIP != wf:
       input_image = cv2.resize(input_image, (wf, hf))
   return input_image

# Game over image
imgGameover = cv2.imread("GameResources/game_over.jpg")
imgGameover = resize2cframe(imgGameover)

# Time's up image
imgTimesup = cv2.imread("GameResources/time-s-up.png")
imgTimesup = resize2cframe(imgTimesup)

# Big win image
imgGamewin = cv2.imread("GameResources/game_win.jpg")
imgGamewin = resize2cframe(imgGamewin)

# Background images
imgBackground1 = cv2.imread("GameResources/background/b1.png")
imgBackground1 = resize2cframe(imgBackground1)
imgBackground2 = cv2.imread("GameResources/background/b2.png")
imgBackground2 = resize2cframe(imgBackground2)
imgBackground3 = cv2.imread("GameResources/background/b3.png")
imgBackground3 = resize2cframe(imgBackground3)

# Gif animation
cap_firework = cv2.VideoCapture('GameResources/firework1.gif')

# Needle image
imgNeedle = cv2.imread("GameResources/needle/cat1.png", cv2.IMREAD_UNCHANGED)
hN = int(0.2*hf)
imgNeedle = cv2.resize(imgNeedle, ((imgNeedle.shape[1]*hN)//imgNeedle.shape[0], hN))
hN, wN, _ = imgNeedle.shape

# Initial values
img_ratio = 0.2  # transparent level of camera frame (player)
score = 0
needlePos = [0, 0]
status = "Playing"
num_object = 2
blackBg = np.zeros([hf, wf], dtype=np.uint8)
timeLimit = 20

detector = HandDetector(detectionCon=0.8, maxHands=1)
initialTime = time.time()


imgObjects_S2, points_S2 = create_imgObjects("GameResources/cartoon")
imgObjects_S1, points_S1 = create_imgObjects("GameResources/okashi")

while True:
    if status == "Playing":
        # Get image frame
        success, img = cap.read()
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, draw=True, flipType=True)

        if hands:
            hand = hands[0]
            HandLandMarkList = hand["lmList"]
            fingertip_x, fingertip_y = HandLandMarkList[8][0:2]
            needlePos = [fingertip_x - int(wN * 0.5), fingertip_y - int(hN * 0.8)]
            needlePos[0] = np.clip(needlePos[0], 0, wf-wN)
            needlePos[1] = np.clip(needlePos[1], 0, hf-hN)
            img = cvzone.overlayPNG(img, imgNeedle, needlePos)
            img = cv2.circle(img, (fingertip_x, fingertip_y), 10, (255, 0, 255), -1)  # center_coordinates, radius, color, thickness

    cv2.imshow("Okashi Game", img)
    key = cv2.waitKey(1)
    if key == 27:  # Esc
        break
    elif key == ord('r'):
        reset()