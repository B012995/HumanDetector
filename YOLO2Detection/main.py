from darkflow.net.build import TFNet
import cv2
import os
# import matplotlib.pyplot as plt



if __name__ == '__main__':

    os.chdir("/Users/nttcom/darkflow")
    # options = {"model": "/Users/nttcom/darkflow/cfg/yolo.cfg", "load": "/Users/nttcom/darkflow/yolo.weights", "threshold": 0.1}
    options = {"model": "cfg/yolo.cfg", "load": "yolo.weights", "threshold": 0.1}

    tfnet = TFNet(options)

    src = cv2.imread("/Users/nttcom/Desktop/FrameSave/24540.jpg")

    result = tfnet.return_predict(src)

    for key in result:
        label = key["label"]
#         if(label != "person"):
#             break
        tlx = key["topleft"]["x"]
        tly = key["topleft"]["y"]
        brx = key["bottomright"]["x"]
        bry = key["bottomright"]["y"]
        cv2.rectangle(src, (tlx,tly), (brx,bry), (0,0,255), 2, 4)

        cv2.putText(src, label, (tlx,tly), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0))

    cv2.imshow("result",src)
    cv2.waitKey()

    print(result)