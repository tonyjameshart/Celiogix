# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings_panel.ui'
##
## Created by: Qt User Interface Compiler version 6.9.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_SettingsPanel(object):
    def setupUi(self, SettingsPanel):
        if not SettingsPanel.objectName():
            SettingsPanel.setObjectName(u"SettingsPanel")
        SettingsPanel.resize(800, 600)
        self.verticalLayout = QVBoxLayout(SettingsPanel)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.placeholderLabel = QLabel(SettingsPanel)
        self.placeholderLabel.setObjectName(u"placeholderLabel")
        self.placeholderLabel.setAlignment(Qt.AlignCenter)
        self.placeholderLabel.setWordWrap(True)

        self.verticalLayout.addWidget(self.placeholderLabel)


        self.retranslateUi(SettingsPanel)

        QMetaObject.connectSlotsByName(SettingsPanel)
    # setupUi

    def retranslateUi(self, SettingsPanel):
        self.placeholderLabel.setText(QCoreApplication.translate("SettingsPanel", u"Settings functionality will be implemented here.\n"
"\n"
"Features will include:\n"
"\u2022 Application preferences\n"
"\u2022 Database management\n"
"\u2022 Theme selection\n"
"\u2022 Export/import settings", None))
        pass
    # retranslateUi

