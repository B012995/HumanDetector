import sys
import numpy as np
import cv2
import glob

import cvmouse
import qtaddtag


if __name__ == "__main__":
#     app = qtaddtag.QApplication(sys.argv)
#     qtwin = qtaddtag.QtAddTag()
#     sys.exit(app.exec_())
#     source_dir = "C:/Users/CSYSBP01/Desktop/FrameSave/"
#     save_dir = "C:/Users/CSYSBP01/Desktop/DataSet/"
    source_dir = "/Users/nttcom/Desktop/FrameSave/"
    save_dir = "/Users/nttcom/Desktop/DataSet/"

    file_list = sorted(glob.glob(source_dir + "*"))

    win_pos = (300,300)

    for filename in file_list:
#         print(filename)
#         original_img = cv2.imread(filename, 1)
#         cv2.imshow('image', original_img)
        cvm = cvmouse.CVMousePaint(filename, save_dir, win_pos)
        win_pos = cvm.win_pos   # ウィンドウ位置を引き継ぐ。

#         cv2.waitKey(0)
#         cv2.destroyAllWindows()