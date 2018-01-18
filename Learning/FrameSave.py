# -*- coding: utf-8 -*-

'''
video2jpg.py.

Usage:
  video2jpg.py [<video source>] [<fps>] [<resize_rate>]
'''

import cv2
import datetime

video_input = cv2.VideoCapture('http://admin:3476C559C42E@192.168.11.4:10226/snapshot.cgi?.mjpeg')

if (video_input.isOpened() == False):
    print("ビデオカメラが見つかりません")
    exit()

fps = int(video_input.get(cv2.CAP_PROP_FPS))
frame_count = 0
save_count = 0
wait = 60

while(True):
    frame_count += 1


    ret, frame = video_input.read()

    if frame_count % (fps * (wait/2)) == 0:
        save_count += 1
        cv2.imshow('frame', frame)

        count_padded = '%05d' % save_count
        time = "{0:%Y%m%d%H%M%S%f}".format(datetime.datetime.now())
        write_file_name = 'C:\\Users\\CSYSBP01\\Desktop\\FrameSave\\' + time + "_" + count_padded + ".jpg"

        cv2.imwrite(write_file_name, frame)

    c = cv2.waitKey(1) & 0xFF
    if c==27: # ESC
        break

video_input.release()
cv2.destroyAllWindows()