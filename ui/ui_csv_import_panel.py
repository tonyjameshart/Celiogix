# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'csv_import_panel.ui'
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
from PySide6.QtWidgets import (QApplication, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QProgressBar, QPushButton, QRadioButton,
    QSizePolicy, QSpacerItem, QTextEdit, QVBoxLayout,
    QWidget)

class Ui_CSVImportPanel(object):
    def setupUi(self, CSVImportPanel):
        if not CSVImportPanel.objectName():
            CSVImportPanel.setObjectName(u"CSVImportPanel")
        CSVImportPanel.resize(800, 600)
        self.verticalLayout = QVBoxLayout(CSVImportPanel)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)
        self.fileGroup = QGroupBox(CSVImportPanel)
        self.fileGroup.setObjectName(u"fileGroup")
        self.fileLayout = QVBoxLayout(self.fileGroup)
        self.fileLayout.setObjectName(u"fileLayout")
        self.filePathLayout = QHBoxLayout()
        self.filePathLayout.setObjectName(u"filePathLayout")
        self.fileLabel = QLabel(self.fileGroup)
        self.fileLabel.setObjectName(u"fileLabel")

        self.filePathLayout.addWidget(self.fileLabel)

        self.filePathEdit = QLineEdit(self.fileGroup)
        self.filePathEdit.setObjectName(u"filePathEdit")
        self.filePathEdit.setReadOnly(True)

        self.filePathLayout.addWidget(self.filePathEdit)

        self.browseButton = QPushButton(self.fileGroup)
        self.browseButton.setObjectName(u"browseButton")

        self.filePathLayout.addWidget(self.browseButton)


        self.fileLayout.addLayout(self.filePathLayout)


        self.verticalLayout.addWidget(self.fileGroup)

        self.validationGroup = QGroupBox(CSVImportPanel)
        self.validationGroup.setObjectName(u"validationGroup")
        self.validationLayout = QVBoxLayout(self.validationGroup)
        self.validationLayout.setObjectName(u"validationLayout")
        self.validationText = QTextEdit(self.validationGroup)
        self.validationText.setObjectName(u"validationText")
        self.validationText.setMaximumSize(QSize(16777215, 100))
        self.validationText.setReadOnly(True)

        self.validationLayout.addWidget(self.validationText)


        self.verticalLayout.addWidget(self.validationGroup)

        self.optionsGroup = QGroupBox(CSVImportPanel)
        self.optionsGroup.setObjectName(u"optionsGroup")
        self.optionsLayout = QVBoxLayout(self.optionsGroup)
        self.optionsLayout.setObjectName(u"optionsLayout")
        self.modeLayout = QHBoxLayout()
        self.modeLayout.setObjectName(u"modeLayout")
        self.modeLabel = QLabel(self.optionsGroup)
        self.modeLabel.setObjectName(u"modeLabel")

        self.modeLayout.addWidget(self.modeLabel)

        self.replaceRadio = QRadioButton(self.optionsGroup)
        self.replaceRadio.setObjectName(u"replaceRadio")
        self.replaceRadio.setChecked(True)

        self.modeLayout.addWidget(self.replaceRadio)

        self.skipRadio = QRadioButton(self.optionsGroup)
        self.skipRadio.setObjectName(u"skipRadio")

        self.modeLayout.addWidget(self.skipRadio)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.modeLayout.addItem(self.horizontalSpacer)


        self.optionsLayout.addLayout(self.modeLayout)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.importButton = QPushButton(self.optionsGroup)
        self.importButton.setObjectName(u"importButton")
        self.importButton.setEnabled(False)

        self.buttonLayout.addWidget(self.importButton)

        self.clearButton = QPushButton(self.optionsGroup)
        self.clearButton.setObjectName(u"clearButton")

        self.buttonLayout.addWidget(self.clearButton)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.horizontalSpacer_2)


        self.optionsLayout.addLayout(self.buttonLayout)


        self.verticalLayout.addWidget(self.optionsGroup)

        self.progressGroup = QGroupBox(CSVImportPanel)
        self.progressGroup.setObjectName(u"progressGroup")
        self.progressLayout = QVBoxLayout(self.progressGroup)
        self.progressLayout.setObjectName(u"progressLayout")
        self.progressLabel = QLabel(self.progressGroup)
        self.progressLabel.setObjectName(u"progressLabel")

        self.progressLayout.addWidget(self.progressLabel)

        self.progressBar = QProgressBar(self.progressGroup)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setVisible(False)

        self.progressLayout.addWidget(self.progressBar)


        self.verticalLayout.addWidget(self.progressGroup)

        self.resultsGroup = QGroupBox(CSVImportPanel)
        self.resultsGroup.setObjectName(u"resultsGroup")
        self.resultsLayout = QVBoxLayout(self.resultsGroup)
        self.resultsLayout.setObjectName(u"resultsLayout")
        self.resultsText = QTextEdit(self.resultsGroup)
        self.resultsText.setObjectName(u"resultsText")
        self.resultsText.setReadOnly(True)

        self.resultsLayout.addWidget(self.resultsText)


        self.verticalLayout.addWidget(self.resultsGroup)


        self.retranslateUi(CSVImportPanel)

        QMetaObject.connectSlotsByName(CSVImportPanel)
    # setupUi

    def retranslateUi(self, CSVImportPanel):
        self.fileGroup.setTitle(QCoreApplication.translate("CSVImportPanel", u"Select CSV File", None))
        self.fileLabel.setText(QCoreApplication.translate("CSVImportPanel", u"File:", None))
        self.filePathEdit.setPlaceholderText(QCoreApplication.translate("CSVImportPanel", u"No file selected", None))
        self.browseButton.setText(QCoreApplication.translate("CSVImportPanel", u"Browse...", None))
        self.validationGroup.setTitle(QCoreApplication.translate("CSVImportPanel", u"File Validation", None))
        self.validationText.setPlaceholderText(QCoreApplication.translate("CSVImportPanel", u"File validation results will appear here...", None))
        self.optionsGroup.setTitle(QCoreApplication.translate("CSVImportPanel", u"Import Options", None))
        self.modeLabel.setText(QCoreApplication.translate("CSVImportPanel", u"Import Mode:", None))
        self.replaceRadio.setText(QCoreApplication.translate("CSVImportPanel", u"Replace existing data", None))
        self.skipRadio.setText(QCoreApplication.translate("CSVImportPanel", u"Skip existing data", None))
        self.importButton.setText(QCoreApplication.translate("CSVImportPanel", u"Import CSV File", None))
        self.clearButton.setText(QCoreApplication.translate("CSVImportPanel", u"Clear", None))
        self.progressGroup.setTitle(QCoreApplication.translate("CSVImportPanel", u"Import Progress", None))
        self.progressLabel.setText(QCoreApplication.translate("CSVImportPanel", u"Ready to import...", None))
        self.resultsGroup.setTitle(QCoreApplication.translate("CSVImportPanel", u"Import Results", None))
        self.resultsText.setPlaceholderText(QCoreApplication.translate("CSVImportPanel", u"Import results will appear here...", None))
        pass
    # retranslateUi
