# coding:utf-8
import os
import sys
from PySide6.QtCore import Qt, QTranslator
# from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator
from app.common.config import cfg
from app.view.main_window import MainWindow
from app.resource import resource_rc

# enable dpi scale
if cfg.get(cfg.dpiScale) != "Auto":
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

# create application
app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

# internationalization
locale = cfg.get(cfg.language).value
translator = FluentTranslator(locale)
galleryTranslator = QTranslator()
galleryTranslator.load(locale, "app", ".", ":/app/i18n")

app.installTranslator(translator)
app.installTranslator(galleryTranslator)

# create main window
w = MainWindow()
w.show()

app.exec()
