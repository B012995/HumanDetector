import sys
import copy
from PyQt5.QtWidgets import QWidget, QCheckBox, QPushButton, QApplication, QLabel
from PyQt5.QtCore import Qt


class QtAddTag(QWidget):

    def __init__(self, win_pos):
        super().__init__()

        self.win_pos = win_pos
        self.tag_name = [
            "front_man",
            "front_man_glasses",
            "front_woman",
            "front_woman_glasses",
            "side_man",
            "side_man_glasses",
            "side_woman",
            "side_woman_glasses",
            "back_man",
            "back_woman",
            "back_woman_long",
            ]
        self.cblist = [0 for i in range(len(self.tag_name))]
        self.err_lbl = None

        self.initUI()


    def initUI(self):

        # チェックボックス作成
        for i,tag in enumerate(self.tag_name):
            self.cblist[i] = QCheckBox(tag, self)
            self.cblist[i].move(20+230*(i//10), 10+30*(i%10))

        # 保存ボタン作成
        save_btn = QPushButton("保存", self)
        save_btn.move(20, 30+300)
        save_btn.clicked.connect(self.saveButtonClicked)

        # 次の画像へボタン作成
        next_btn = QPushButton("次の画像へ", self)
        next_btn.move(130, 30+300)
        next_btn.clicked.connect(self.nextButtonClicked)

        # エラーメッセージ用ラベル作成
        self.err_lbl = QLabel(self)
        self.err_lbl.move(20, 10+300)

        self.setGeometry(self.win_pos[0], self.win_pos[1], 230*(1+len(self.tag_name)//10), 60+30*len(self.tag_name))

        self.setWindowTitle('QCheckBox')
        self.show()


    # 抽象メソッドのつもり...
    def saveButtonClicked(self):
        pass

    def nextButtonClicked(self):
        pass