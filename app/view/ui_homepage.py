# -*- coding: utf-8 -*-

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtGui import QPainter, QPainterPath
from PySide6.QtWidgets import QWidget, QLabel


class Ui_homepage(object):
    def setupUi(self, homepage):
        homepage.setObjectName("homepage")
        homepage.resize(1426, 938)
        homepage.setMinimumSize(QtCore.QSize(700, 500))
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(homepage)
        self.verticalLayout_3.setContentsMargins(20, 40, 20, 20)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.CardWidget = CardWidget(homepage)
        self.CardWidget.setObjectName("CardWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.CardWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.SubtitleLabel = SubtitleLabel(self.CardWidget)
        self.SubtitleLabel.setEnabled(True)
        self.SubtitleLabel.setFrameShadow(QtWidgets.QFrame.Plain)
        self.SubtitleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.SubtitleLabel.setObjectName("SubtitleLabel")
        self.verticalLayout.addWidget(self.SubtitleLabel)
        self.verticalLayout_2.addWidget(self.CardWidget)
        self.label = RoundedLabel(homepage)
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/images/background.jpg"))


        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        spacerItem = QtWidgets.QSpacerItem(1401, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_3.addItem(spacerItem)

        self.retranslateUi(homepage)
        QtCore.QMetaObject.connectSlotsByName(homepage)

    def retranslateUi(self, homepage):
        _translate = QtCore.QCoreApplication.translate
        homepage.setWindowTitle(_translate("homepage", "主页"))
        self.SubtitleLabel.setText(_translate("homepage", "欢迎使用作物预测系统"))


from qfluentwidgets import CardWidget, SubtitleLabel


class RoundedLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.radius = 10  # 圆角的半径可以根据需要调整

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(self.rect(), self.radius, self.radius)
        painter.setClipPath(path)
        painter.drawPixmap(self.rect(), self.pixmap())

class Page1(Ui_homepage, QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)