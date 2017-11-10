# -*- coding: utf-8 -*-

'''
Created on 2017/10/11

@author: CSYSBP01
'''

import numpy as np
import cv2

#cap = cv2.VideoCapture('D:\\Work_Documents\\sandbox\\OpenCV\\with_EEN\\viaVLC\\EN-CDUM-002a+2016-08-29+14-38-40.mp4') #Open video file
cap = cv2.VideoCapture('http://admin:3476C559C42E@192.168.11.2:10226/snapshot.cgi?.mjpeg')
#cap = cv2.VideoCapture('http://127.0.0.1:8080')

fps = 15 #int(cap.get(5)+4)
print('Current FPS is ' + str(fps))
#cv2.ocl.setUseOpenCL(False)
fgbg = cv2.createBackgroundSubtractorKNN(detectShadows = True) # 背景差分の取得にk近傍法(kNN法)を用いる

# initialize var and windows
itr = 0
count = 0
font = cv2.FONT_HERSHEY_SIMPLEX
old_center = np.empty((0,2), float)
'''
cv2.namedWindow("Frame", cv2.WINDOW_KEEPRATIO | cv2.WINDOW_NORMAL)
cv2.namedWindow("Background Substraction", cv2.WINDOW_KEEPRATIO | cv2.WINDOW_NORMAL)
cv2.namedWindow("Contours", cv2.WINDOW_KEEPRATIO | cv2.WINDOW_NORMAL)
'''


# define functions
def padding_position(x, y, w, h, p):    # 矩形の上下左右にpだけ広げる
    return x - p, y - p, w + p * 2, h + p * 2

# find a nearest neighbour point
def serchNN(p0, ps):
    L = np.array([])
    for i in range(ps.shape[0]):
        L = np.append(L,np.linalg.norm(ps[i]-p0))
    return ps[np.argmin(L)]

'''
2つのベクトルが交差しているかを判定する。
2つのベクトルが交差している場合、互いに自身のベクトルから見てもう一つのベクトルの両端は左右に存在することになる。
つまり、自身のベクトルと、自身の始点からもう一つのベクトルの両端へのベクトルの外積は必ず正・負になり、その積は必ず負になる。
両方のベクトルでその計算をし、両方負になれば2つのベクトルは交差していると言える。
'''
def intersectDirection(ap1, ap2, bp1, bp2):
    cross1 = np.cross(ap2 - ap1, bp1 - ap1)
    cross2 = np.cross(ap2 - ap1, bp2 - ap1)
    calc1 = cross1 * cross2
    if (calc1 < 0):
        calc2 = np.cross(bp2 - bp1, ap1 - bp1) * np.cross(bp2 - bp1, ap2 - bp1)
        if (calc2 < 0):
            return 1 if cross1 < 0 else -1  #交差した場合、左から右に通過した場合は1、右から左に通過した場合は-1を返す。
    return 0

# apply convexHull to the contour
def convHull(cnt):
    epsilon = 0.1*cv2.arcLength(cnt, True)  # 領域を囲む周囲長を計算
    approx = cv2.approxPolyDP(cnt, epsilon, True)   # 領域の形状に近似した形状を取得、epsilonが小さければ小さいほど近似の精度が高くなる
    hull = cv2.convexHull(cnt, returnPoints = True) # 凸包(図形を紐で囲い締め上げたときに取る形状)を取得
    return hull

# detect a centroid from a coutour
def centroidPL(cnt):
    M = cv2.moments(cnt)    # モーメントを取得
    cx = int(M['m10']/M['m00']) # モーメントから重心のx軸を計算
    cy = int(M['m01']/M['m00']) # モーメントから重心のy軸を計算
    return cx,cy

# display 1st frame and set counting line
ret, img = cap.read()
img = cv2.putText(img, 'Please draw a line with drug the mouse.', (img.shape[1]//2-300, img.shape[0]//2), font, 1, (0,0,255), 2, cv2.LINE_AA)
img = cv2.putText(img, 'Finish the draw, press ESC. \n Retry, press "r".', (img.shape[1]//2-300, img.shape[0]//2+40), font, 1, (0,0,255), 2, cv2.LINE_AA)
img = cv2.putText(img, 'Retry, press "r".', (img.shape[1]//2-300, img.shape[0]//2+80), font, 1, (0,0,255), 2, cv2.LINE_AA)
img = cv2.resize(img, (img.shape[1]//2, img.shape[0]//2))
imgr = img.copy()   # 参照型のため同じオブジェクトを参照しないようコピー
sx,sy = -1,-1
ex,ey = -1,-1

def draw_line(event,x,y,flags,param):   # ドラッグの始点から終点に直線を引く
    global sx,sy,ex,ey

    if event == cv2.EVENT_LBUTTONDOWN:
        sx,sy = x,y

    elif event == cv2.EVENT_LBUTTONUP:
        cv2.line(img,(sx,sy),(x,y),(255,0,0), 2)
        ex,ey = x,y

cv2.namedWindow('Draw_Line')    # 名前をつけたウィンドウを生成
cv2.setMouseCallback('Draw_Line',draw_line) # 画像(Draw_Lineウィンドウ)にマウスイベントを設定

while(1):
    cv2.imshow('Draw_Line',img)
    k = cv2.waitKey(20) & 0xFF  # 入力キーのビットの論理積をとることでASCIIコードに変換？
    if k == 27: # escキーが押下された場合
        break
    elif k == ord('r'):
        img = imgr.copy()
        continue

cv2.destroyAllWindows()

# initialize line
lp0 = (sx, sy)
lp1 = (ex, ey)
nlp0 = np.array([lp0[0], lp0[1]], float)
nlp1 = np.array([lp1[0], lp1[1]], float)

while(cap.isOpened()):
    try:
        ret, o_frame = cap.read() #read a frame
        frame = cv2.resize(o_frame, (o_frame.shape[1]//2, o_frame.shape[0]//2))

        #Use the substractor
        fgmask = fgbg.apply(frame) #現在のシーンをkNN法でグレースケール化する？
        fgmask_o = fgmask.copy()

        fgmask = cv2.threshold(fgmask, 244, 255, cv2.THRESH_BINARY)[1]  #グレースケール化された画像を2値化する？
#        kernel = np.ones((5,5), np.uint8)
#        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_CLOSE, kernel)
        # cv2.dilate(入力画像, カーネル, 繰り返し回数) 画像のモルフォロジー変換(膨張処理)
        fgmask = cv2.dilate(fgmask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3)), iterations = 2)    # 2値化された画像の白い箇所を円形カーネルで2回膨張(Dilation)させる?

        # cv2.findContours(入力画像, 抽出モード, 近似法) 画像の輪郭抽出
        im2, contours, hierarchy = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # 抽出モードを最も外側の輪郭のみに設定し、簡略化した頂点数で囲う

        # initialize var iteration
        new_center = np.empty((0,2), float) # 配列の生成速度が若干高速になることがあるため、値を0や1で初期化する必要のない場合は、np.emptyを使う

        for c in contours:

            if (itr % fps == 0):
                continue

            # calc the area
            cArea = cv2.contourArea(c)  # 領域が占める面積を計算
            if cArea < 300: # if 1280x960 set to 50000, 640x480 set to 12500 面積が小さすぎたら処理をスキップ
                continue

            # apply the convex hull
            c = convHull(c) # 領域の凸包を取得

            # rectangle area
            x, y, w, h = cv2.boundingRect(c)    # 領域の矩形の左上のポイントと幅、高さを取得
            x, y, w, h = padding_position(x, y, w, h, 5)    # 矩形の上下左右に5だけ広げる

            # center point
            cx, cy = centroidPL(c)  # 領域の重心点を取得
            new_point = np.array([cx, cy], float)
            new_center = np.append(new_center, np.array([[cx, cy]]), axis=0)    # 行方向に重心点を追加

            if (old_center.size > 1):
                #print cArea and new center point
                print('Loop: ' + str(itr) + '   Coutours #: ' + str(len(contours)))
                print('New Center :' + str(cx) + ',' + str(cy))
                #print 'New Center :' + str(new_center)

                # calicurate nearest old center point
                old_point_t = serchNN(new_point, old_center)

                # check the old center point in the counding box
                if (cv2.pointPolygonTest(c, (old_point_t[0], old_point_t[1]), True) > 0):
                    old_point = old_point_t
                    print('Old Center :' + str(int(old_point[0])) + ',' + str(int(old_point[1])))

                    # put line between old_center to new_center
                    cv2.line(frame, (int(old_point[0]), int(old_point[1])), (cx, cy), (0,0,255), 2)

                    # cross line check
                    direction = intersectDirection(nlp0, nlp1, old_point, new_point)
                    if (direction == 1):
                        print('Enter!')
                        count += 1
                    elif (direction == -1):
                        print('Exit!')
                        count -= 1

            # put floating text
            cv2.putText(frame, 'CA:' + str(cArea)[0:-2] , (x+10, y+20), font, 0.5, (255,255,255), 1, cv2.LINE_AA)

            # draw center
            cv2.circle(frame,(cx,cy),5,(0,0,255),-1)

            # draw rectangle or contour
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)  #rectangle contour
#            cv2.drawContours(frame, [c], 0, (0,255,0), 2)
#            cv2.polylines(frame, [c], True, (0,255,0), 2)

        # put fixed text, line and show images
        cv2.putText(frame, 'Count:' + str(count), ((o_frame.shape[1]//6), 30), font, 1, (255,255,255), 1, cv2.LINE_AA)
        cv2.line(frame, (lp0), (lp1), (255,0,0), 2)
        cv2.imshow('Frame',frame)
        cv2.imshow('Background Substraction',fgmask_o)
        cv2.imshow('Contours',fgmask)

        # increase var number and renew center array
        old_center = new_center
        itr += 1

    except:
        #if there are no more frames to show...
        print('EOF')
        break

    #Abort and exit with 'Q' or ESC
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release() #release video file
cv2.destroyAllWindows() #close all openCV windows