# -*- coding: utf-8 -*-

'''
Created on 2017/10/18

@author: CSYSBP01
'''

import numpy as np
import cv2

detect_state = np.zeros(120, dtype = np.int)
detect_state_point = 0

def detectedo(detect_cnt):
    global detect_state_point
    global detect_state
    detect_state[detect_state_point] = detect_cnt

    if detect_state_point == 119:
        detect_state_point = 0
    else:
        detect_state_point = detect_state_point + 1
    b = detect_state.sum()
    if 60 <= b:
        return True
    else:
        return False
    return None

for a in range(100):
    de = detectedo(0)
    print(de)