# OpenCVのマウスイベントを扱うためのクラス

import sys
import cv2
import numpy as np
import qtaddtag
import glob
import datetime

class CVMouseEvent:
    def __init__(self, press_func=None, drag_func=None, release_func=None):
        self._press_func = press_func
        self._drag_func = drag_func
        self._release_func = release_func

        self._is_drag = False
        self.press_point = (0,0)
        self.drag_point = (0,0)
        self.release_point = (0,0)

    # Callback登録関数
    def setCallBack(self, win_name):
        cv2.setMouseCallback(win_name, self._callBack)

    def _doEvent(self, event_func):
        if event_func is not None:
            event_func(self.press_point, self.drag_point, self.release_point)

    def _callBack(self, event, x, y, flags, param):
        # マウス左ボタンが押された時の処理
        if event == cv2.EVENT_LBUTTONDOWN:
            self.press_point = (x,y)
            self._doEvent(self._press_func)
            self._is_drag = True

        # マウス左ドラッグ時の処理
        elif event == cv2.EVENT_MOUSEMOVE:
            self.drag_point = (x,y)
            if self._is_drag:
                self._doEvent(self._drag_func)

        # マウス左ボタンが離された時の処理
        elif event == cv2.EVENT_LBUTTONUP:
            self.release_point = (x,y)
            self._doEvent(self._release_func)
            self._is_drag = False


class CVMousePaint(qtaddtag.QtAddTag):
    def __init__(self, filename, save_dir, win_pos):

        self.original_image = cv2.imread(filename, 1)
        self.save_dir = save_dir
        self.cut_point = (0,0)
        self.cut_side = 0
        self.next_flag = False
        self.app = qtaddtag.QApplication(sys.argv)
        super().__init__(win_pos)
        self.simplePaint()

    def saveButtonClicked(self):

        # トリミング範囲が指定されていないか小さすぎるときに保存をさせずにメッセージを出す。
        if self.cut_side <= 50:
            self.err_lbl.setText("トリミング範囲が指定されていないか小さすぎます。")
            self.err_lbl.adjustSize()

        # トリミング範囲の保存処理
        else:
            self.err_lbl.setText("")
            tag_cnt = 0
            for cb in self.cblist:
                if cb.checkState() == qtaddtag.Qt.Checked:
                    cut_image = self.original_image[self.cut_point[1]:self.cut_point[1]+self.cut_side, self.cut_point[0]:self.cut_point[0]+self.cut_side]
                    resize_image = cv2.resize(cut_image,(64,64))
                    time = "{0:%Y%m%d%H%M%S%f}".format(datetime.datetime.now())
                    cv2.imwrite(self.save_dir + cb.text() + "-" + time + ".jpg", resize_image)
                    cb.setCheckState(qtaddtag.Qt.Unchecked)
                    tag_cnt += 1

            # タグが一つも選択されていないときにメッセージを出す。
            if tag_cnt == 0:
                self.err_lbl.setText("タグが選択されていません。")
                self.err_lbl.adjustSize()

    def nextButtonClicked(self):
        # simplePaintの描画更新ループを停止するフラグを立てる。
        self.next_flag = True

    # 描画リセット用の元画像を生成
    def oriImage(self):
#         return np.zeros((512, 512, 3), np.uint8)
        return self.original_image.copy()
    # 正方形のマウス描画
    def simplePaint(self):
        img = self.oriImage()

        colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]


        # ドラッグ時に描画する関数の定義
        def dragPaint(press_point, drag_point, release_point):
            nonlocal img
            img = self.oriImage()
            width = drag_point[0] - press_point[0]
            height = drag_point[1] - press_point[1]
            side = width if width < height else height

            img = cv2.rectangle(img, press_point, (press_point[0]+side, press_point[1]+side), colors[0], 1)

        def endPaint(press_point, drag_point, release_point):
            nonlocal img
            img = self.oriImage()
            width = release_point[0] - press_point[0]
            height = release_point[1] - press_point[1]
            self.cut_side = width if width < height else height
            self.cut_point = press_point

            img = cv2.rectangle(img, press_point, (press_point[0]+self.cut_side, press_point[1]+self.cut_side), colors[1], 1)

        win_name = 'Paint'
        cv2.namedWindow(win_name)

        # CVMouseEventクラスによるドラッグ描画関数の登録
        mouse_event = CVMouseEvent(drag_func=dragPaint, release_func=endPaint)
        mouse_event.setCallBack(win_name)

        while(True):
            cv2.imshow(win_name, img)
            key = cv2.waitKey(20) & 0xFF

            if self.isVisible() == False:
                sys.exit()
            elif self.next_flag == True:
                break
            # 画像のリセット
            if key == ord('r'):
                img = self.oriImage()

            elif key == ord('q'):
                break
        cv2.destroyAllWindows()
        self.win_pos = (self.geometry().left(), self.geometry().top())
        self.close()