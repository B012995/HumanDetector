# -*- coding: utf-8 -*-

'''
Created on 2017/10/18

@author: CSYSBP01
'''

import numpy as np
import cv2
from PIL import ImageGrab
from matplotlib import pyplot

ImageGrab.grab().save("C:\\Users\\CSYSBP01\\Desktop\\desk.png")

ImageGrab.grab(bbox=(100,100,450,450)).save("C:\\Users\\CSYSBP01\\Desktop\\cut.png")

desk=cv2.imread("C:\\Users\\CSYSBP01\\Desktop\\desk.png",0)
cut=cv2.imread("C:\\Users\\CSYSBP01\\Desktop\\cut.png",0)

w,h = cut.shape[::-1]

result = cv2.matchTemplate(desk,cut,cv2.TM_CCOEFF)
min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result)

top_left=max_loc
bottom_right=(top_left[0]+w,top_left[1]+h)
cv2.rectangle(desk,top_left,bottom_right,0,2)

pyplot.imshow(desk)
pyplot.show()