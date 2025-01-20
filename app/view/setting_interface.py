# coding:utf-8
from qfluentwidgets import (SwitchSettingCard, 
                            HyperlinkCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout,setTheme, setFont)
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import SettingCardGroup as CardGroup
from qfluentwidgets import InfoBar
import sys
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QFont
from PySide6.QtWidgets import QWidget, QLabel
from ..common.config import cfg, isWin11
from ..common.setting import HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR
from ..common.signal_bus import signalBus
from ..common.style_sheet import StyleSheet


class SettingCardGroup(CardGroup):

   def __init__(self, title: str, parent=None):
       super().__init__(title, parent)
       setFont(self.titleLabel, 14, QFont.Weight.DemiBold)



class SettingInterface(ScrollArea):
    """ Setting interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.settingLabel = QLabel(self.tr(""), self)

        # personalization
        self.personalGroup = SettingCardGroup(
            self.tr('Personalization'), self.scrollWidget)
        

        if sys.platform == "win32":
            self.backgroundEffectCard = ComboBoxSettingCard(
                cfg.backgroundEffect,
                FIF.BRUSH,
                self.tr('Mica effect'),
                self.tr("Apply semi transparent to windows and surfaces"),
                texts=["Mica", "MicaBlur", "MicaAlt", "Aero","Acrylic"],
                parent=self.personalGroup
            )
        
        self.themeCard = ComboBoxSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            self.tr('Application theme'),
            self.tr("Change the appearance of your application"),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            parent=self.personalGroup
        )
        
        self.zoomCard = ComboBoxSettingCard(
            cfg.dpiScale,
            FIF.ZOOM,
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("Use system setting")
            ],
            parent=self.personalGroup
        )
        
        
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            self.tr('Language'),
            self.tr('Set your preferred language for UI'),
            texts=['简体中文', '繁體中文', 'English', self.tr('Use system setting')],
            parent=self.personalGroup
        )

        # update software
        self.updateSoftwareGroup = SettingCardGroup(
            self.tr("Software update"), self.scrollWidget)
        self.updateOnStartUpCard = SwitchSettingCard(
            FIF.UPDATE,
            self.tr('Check for updates when the application starts'),
            self.tr('The new version will be more stable and have more features'),
            configItem=cfg.checkUpdateAtStartUp,
            parent=self.updateSoftwareGroup
        )

        # application
        self.aboutGroup = SettingCardGroup(self.tr('About'), self.scrollWidget)
        self.helpCard = HyperlinkCard(
            HELP_URL,
            self.tr('Open help page'),
            FIF.HELP,
            self.tr('Help'),
            self.tr(
                'Discover new features and learn useful tips about Fluent Client'),
            self.aboutGroup
        )
        self.feedbackCard = PrimaryPushSettingCard(
            self.tr('Provide feedback'),
            FIF.FEEDBACK,
            self.tr('Provide feedback'),
            self.tr('Help us improve Fluent Client by providing feedback'),
            self.aboutGroup
        )
        self.aboutCard = PrimaryPushSettingCard(
            self.tr('Check update'),
            ":/qfluentwidgets/images/logo.png",
            self.tr('About'),
            '© ' + self.tr('Copyright') + f" {YEAR}, {AUTHOR}. " +
            self.tr('Version') + " " + VERSION,
            self.aboutGroup
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 100, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface')

        # initialize style sheet
        setFont(self.settingLabel, 23, QFont.Weight.DemiBold)
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)
        self.scrollWidget.setStyleSheet("QWidget{background:transparent}")

        # self.micaCard.setEnabled(isWin11())

        # initialize layout
        self.__initLayout()
        self._connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(36, 50)

        # self.personalGroup.addSettingCard(self.micaCard)
        self.personalGroup.addSettingCard(self.themeCard)
        if sys.platform == "win32":
            self.personalGroup.addSettingCard(self.backgroundEffectCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        self.personalGroup.addSettingCard(self.languageCard)

        self.updateSoftwareGroup.addSettingCard(self.updateOnStartUpCard)

        self.aboutGroup.addSettingCard(self.helpCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.updateSoftwareGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def _showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.success(
            self.tr('Updated successfully'),
            self.tr('Configuration takes effect after restart'),
            duration=1500,
            parent=self
        )

    def _connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self._showRestartTooltip)

        # personalization
        cfg.themeChanged.connect(setTheme)
        cfg.themeChanged.connect(self._themeChangedFinished)
        # self.micaCard.checkedChanged.connect(signalBus.micaEnableChanged)
        if sys.platform == "win32":
            self.backgroundEffectCard.comboBox.currentIndexChanged.connect(self.__onBackgroundEffectCardChanged)

        # if sys.platform == "win32":
        #     self.themeCard.comboBox.currentIndexChanged.connect(self.__onthemeCard)
            
        # check update
        self.aboutCard.clicked.connect(signalBus.checkUpdateSig)

        # about
        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))
    
    def __onBackgroundEffectCardChanged(self, option):
        """ background effect card changed slot """
        self.window().applyBackgroundEffectByCfg()
        
    def _themeChangedFinished(self, themeIndex):
        # 当主题选项为深色时，禁用云母效果选项
        if themeIndex == themeIndex.DARK:
            self.backgroundEffectCard.setEnabled(False)
        else:
            self.backgroundEffectCard.setEnabled(True)
            
        # 确保云母效果选项恢复为 Mica
        self.backgroundEffectCard.comboBox.setCurrentText("Mica")


        
    
        
    

