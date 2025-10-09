# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'shopping_list_panel.ui'
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

class Ui_ShoppingListPanel(object):
    def setupUi(self, ShoppingListPanel):
        if not ShoppingListPanel.objectName():
            ShoppingListPanel.setObjectName(u"ShoppingListPanel")
        ShoppingListPanel.resize(800, 600)
        self.verticalLayout = QVBoxLayout(ShoppingListPanel)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.placeholderLabel = QLabel(ShoppingListPanel)
        self.placeholderLabel.setObjectName(u"placeholderLabel")
        self.placeholderLabel.setAlignment(Qt.AlignCenter)
        self.placeholderLabel.setWordWrap(True)

        self.verticalLayout.addWidget(self.placeholderLabel)


        self.retranslateUi(ShoppingListPanel)

        QMetaObject.connectSlotsByName(ShoppingListPanel)
    # setupUi

    def retranslateUi(self, ShoppingListPanel):
        self.placeholderLabel.setText(QCoreApplication.translate("ShoppingListPanel", u"Shopping list functionality will be implemented here.\n"
"\n"
"Features will include:\n"
"\u2022 Smart shopping lists\n"
"\u2022 Gluten-free product recommendations\n"
"\u2022 Barcode scanning integration\n"
"\u2022 Price tracking", None))
        pass
    # retranslateUi

