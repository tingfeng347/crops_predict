# coding: utf-8
from PySide6.QtCore import QTimer,QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication
from qfluentwidgets import NavigationItemPosition, SplitFluentWindow, MessageBox,SystemThemeListener,isDarkTheme
from qfluentwidgets import FluentIcon as FIF, setTheme, Theme
import sys
import darkdetect
from ctypes import byref, c_int
from .setting_interface import SettingInterface
from ..common.config import cfg
from ..common.icon import Icon
from ..common import resource
from ..view.ui_homepage import Page1
from ..view.ui_predictpage import PredictPage

     
class MainWindow(SplitFluentWindow):

    def __init__(self):
        super().__init__()
        self.page1 = Page1(self)
        self.predict_page = PredictPage(self)
        self.settingInterface = SettingInterface(self)
        self.initNavigation()
        self.initWindow()
        # 设置背景特效
        QTimer.singleShot(100, lambda: self.applyBackgroundEffectByCfg())
        # 创建并启动系统主题监听器
        self.themeListener = SystemThemeListener(self)
        self.themeListener.systemThemeChanged.connect(self.applyTheme())
        self.themeListener.start()
        
    

    def _onThemeChangedFinished(self):
        super()._onThemeChangedFinished()

        # 云母特效启用时需要增加重试机制
        if self.isMicaEffectEnabled():
            QTimer.singleShot(50, lambda: self.windowEffect.setMicaEffect(self.winId(), isDarkTheme()))
    
       
    def initNavigation(self):
        # 添加子界面
        self.addSubInterface(self.page1, FIF.HOME_FILL, '主页')
        self.addSubInterface(self.predict_page, FIF.VIEW, '作物预测')
        self.addSubInterface(self.settingInterface, FIF.SETTING, '设置', position=NavigationItemPosition.BOTTOM)

        # 添加帮助项
        self.navigationInterface.addItem(
            routeKey='help',  # 帮助项仍需明确设置 routeKey
            icon=FIF.HELP,
            text='帮助',
            onClick=self.showTeachingTip,
            position=NavigationItemPosition.BOTTOM,
        )

        self.navigationInterface.setExpandWidth(200)

    def initWindow(self):
        self.resize(1000, 650)
        self.setMinimumWidth(750)
        self.setMinimumHeight(650)

        self.setCustomBackgroundColor(QColor(240, 244, 249), QColor(32, 32, 32))

        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.show()
        QApplication.processEvents()

    def closeEvent(self, e):
        """ 停止主题监听器线程 """
        self.themeListener.terminate()
        self.themeListener.deleteLater()
        super().closeEvent(e)
    def showTeachingTip(self):
        w = MessageBox(
            '帮助🥰',
            '''这是一个作物预测系统\n
            输入四个指标可以进行预测产量\n
            训练结果在底部标签框展示\n
            点击预测产量后会自动加载对应的模型\n
            点击预训练模型会训练同一模型下的所有作物模型''',
            self
        )
        w.yesButton.setText('确定')
        w.cancelButton.setText('取消')
        w.exec()


    def applyTheme(self):
        """ 应用主题 """
        if cfg.themeMode.value == Theme.AUTO:
            setTheme(Theme.AUTO)
        elif cfg.themeMode.value == Theme.DARK:
            setTheme(Theme.AUTO)
        elif cfg.themeMode.value == Theme.LIGHT:
            setTheme(Theme.LIGHT)
        
    
    def applyBackgroundEffectByCfg(self):
        """ 根据配置加载窗口背景特效 """
        if sys.platform == 'win32':
            # 移除现有背景特效
            self.windowEffect.removeBackgroundEffect(self.winId())
            # 从配置中读取背景特效选项
            effect = cfg.backgroundEffect.value
            # 根据配置选择特效
            if effect == 'Acrylic':
                self.windowEffect.setAcrylicEffect(self.winId(),
                    "00000030" if isDarkTheme() else "F2F2F230")
            elif effect == 'Mica':
                self.windowEffect.setMicaEffect(self.winId(), darkdetect.isDark())
            elif effect == 'MicaBlur':
                self.windowEffect.setMicaEffect(self.winId(), darkdetect.isDark())
                self.windowEffect.DwmSetWindowAttribute(self.winId(), 38, byref(c_int(3)), 4)
            elif effect == 'MicaAlt':
                self.windowEffect.setMicaEffect(self.winId(), darkdetect.isDark(), True)
            else:
                print(f"未知背景特效配置：{effect}")

