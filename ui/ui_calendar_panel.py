# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'calendar_panel.ui'
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

class Ui_CalendarPanel(object):
    def setupUi(self, CalendarPanel):
        if not CalendarPanel.objectName():
            CalendarPanel.setObjectName(u"CalendarPanel")
        CalendarPanel.resize(800, 600)
        self.verticalLayout = QVBoxLayout(CalendarPanel)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.placeholderLabel = QLabel(CalendarPanel)
        self.placeholderLabel.setObjectName(u"placeholderLabel")
        self.placeholderLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholderLabel.setWordWrap(True)

        self.verticalLayout.addWidget(self.placeholderLabel)


        self.retranslateUi(CalendarPanel)

        QMetaObject.connectSlotsByName(CalendarPanel)
    # setupUi

    def retranslateUi(self, CalendarPanel):
        self.placeholderLabel.setText(QCoreApplication.translate("CalendarPanel", u"Calendar functionality will be implemented here.\n"
"\n"
"Features will include:\n"
"\u2022 Health log calendar view\n"
"\u2022 Symptom pattern visualization\n"
"\u2022 Meal planning calendar\n"
"\u2022 Doctor appointment tracking", None))
        pass
    # retranslateUi

