# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'menu_panel.ui'
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

class Ui_MenuPanel(object):
    def setupUi(self, MenuPanel):
        if not MenuPanel.objectName():
            MenuPanel.setObjectName(u"MenuPanel")
        MenuPanel.resize(800, 50)
        self.verticalLayout = QVBoxLayout(MenuPanel)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.placeholderLabel = QLabel(MenuPanel)
        self.placeholderLabel.setObjectName(u"placeholderLabel")
        self.placeholderLabel.setAlignment(Qt.AlignCenter)
        self.placeholderLabel.setWordWrap(True)

        self.verticalLayout.addWidget(self.placeholderLabel)


        self.retranslateUi(MenuPanel)

        QMetaObject.connectSlotsByName(MenuPanel)
    # setupUi

    def retranslateUi(self, MenuPanel):
        self.placeholderLabel.setText(QCoreApplication.translate("MenuPanel", u"Menu planning functionality will be implemented here.\n"
"\n"
"Features will include:\n"
"\u2022 Weekly meal planning\n"
"\u2022 Gluten-free meal suggestions\n"
"\u2022 Nutritional balance tracking\n"
"\u2022 Shopping list generation", None))
        pass
    # retranslateUi

