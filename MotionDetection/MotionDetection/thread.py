# -*- coding: utf-8 -*-
'''
Created on 2017/11/02

@author: CSYSBP01
'''
import threading
import time
import numpy as np
import cv2
import psycopg2

class CameraThread(threading.Thread):
    def __init__(self):
        self.now_count = 0
        self.detect_state = np.zeros(60, dtype = np.int)
        self.detect_state_point = 0
        super(CameraThread, self).__init__()

    def padding_position(self, x, y, w, h, p):    # 矩形の上下左右にpだけ広げる
        return x - p, y - p, w + p * 2, h + p * 2

    # find a nearest neighbour point
    def serchNN(self, p0, ps):
        L = np.array([])
        for i in range(ps.shape[0]):
            L = np.append(L,np.linalg.norm(ps[i]-p0))
        return ps[np.argmin(L)]


    # 2つのベクトルが交差しているかを判定する。
    # 2つのベクトルが交差している場合、互いに自身のベクトルから見てもう一つのベクトルの両端は左右に存在することになる。
    # つまり、自身のベクトルと、自身の始点からもう一つのベクトルの両端へのベクトルの外積は必ず正・負になり、その積は必ず負になる。
    # 両方のベクトルでその計算をし、両方負になれば2つのベクトルは交差していると言える。
    def intersect_direction(self, ap1, ap2, bp1, bp2):
        cross1 = np.cross(ap2 - ap1, bp1 - ap1)
        cross2 = np.cross(ap2 - ap1, bp2 - ap1)
        calc1 = cross1 * cross2
        if (calc1 < 0):
            calc2 = np.cross(bp2 - bp1, ap1 - bp1) * np.cross(bp2 - bp1, ap2 - bp1)
            if (calc2 < 0):
                return 1 if cross1 < 0 else -1  #交差した場合、左から右に通過した場合は1、右から左に通過した場合は-1を返す。
        return 0

    # 直前のフレームでの動体検知状態を保持しておき、現在動体が存在するかどうか決定する。
    # 要はチャタリング防止用関数。
    def detected(self, detect_cnt):
        print(self.detect_state_point)
        self.detect_state[self.detect_state_point] = detect_cnt
        print(self.detect_state_point)
        if self.detect_state_point != self.detect_state.shape[0] - 1:
            self.detect_state_point = self.detect_state_point + 1
        else:
            self.detect_state_point = 0

        if self.detect_state.shape[0] // 2 <= self.detect_state.sum():
            return True
        else:
            return False

    # apply convexHull to the contour
    def convHull(self, cnt):
        epsilon = 0.1*cv2.arcLength(cnt, True)  # 領域を囲む周囲長を計算
        approx = cv2.approxPolyDP(cnt, epsilon, True)   # 領域の形状に近似した形状を取得、epsilonが小さければ小さいほど近似の精度が高くなる
        hull = cv2.convexHull(cnt, returnPoints = True) # 凸包(図形を紐で囲い締め上げたときに取る形状)を取得
        return hull

    # detect a centroid from a coutour
    def centroidPL(self, cnt):
        M = cv2.moments(cnt)    # モーメントを取得
        cx = int(M['m10']/M['m00']) # モーメントから重心のx軸を計算
        cy = int(M['m01']/M['m00']) # モーメントから重心のy軸を計算
        return cx,cy

    def run(self):

        #cap = cv2.VideoCapture('D:\\Work_Documents\\sandbox\\OpenCV\\with_EEN\\viaVLC\\EN-CDUM-002a+2016-08-29+14-38-40.mp4') #Open video file
        cap = cv2.VideoCapture('http://admin:3476C559C42E@192.168.11.2:10226/snapshot.cgi?.mjpeg')
        #cap = cv2.VideoCapture('http://127.0.0.1:8080')

        fps = 15 #int(cap.get(5)+4)
        print('Current FPS is ' + str(fps))
        #cv2.ocl.setUseOpenCL(False)
        fgbg = cv2.createBackgroundSubtractorKNN(detectShadows = True) # 背景差分の取得にk近傍法(kNN法)を用いる

        # initialize var and windows
        itr = 0
        font = cv2.FONT_HERSHEY_SIMPLEX
        old_center = np.empty((0,2), float)
        count = 0
        '''
        cv2.namedWindow("Frame", cv2.WINDOW_KEEPRATIO | cv2.WINDOW_NORMAL)
        cv2.namedWindow("Background Substraction", cv2.WINDOW_KEEPRATIO | cv2.WINDOW_NORMAL)
        cv2.namedWindow("Contours", cv2.WINDOW_KEEPRATIO | cv2.WINDOW_NORMAL)
        '''


        # define functions


        # display 1st frame and set counting line
        ret, img = cap.read()
        img = cv2.resize(img, (img.shape[1]//2, img.shape[0]//2))
        imgr = img.copy()   # 参照型のため同じオブジェクトを参照しないようコピー
        sx,sy = -1,-1
        ex,ey = -1,-1



        # initialize line
        lp0 = (sx, sy)
        lp1 = (ex, ey)
        nlp0 = np.array([lp0[0], lp0[1]], float)
        nlp1 = np.array([lp1[0], lp1[1]], float)


        while(cap.isOpened()):
            count = 0
            try:
                ret, o_frame = cap.read() #read a frame
                frame = cv2.resize(o_frame, (o_frame.shape[1]//2, o_frame.shape[0]//2))

                #Use the substractor
                fgmask = fgbg.apply(frame) #現在のシーンをkNN法でグレースケール化する？
                fgmask_o = fgmask.copy()

                fgmask = cv2.threshold(fgmask, 244, 255, cv2.THRESH_BINARY)[1]  #グレースケール化された画像を2値化する？
                # kernel = np.ones((5,5), np.uint8)
                # fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_CLOSE, kernel)
                # cv2.dilate(入力画像, カーネル, 繰り返し回数) 画像のモルフォロジー変換(膨張処理)
                fgmask = cv2.dilate(fgmask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3)), iterations = 2)    # 2値化された画像の白い箇所を円形カーネルで2回膨張(Dilation)させる?

                # cv2.findContours(入力画像, 抽出モード, 近似法) 画像の輪郭抽出
                im2, contours, hierarchy = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # 抽出モードを最も外側の輪郭のみに設定し、簡略化した頂点数で囲う

                # initialize var iteration
                new_center = np.empty((0,2), float) # 配列の生成速度が若干高速になることがあるため、値を0や1で初期化する必要のない場合は、np.emptyを使う

                for c in contours:

                    if (itr % fps == 0):    #これ15フレームに一回の処理じゃなくて、15回の動画読み込みに1回処理スキップしてるだけじゃね？
                        continue

                    # calc the area
                    cArea = cv2.contourArea(c)  # 領域が占める面積を計算
                    if cArea < 1000: # if 1280x960 set to 50000, 640x480 set to 12500 面積が小さすぎたら処理をスキップ
                        continue

                    # apply the convex hull
                    c = self.convHull(c) # 領域の凸包を取得

                    # rectangle area
                    x, y, w, h = cv2.boundingRect(c)    # 領域の矩形の左上のポイントと幅、高さを取得
                    x, y, w, h = self.padding_position(x, y, w, h, 5)    # 矩形の上下左右に5だけ広げる

                    # center point
                    cx, cy = self.centroidPL(c)  # 領域の重心点を取得
                    new_point = np.array([cx, cy], float)
                    new_center = np.append(new_center, np.array([[cx, cy]]), axis=0)    # 行方向に重心点を追加

                    if (old_center.size > 1):
                        #print cArea and new center point
                        print('Loop: ' + str(itr) + '   Coutours #: ' + str(len(contours)))
                        print('New Center :' + str(cx) + ',' + str(cy))
                        #print 'New Center :' + str(new_center)

                        # calicurate nearest old center point
                        old_point_t = self.serchNN(new_point, old_center)

                        # check the old center point in the counding box
                        if (cv2.pointPolygonTest(c, (old_point_t[0], old_point_t[1]), True) > 0):
                            old_point = old_point_t
                            print('Old Center :' + str(int(old_point[0])) + ',' + str(int(old_point[1])))

                            # put line between old_center to new_center
                            cv2.line(frame, (int(old_point[0]), int(old_point[1])), (cx, cy), (0,0,255), 2)

                            count = 1

                    # put floating text
                    cv2.putText(frame, 'CA:' + str(cArea)[0:-2] , (x+10, y+20), font, 0.5, (255,255,255), 1, cv2.LINE_AA)

                    # draw center
                    cv2.circle(frame,(cx,cy),5,(0,0,255),-1)

                    # draw rectangle or contour
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)  #rectangle contour
                    # cv2.drawContours(frame, [c], 0, (0,255,0), 2)
                    # cv2.polylines(frame, [c], True, (0,255,0), 2)

                # put fixed text, line and show images
                if self.detected(count) == True:
                    cv2.putText(frame, 'Detect!', ((o_frame.shape[1]//6), 30), font, 1, (255,255,255), 1, cv2.LINE_AA)
                    self.now_count = 1
                else:
                    self.now_count = 0
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

class WriteThread(threading.Thread):
    def __init__(self, interval):
        self.c = CameraThread()
        self.c.start()
        self.connection = psycopg2.connect("host=127.0.0.1 port=5432 dbname=detection user=postgres password=sysadmin")
        self.cur = self.connection.cursor()
        super(WriteThread, self).__init__()
        self.interval = interval
        self.lock = threading.Lock()
        self.bStop = False

    def run(self):
        while True:
            with self.lock:
                if self.bStop:
                    self.c.stop()
                    return
            self.cur.execute("insert into api_count (cnt, created_at) values (%s, current_timestamp)",(self.c.now_count,))
            self.connection.commit()
            time.sleep(self.interval)