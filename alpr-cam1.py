# -*- coding: cp1251 -*-
#Specify device
import os
#os.environ["CUDA_VISIBLE_DEVICES"] = "0"
#os.environ["TF_FORCE_GPU_ALLOW_GROWTH"] = "true"
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # For CPU inference

# Import all necessary libraries.
import numpy as np
import sys
import glob
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import cv2
import copy
from datetime import datetime
import re
import pathlib

# NomeroffNet workdir path
NOMEROFF_NET_DIR = os.path.abspath('../../')
sys.path.append(NOMEROFF_NET_DIR)

from NomeroffNet.YoloV5Detector import Detector

detector = Detector()
detector.load()

from NomeroffNet.BBoxNpPoints import NpPointsCraft, getCvZoneRGB, convertCvZonesRGBtoBGR, reshapePoints

npPointsCraft = NpPointsCraft()
npPointsCraft.load()

from NomeroffNet.OptionsDetector import OptionsDetector
from NomeroffNet.TextDetector import TextDetector

optionsDetector = OptionsDetector()
optionsDetector.load("latest")

# Initialize text detector.
textDetector = TextDetector({

    "ru": {
        "for_regions": ["ru", "eu-ua-fake-lnr", "eu-ua-fake-dnr"],
        "model_path": "latest"
    },
})


DetectedNumber = 'none'


while True:

 # Get image from ip-cam
 CamFrame = '../cam1/img.jpg'
 # Cam IP:PORT
 CamIP = 'rtsp://admin:admin@123.17.13.177:555'
 
 cap2 = cv2.VideoCapture(CamIP) # it can be rtsp or http stream
 ret, frame = cap2.read()
 if cap2.isOpened():
     _,frame = cap2.read()
     cap2.release() #releasing camera immediately after capturing picture
     if _ and frame is not None:
#         cv2.imwrite('../cam1/img.jpg', frame)
         cv2.imwrite(CamFrame, frame)
         print(str(datetime.now().strftime("%d-%m-%Y_%H-%M-%S")) + ': OK Write image from "ip-cam" in file: ' + CamFrame)
 
 CamDir = '../cam1/*'
 imgs = [mpimg.imread(img_path) for img_path in glob.glob(CamDir)]
 
 for img in imgs:
     targetBoxes = detector.detect_bbox(copy.deepcopy(img))
     targetBoxes = targetBoxes
 
     all_points = npPointsCraft.detect(img, targetBoxes)
     all_points = [ps for ps in all_points if len(ps)]
 #    print(all_points)
 
      # cut zones
     toShowZones = [getCvZoneRGB(img, reshapePoints(rect, 1)) for rect in all_points]
     zones = convertCvZonesRGBtoBGR(toShowZones)
     for zone, points in zip(toShowZones, all_points):
         plt.axis("off")
#         plt.imshow(zone)
#         plt.show()
 
     # find standart
     regionIds, countLines = optionsDetector.predict(zones)
     regionNames = optionsDetector.getRegionLabels(regionIds)
#     print(regionNames)
#     print(countLines)
 
     # find text with postprocessing by standart
     textArr = textDetector.predict(zones, regionNames, countLines)
     DetectedNumber = str(textArr)
     #print(DetectedNumber)
     
     # Check for recognition errors and doubles
     NumberCheck=re.findall(r"\D(\d{3})\D", DetectedNumber)
     NumberCheck = str(NumberCheck)
     if NumberCheck != DetectedNumber:
        DetectedNumber = str(NumberCheck)
        chars = set('0123456789,')
        if any((c in chars) for c in DetectedNumber):

            # draw rect and 4 points
            for targetBox, points in zip(targetBoxes, all_points):
                cv2.rectangle(img,
                              (int(targetBox[0]), int(targetBox[1])),
                              (int(targetBox[2]), int(targetBox[3])),
                              (0,120,255),
                              3)
            plt.imshow(img)
       #     plt.show()
       
            CamFolder = '../images/' + str(datetime.now().strftime("%Y-%m-%d")) + '/'
            CurrentDateTime = str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
            ImgPath = CamFolder + CurrentDateTime + '_cam1_' + DetectedNumber + '.jpg'
            
            #Create folder
            pathlib.Path(CamFolder).mkdir(parents=True, exist_ok=True) 
            
            #Save image with detected licence plate and DPI 400
            plt.savefig(ImgPath, bbox_inches='tight', pad_inches=0, dpi=400)
            
            #Clear memory in plt widows
            plt.clf() #close last plt widow
            #plt.close('all') #close all plt widows
            
            print(CurrentDateTime + ': OK Complete detection in: ' + ImgPath)
            
            text_to_append = CurrentDateTime + ';' + '_cam1_' + ';' + DetectedNumber + ';' + ImgPath
            
            #Write data to CSV file
            CSV_file = CamFolder + '_Detected_numbers.csv'            
            def append_new_line(CSV_file, text_to_append):
             # Append given text as a new line at the end of file
             # Open the file in append & read mode ('a+')
             with open(CSV_file, "a+") as file_object:
                 # Move read cursor to the start of file.
                 file_object.seek(0)
                 # If file is not empty then append '\n'
                 data = file_object.read(100)
                 if len(data) > 0:
                     file_object.write('\n')
                 # Append text at the end of file
                 file_object.write(text_to_append)
             
            append_new_line(CSV_file, text_to_append)
        else:
            print(str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + ': Failed to detect numberplate')

     else:
        print(str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + ': No new numbers detected')
        #time.sleep(5 / 1000)   
