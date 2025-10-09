# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pantry_panel.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QDateEdit,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QSpinBox, QSplitter, QTableWidget, QTableWidgetItem,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_PantryPanel(object):
    def setupUi(self, PantryPanel):
        if not PantryPanel.objectName():
            PantryPanel.setObjectName(u"PantryPanel")
        PantryPanel.resize(825, 600)
        self.verticalLayout = QVBoxLayout(PantryPanel)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.splitter = QSplitter(PantryPanel)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.formWidget = QWidget(self.splitter)
        self.formWidget.setObjectName(u"formWidget")
        self.formWidget.setMinimumSize(QSize(300, 0))
        self.formLayout = QVBoxLayout(self.formWidget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formGroup = QGroupBox(self.formWidget)
        self.formGroup.setObjectName(u"formGroup")
        self.formGroupLayout = QVBoxLayout(self.formGroup)
        self.formGroupLayout.setObjectName(u"formGroupLayout")
        self.nameLayout = QHBoxLayout()
        self.nameLayout.setObjectName(u"nameLayout")
        self.nameLabel = QLabel(self.formGroup)
        self.nameLabel.setObjectName(u"nameLabel")

        self.nameLayout.addWidget(self.nameLabel)

        self.nameEdit = QLineEdit(self.formGroup)
        self.nameEdit.setObjectName(u"nameEdit")

        self.nameLayout.addWidget(self.nameEdit)


        self.formGroupLayout.addLayout(self.nameLayout)

        self.categoryLayout = QHBoxLayout()
        self.categoryLayout.setObjectName(u"categoryLayout")
        self.categoryLabel = QLabel(self.formGroup)
        self.categoryLabel.setObjectName(u"categoryLabel")

        self.categoryLayout.addWidget(self.categoryLabel)

        self.categoryCombo = QComboBox(self.formGroup)
        self.categoryCombo.addItem("")
        self.categoryCombo.addItem("")
        self.categoryCombo.addItem("")
        self.categoryCombo.addItem("")
        self.categoryCombo.addItem("")
        self.categoryCombo.addItem("")
        self.categoryCombo.addItem("")
        self.categoryCombo.addItem("")
        self.categoryCombo.addItem("")
        self.categoryCombo.addItem("")
        self.categoryCombo.setObjectName(u"categoryCombo")

        self.categoryLayout.addWidget(self.categoryCombo)


        self.formGroupLayout.addLayout(self.categoryLayout)

        self.quantityLayout = QHBoxLayout()
        self.quantityLayout.setObjectName(u"quantityLayout")
        self.quantityLabel = QLabel(self.formGroup)
        self.quantityLabel.setObjectName(u"quantityLabel")

        self.quantityLayout.addWidget(self.quantityLabel)

        self.quantitySpin = QSpinBox(self.formGroup)
        self.quantitySpin.setObjectName(u"quantitySpin")
        self.quantitySpin.setMinimum(0)
        self.quantitySpin.setMaximum(9999)
        self.quantitySpin.setValue(1)

        self.quantityLayout.addWidget(self.quantitySpin)


        self.formGroupLayout.addLayout(self.quantityLayout)

        self.unitLayout = QHBoxLayout()
        self.unitLayout.setObjectName(u"unitLayout")
        self.unitLabel = QLabel(self.formGroup)
        self.unitLabel.setObjectName(u"unitLabel")

        self.unitLayout.addWidget(self.unitLabel)

        self.unitCombo = QComboBox(self.formGroup)
        self.unitCombo.addItem("")
        self.unitCombo.addItem("")
        self.unitCombo.addItem("")
        self.unitCombo.addItem("")
        self.unitCombo.addItem("")
        self.unitCombo.addItem("")
        self.unitCombo.addItem("")
        self.unitCombo.addItem("")
        self.unitCombo.addItem("")
        self.unitCombo.addItem("")
        self.unitCombo.addItem("")
        self.unitCombo.addItem("")
        self.unitCombo.setObjectName(u"unitCombo")

        self.unitLayout.addWidget(self.unitCombo)


        self.formGroupLayout.addLayout(self.unitLayout)

        self.expLayout = QHBoxLayout()
        self.expLayout.setObjectName(u"expLayout")
        self.expLabel = QLabel(self.formGroup)
        self.expLabel.setObjectName(u"expLabel")

        self.expLayout.addWidget(self.expLabel)

        self.expDate = QDateEdit(self.formGroup)
        self.expDate.setObjectName(u"expDate")
        self.expDate.setDate(QDate(2024, 2, 15))

        self.expLayout.addWidget(self.expDate)


        self.formGroupLayout.addLayout(self.expLayout)

        self.gfLayout = QHBoxLayout()
        self.gfLayout.setObjectName(u"gfLayout")
        self.gfLabel = QLabel(self.formGroup)
        self.gfLabel.setObjectName(u"gfLabel")

        self.gfLayout.addWidget(self.gfLabel)

        self.gfCombo = QComboBox(self.formGroup)
        self.gfCombo.addItem("")
        self.gfCombo.addItem("")
        self.gfCombo.addItem("")
        self.gfCombo.setObjectName(u"gfCombo")

        self.gfLayout.addWidget(self.gfCombo)


        self.formGroupLayout.addLayout(self.gfLayout)

        self.notesLayout = QVBoxLayout()
        self.notesLayout.setObjectName(u"notesLayout")
        self.notesLabel = QLabel(self.formGroup)
        self.notesLabel.setObjectName(u"notesLabel")
        self.notesLabel.setMaximumSize(QSize(16777215, 25))

        self.notesLayout.addWidget(self.notesLabel)

        self.notesEdit = QTextEdit(self.formGroup)
        self.notesEdit.setObjectName(u"notesEdit")
        self.notesEdit.setMaximumSize(QSize(16777215, 800))

        self.notesLayout.addWidget(self.notesEdit)


        self.formGroupLayout.addLayout(self.notesLayout)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.addButton = QPushButton(self.formGroup)
        self.addButton.setObjectName(u"addButton")

        self.buttonLayout.addWidget(self.addButton)

        self.updateButton = QPushButton(self.formGroup)
        self.updateButton.setObjectName(u"updateButton")

        self.buttonLayout.addWidget(self.updateButton)

        self.clearButton = QPushButton(self.formGroup)
        self.clearButton.setObjectName(u"clearButton")

        self.buttonLayout.addWidget(self.clearButton)


        self.formGroupLayout.addLayout(self.buttonLayout)


        self.formLayout.addWidget(self.formGroup)

        self.splitter.addWidget(self.formWidget)
        self.listWidget = QWidget(self.splitter)
        self.listWidget.setObjectName(u"listWidget")
        self.listWidget.setMinimumSize(QSize(500, 0))
        self.listLayout = QVBoxLayout(self.listWidget)
        self.listLayout.setObjectName(u"listLayout")
        self.listLayout.setContentsMargins(0, 0, 0, 0)
        self.listGroup = QGroupBox(self.listWidget)
        self.listGroup.setObjectName(u"listGroup")
        self.listGroupLayout = QVBoxLayout(self.listGroup)
        self.listGroupLayout.setObjectName(u"listGroupLayout")
        self.searchLayout = QHBoxLayout()
        self.searchLayout.setObjectName(u"searchLayout")
        self.searchLabel = QLabel(self.listGroup)
        self.searchLabel.setObjectName(u"searchLabel")

        self.searchLayout.addWidget(self.searchLabel)

        self.searchEdit = QLineEdit(self.listGroup)
        self.searchEdit.setObjectName(u"searchEdit")

        self.searchLayout.addWidget(self.searchEdit)


        self.listGroupLayout.addLayout(self.searchLayout)

        self.itemsTable = QTableWidget(self.listGroup)
        if (self.itemsTable.columnCount() < 7):
            self.itemsTable.setColumnCount(7)
        __qtablewidgetitem = QTableWidgetItem()
        self.itemsTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.itemsTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.itemsTable.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.itemsTable.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.itemsTable.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.itemsTable.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.itemsTable.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        self.itemsTable.setObjectName(u"itemsTable")
        self.itemsTable.setAlternatingRowColors(True)
        self.itemsTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.listGroupLayout.addWidget(self.itemsTable)

        self.actionLayout = QHBoxLayout()
        self.actionLayout.setObjectName(u"actionLayout")
        self.deleteButton = QPushButton(self.listGroup)
        self.deleteButton.setObjectName(u"deleteButton")

        self.actionLayout.addWidget(self.deleteButton)

        self.refreshButton = QPushButton(self.listGroup)
        self.refreshButton.setObjectName(u"refreshButton")

        self.actionLayout.addWidget(self.refreshButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.actionLayout.addItem(self.horizontalSpacer)


        self.listGroupLayout.addLayout(self.actionLayout)


        self.listLayout.addWidget(self.listGroup)

        self.splitter.addWidget(self.listWidget)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(PantryPanel)

        QMetaObject.connectSlotsByName(PantryPanel)
    # setupUi

    def retranslateUi(self, PantryPanel):
        self.formGroup.setTitle(QCoreApplication.translate("PantryPanel", u"Add/Edit Item", None))
        self.nameLabel.setText(QCoreApplication.translate("PantryPanel", u"Item Name:", None))
        self.nameEdit.setPlaceholderText(QCoreApplication.translate("PantryPanel", u"Enter item name", None))
        self.categoryLabel.setText(QCoreApplication.translate("PantryPanel", u"Category:", None))
        self.categoryCombo.setItemText(0, QCoreApplication.translate("PantryPanel", u"Grains & Flours", None))
        self.categoryCombo.setItemText(1, QCoreApplication.translate("PantryPanel", u"Baking", None))
        self.categoryCombo.setItemText(2, QCoreApplication.translate("PantryPanel", u"Canned Goods", None))
        self.categoryCombo.setItemText(3, QCoreApplication.translate("PantryPanel", u"Dairy", None))
        self.categoryCombo.setItemText(4, QCoreApplication.translate("PantryPanel", u"Meat & Seafood", None))
        self.categoryCombo.setItemText(5, QCoreApplication.translate("PantryPanel", u"Fruits & Vegetables", None))
        self.categoryCombo.setItemText(6, QCoreApplication.translate("PantryPanel", u"Spices & Seasonings", None))
        self.categoryCombo.setItemText(7, QCoreApplication.translate("PantryPanel", u"Snacks", None))
        self.categoryCombo.setItemText(8, QCoreApplication.translate("PantryPanel", u"Beverages", None))
        self.categoryCombo.setItemText(9, QCoreApplication.translate("PantryPanel", u"Other", None))

        self.quantityLabel.setText(QCoreApplication.translate("PantryPanel", u"Quantity:", None))
        self.unitLabel.setText(QCoreApplication.translate("PantryPanel", u"Unit:", None))
        self.unitCombo.setItemText(0, QCoreApplication.translate("PantryPanel", u"pieces", None))
        self.unitCombo.setItemText(1, QCoreApplication.translate("PantryPanel", u"cups", None))
        self.unitCombo.setItemText(2, QCoreApplication.translate("PantryPanel", u"tbsp", None))
        self.unitCombo.setItemText(3, QCoreApplication.translate("PantryPanel", u"tsp", None))
        self.unitCombo.setItemText(4, QCoreApplication.translate("PantryPanel", u"lbs", None))
        self.unitCombo.setItemText(5, QCoreApplication.translate("PantryPanel", u"oz", None))
        self.unitCombo.setItemText(6, QCoreApplication.translate("PantryPanel", u"grams", None))
        self.unitCombo.setItemText(7, QCoreApplication.translate("PantryPanel", u"ml", None))
        self.unitCombo.setItemText(8, QCoreApplication.translate("PantryPanel", u"liters", None))
        self.unitCombo.setItemText(9, QCoreApplication.translate("PantryPanel", u"cans", None))
        self.unitCombo.setItemText(10, QCoreApplication.translate("PantryPanel", u"boxes", None))
        self.unitCombo.setItemText(11, QCoreApplication.translate("PantryPanel", u"bags", None))

        self.expLabel.setText(QCoreApplication.translate("PantryPanel", u"Expiration:", None))
        self.gfLabel.setText(QCoreApplication.translate("PantryPanel", u"Gluten-Free:", None))
        self.gfCombo.setItemText(0, QCoreApplication.translate("PantryPanel", u"Yes", None))
        self.gfCombo.setItemText(1, QCoreApplication.translate("PantryPanel", u"No", None))
        self.gfCombo.setItemText(2, QCoreApplication.translate("PantryPanel", u"Unknown", None))

        self.notesLabel.setText(QCoreApplication.translate("PantryPanel", u"Notes:", None))
        self.notesEdit.setPlaceholderText(QCoreApplication.translate("PantryPanel", u"Additional notes...", None))
        self.addButton.setText(QCoreApplication.translate("PantryPanel", u"Add Item", None))
        self.updateButton.setText(QCoreApplication.translate("PantryPanel", u"Update Item", None))
        self.clearButton.setText(QCoreApplication.translate("PantryPanel", u"Clear Form", None))
        self.listGroup.setTitle(QCoreApplication.translate("PantryPanel", u"Pantry Items", None))
        self.searchLabel.setText(QCoreApplication.translate("PantryPanel", u"Search:", None))
        self.searchEdit.setPlaceholderText(QCoreApplication.translate("PantryPanel", u"Search items...", None))
        ___qtablewidgetitem = self.itemsTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("PantryPanel", u"Name", None));
        ___qtablewidgetitem1 = self.itemsTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("PantryPanel", u"Category", None));
        ___qtablewidgetitem2 = self.itemsTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("PantryPanel", u"Quantity", None));
        ___qtablewidgetitem3 = self.itemsTable.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("PantryPanel", u"Unit", None));
        ___qtablewidgetitem4 = self.itemsTable.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("PantryPanel", u"Expiration", None));
        ___qtablewidgetitem5 = self.itemsTable.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("PantryPanel", u"GF Status", None));
        ___qtablewidgetitem6 = self.itemsTable.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("PantryPanel", u"Notes", None));
        self.deleteButton.setText(QCoreApplication.translate("PantryPanel", u"Delete Item", None))
        self.refreshButton.setText(QCoreApplication.translate("PantryPanel", u"Refresh", None))
        pass
    # retranslateUi

