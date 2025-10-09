# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cookbook_panel.ui'
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

class Ui_CookbookPanel(object):
    def setupUi(self, CookbookPanel):
        if not CookbookPanel.objectName():
            CookbookPanel.setObjectName(u"CookbookPanel")
        CookbookPanel.resize(800, 600)
        self.verticalLayout = QVBoxLayout(CookbookPanel)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.placeholderLabel = QLabel(CookbookPanel)
        self.placeholderLabel.setObjectName(u"placeholderLabel")
        self.placeholderLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholderLabel.setWordWrap(True)

        self.verticalLayout.addWidget(self.placeholderLabel)


        self.retranslateUi(CookbookPanel)

        QMetaObject.connectSlotsByName(CookbookPanel)
    # setupUi

    def retranslateUi(self, CookbookPanel):
        self.placeholderLabel.setText(QCoreApplication.translate("CookbookPanel", u"Cookbook functionality will be implemented here.\n"
"\n"
"Features will include:\n"
"\u2022 Recipe management\n"
"\u2022 Gluten-free recipe database\n"
"\u2022 Nutritional information\n"
"\u2022 Meal planning integration", None))
        pass
    # retranslateUi

