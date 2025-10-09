# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QMainWindow, QMenu, QMenuBar,
    QSizePolicy, QStatusBar, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1440, 900)
        MainWindow.setMinimumSize(QSize(1024, 768))
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.pantryTab = QWidget()
        self.pantryTab.setObjectName(u"pantryTab")
        self.tabWidget.addTab(self.pantryTab, "")
        self.cookbookTab = QWidget()
        self.cookbookTab.setObjectName(u"cookbookTab")
        self.tabWidget.addTab(self.cookbookTab, "")
        self.shoppingTab = QWidget()
        self.shoppingTab.setObjectName(u"shoppingTab")
        self.tabWidget.addTab(self.shoppingTab, "")
        self.healthTab = QWidget()
        self.healthTab.setObjectName(u"healthTab")
        self.tabWidget.addTab(self.healthTab, "")
        self.menuTab = QWidget()
        self.menuTab.setObjectName(u"menuTab")
        self.tabWidget.addTab(self.menuTab, "")
        self.calendarTab = QWidget()
        self.calendarTab.setObjectName(u"calendarTab")
        self.tabWidget.addTab(self.calendarTab, "")
        self.importTab = QWidget()
        self.importTab.setObjectName(u"importTab")
        self.tabWidget.addTab(self.importTab, "")
        self.settingsTab = QWidget()
        self.settingsTab.setObjectName(u"settingsTab")
        self.tabWidget.addTab(self.settingsTab, "")

        self.verticalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1440, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Celiogix - PySide6", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"E&xit", None))
#if QT_CONFIG(shortcut)
        self.actionExit.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"&About", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.pantryTab), QCoreApplication.translate("MainWindow", u"Pantry", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.cookbookTab), QCoreApplication.translate("MainWindow", u"Cookbook", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.shoppingTab), QCoreApplication.translate("MainWindow", u"Shopping", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.healthTab), QCoreApplication.translate("MainWindow", u"Health Log", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.menuTab), QCoreApplication.translate("MainWindow", u"Menu", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.calendarTab), QCoreApplication.translate("MainWindow", u"Calendar", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.importTab), QCoreApplication.translate("MainWindow", u"Import Mobile Data", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.settingsTab), QCoreApplication.translate("MainWindow", u"Settings", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"&File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"&Help", None))
    # retranslateUi

