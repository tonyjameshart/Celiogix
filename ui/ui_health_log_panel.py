# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'health_log_panel.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDateEdit, QGroupBox,
    QHBoxLayout, QLabel, QPushButton, QRadioButton,
    QScrollArea, QSizePolicy, QSlider, QSpacerItem,
    QSpinBox, QTextEdit, QVBoxLayout, QWidget)

class Ui_HealthLogPanel(object):
    def setupUi(self, HealthLogPanel):
        if not HealthLogPanel.objectName():
            HealthLogPanel.setObjectName(u"HealthLogPanel")
        HealthLogPanel.resize(800, 600)
        self.verticalLayout = QVBoxLayout(HealthLogPanel)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.scrollArea = QScrollArea(HealthLogPanel)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 798, 480))
        self.scrollLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.scrollLayout.setSpacing(15)
        self.scrollLayout.setObjectName(u"scrollLayout")
        self.basicGroup = QGroupBox(self.scrollAreaWidgetContents)
        self.basicGroup.setObjectName(u"basicGroup")
        self.basicLayout = QVBoxLayout(self.basicGroup)
        self.basicLayout.setObjectName(u"basicLayout")
        self.datetimeLayout = QHBoxLayout()
        self.datetimeLayout.setObjectName(u"datetimeLayout")
        self.dateLabel = QLabel(self.basicGroup)
        self.dateLabel.setObjectName(u"dateLabel")

        self.datetimeLayout.addWidget(self.dateLabel)

        self.dateEdit = QDateEdit(self.basicGroup)
        self.dateEdit.setObjectName(u"dateEdit")

        self.datetimeLayout.addWidget(self.dateEdit)

        self.timeLabel = QLabel(self.basicGroup)
        self.timeLabel.setObjectName(u"timeLabel")

        self.datetimeLayout.addWidget(self.timeLabel)

        self.timeCombo = QComboBox(self.basicGroup)
        self.timeCombo.setObjectName(u"timeCombo")
        self.timeCombo.setEditable(True)

        self.datetimeLayout.addWidget(self.timeCombo)


        self.basicLayout.addLayout(self.datetimeLayout)

        self.mealLayout = QHBoxLayout()
        self.mealLayout.setObjectName(u"mealLayout")
        self.mealLabel = QLabel(self.basicGroup)
        self.mealLabel.setObjectName(u"mealLabel")

        self.mealLayout.addWidget(self.mealLabel)

        self.mealCombo = QComboBox(self.basicGroup)
        self.mealCombo.addItem("")
        self.mealCombo.addItem("")
        self.mealCombo.addItem("")
        self.mealCombo.addItem("")
        self.mealCombo.addItem("")
        self.mealCombo.setObjectName(u"mealCombo")

        self.mealLayout.addWidget(self.mealCombo)


        self.basicLayout.addLayout(self.mealLayout)

        self.itemsLayout = QVBoxLayout()
        self.itemsLayout.setObjectName(u"itemsLayout")
        self.itemsLabel = QLabel(self.basicGroup)
        self.itemsLabel.setObjectName(u"itemsLabel")

        self.itemsLayout.addWidget(self.itemsLabel)

        self.itemsEdit = QTextEdit(self.basicGroup)
        self.itemsEdit.setObjectName(u"itemsEdit")
        self.itemsEdit.setMaximumSize(QSize(16777215, 60))

        self.itemsLayout.addWidget(self.itemsEdit)


        self.basicLayout.addLayout(self.itemsLayout)


        self.scrollLayout.addWidget(self.basicGroup)

        self.symptomsGroup = QGroupBox(self.scrollAreaWidgetContents)
        self.symptomsGroup.setObjectName(u"symptomsGroup")
        self.symptomsLayout = QVBoxLayout(self.symptomsGroup)
        self.symptomsLayout.setObjectName(u"symptomsLayout")
        self.riskLayout = QHBoxLayout()
        self.riskLayout.setObjectName(u"riskLayout")
        self.riskLabel = QLabel(self.symptomsGroup)
        self.riskLabel.setObjectName(u"riskLabel")

        self.riskLayout.addWidget(self.riskLabel)

        self.riskCombo = QComboBox(self.symptomsGroup)
        self.riskCombo.addItem("")
        self.riskCombo.addItem("")
        self.riskCombo.addItem("")
        self.riskCombo.addItem("")
        self.riskCombo.setObjectName(u"riskCombo")

        self.riskLayout.addWidget(self.riskCombo)


        self.symptomsLayout.addLayout(self.riskLayout)

        self.onsetLayout = QHBoxLayout()
        self.onsetLayout.setObjectName(u"onsetLayout")
        self.onsetLabel = QLabel(self.symptomsGroup)
        self.onsetLabel.setObjectName(u"onsetLabel")

        self.onsetLayout.addWidget(self.onsetLabel)

        self.onsetSpin = QSpinBox(self.symptomsGroup)
        self.onsetSpin.setObjectName(u"onsetSpin")
        self.onsetSpin.setMinimum(0)
        self.onsetSpin.setMaximum(1440)

        self.onsetLayout.addWidget(self.onsetSpin)

        self.severityLabel = QLabel(self.symptomsGroup)
        self.severityLabel.setObjectName(u"severityLabel")

        self.onsetLayout.addWidget(self.severityLabel)

        self.severitySpin = QSpinBox(self.symptomsGroup)
        self.severitySpin.setObjectName(u"severitySpin")
        self.severitySpin.setMinimum(0)
        self.severitySpin.setMaximum(10)

        self.onsetLayout.addWidget(self.severitySpin)


        self.symptomsLayout.addLayout(self.onsetLayout)

        self.symptomsTextLayout = QVBoxLayout()
        self.symptomsTextLayout.setObjectName(u"symptomsTextLayout")
        self.symptomsTextLabel = QLabel(self.symptomsGroup)
        self.symptomsTextLabel.setObjectName(u"symptomsTextLabel")

        self.symptomsTextLayout.addWidget(self.symptomsTextLabel)

        self.symptomsEdit = QTextEdit(self.symptomsGroup)
        self.symptomsEdit.setObjectName(u"symptomsEdit")
        self.symptomsEdit.setMaximumSize(QSize(16777215, 60))

        self.symptomsTextLayout.addWidget(self.symptomsEdit)


        self.symptomsLayout.addLayout(self.symptomsTextLayout)


        self.scrollLayout.addWidget(self.symptomsGroup)

        self.bristolGroup = QGroupBox(self.scrollAreaWidgetContents)
        self.bristolGroup.setObjectName(u"bristolGroup")
        self.bristolLayout = QVBoxLayout(self.bristolGroup)
        self.bristolLayout.setObjectName(u"bristolLayout")
        self.bristol1Radio = QRadioButton(self.bristolGroup)
        self.bristol1Radio.setObjectName(u"bristol1Radio")

        self.bristolLayout.addWidget(self.bristol1Radio)

        self.bristol2Radio = QRadioButton(self.bristolGroup)
        self.bristol2Radio.setObjectName(u"bristol2Radio")

        self.bristolLayout.addWidget(self.bristol2Radio)

        self.bristol3Radio = QRadioButton(self.bristolGroup)
        self.bristol3Radio.setObjectName(u"bristol3Radio")

        self.bristolLayout.addWidget(self.bristol3Radio)

        self.bristol4Radio = QRadioButton(self.bristolGroup)
        self.bristol4Radio.setObjectName(u"bristol4Radio")
        self.bristol4Radio.setChecked(True)

        self.bristolLayout.addWidget(self.bristol4Radio)

        self.bristol5Radio = QRadioButton(self.bristolGroup)
        self.bristol5Radio.setObjectName(u"bristol5Radio")

        self.bristolLayout.addWidget(self.bristol5Radio)

        self.bristol6Radio = QRadioButton(self.bristolGroup)
        self.bristol6Radio.setObjectName(u"bristol6Radio")

        self.bristolLayout.addWidget(self.bristol6Radio)

        self.bristol7Radio = QRadioButton(self.bristolGroup)
        self.bristol7Radio.setObjectName(u"bristol7Radio")

        self.bristolLayout.addWidget(self.bristol7Radio)


        self.scrollLayout.addWidget(self.bristolGroup)

        self.ggGroup = QGroupBox(self.scrollAreaWidgetContents)
        self.ggGroup.setObjectName(u"ggGroup")
        self.ggLayout = QVBoxLayout(self.ggGroup)
        self.ggLayout.setObjectName(u"ggLayout")
        self.hydrationLayout = QHBoxLayout()
        self.hydrationLayout.setObjectName(u"hydrationLayout")
        self.hydrationLabel = QLabel(self.ggGroup)
        self.hydrationLabel.setObjectName(u"hydrationLabel")

        self.hydrationLayout.addWidget(self.hydrationLabel)

        self.hydrationSpin = QSpinBox(self.ggGroup)
        self.hydrationSpin.setObjectName(u"hydrationSpin")
        self.hydrationSpin.setMinimum(0)
        self.hydrationSpin.setMaximum(10)

        self.hydrationLayout.addWidget(self.hydrationSpin)

        self.fiberLabel = QLabel(self.ggGroup)
        self.fiberLabel.setObjectName(u"fiberLabel")

        self.hydrationLayout.addWidget(self.fiberLabel)

        self.fiberSpin = QSpinBox(self.ggGroup)
        self.fiberSpin.setObjectName(u"fiberSpin")
        self.fiberSpin.setMinimum(0)
        self.fiberSpin.setMaximum(100)

        self.hydrationLayout.addWidget(self.fiberSpin)


        self.ggLayout.addLayout(self.hydrationLayout)

        self.moodLayout = QHBoxLayout()
        self.moodLayout.setObjectName(u"moodLayout")
        self.moodLabel = QLabel(self.ggGroup)
        self.moodLabel.setObjectName(u"moodLabel")

        self.moodLayout.addWidget(self.moodLabel)

        self.moodCombo = QComboBox(self.ggGroup)
        self.moodCombo.addItem("")
        self.moodCombo.addItem("")
        self.moodCombo.addItem("")
        self.moodCombo.addItem("")
        self.moodCombo.addItem("")
        self.moodCombo.setObjectName(u"moodCombo")

        self.moodLayout.addWidget(self.moodCombo)


        self.ggLayout.addLayout(self.moodLayout)

        self.energyLayout = QVBoxLayout()
        self.energyLayout.setObjectName(u"energyLayout")
        self.energyLabel = QLabel(self.ggGroup)
        self.energyLabel.setObjectName(u"energyLabel")

        self.energyLayout.addWidget(self.energyLabel)

        self.energySlider = QSlider(self.ggGroup)
        self.energySlider.setObjectName(u"energySlider")
        self.energySlider.setOrientation(Qt.Horizontal)
        self.energySlider.setMinimum(1)
        self.energySlider.setMaximum(10)
        self.energySlider.setValue(5)
        self.energySlider.setTickPosition(QSlider.TicksBelow)
        self.energySlider.setTickInterval(1)

        self.energyLayout.addWidget(self.energySlider)

        self.energyValueLabel = QLabel(self.ggGroup)
        self.energyValueLabel.setObjectName(u"energyValueLabel")
        self.energyValueLabel.setAlignment(Qt.AlignCenter)

        self.energyLayout.addWidget(self.energyValueLabel)


        self.ggLayout.addLayout(self.energyLayout)


        self.scrollLayout.addWidget(self.ggGroup)

        self.notesGroup = QGroupBox(self.scrollAreaWidgetContents)
        self.notesGroup.setObjectName(u"notesGroup")
        self.notesLayout = QVBoxLayout(self.notesGroup)
        self.notesLayout.setObjectName(u"notesLayout")
        self.notesEdit = QTextEdit(self.notesGroup)
        self.notesEdit.setObjectName(u"notesEdit")
        self.notesEdit.setMaximumSize(QSize(16777215, 80))

        self.notesLayout.addWidget(self.notesEdit)


        self.scrollLayout.addWidget(self.notesGroup)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.saveButton = QPushButton(HealthLogPanel)
        self.saveButton.setObjectName(u"saveButton")

        self.buttonLayout.addWidget(self.saveButton)

        self.clearButton = QPushButton(HealthLogPanel)
        self.clearButton.setObjectName(u"clearButton")

        self.buttonLayout.addWidget(self.clearButton)

        self.analyzeButton = QPushButton(HealthLogPanel)
        self.analyzeButton.setObjectName(u"analyzeButton")

        self.buttonLayout.addWidget(self.analyzeButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.buttonLayout)


        self.retranslateUi(HealthLogPanel)

        QMetaObject.connectSlotsByName(HealthLogPanel)
    # setupUi

    def retranslateUi(self, HealthLogPanel):
        self.basicGroup.setTitle(QCoreApplication.translate("HealthLogPanel", u"Basic Information", None))
        self.dateLabel.setText(QCoreApplication.translate("HealthLogPanel", u"Date:", None))
        self.timeLabel.setText(QCoreApplication.translate("HealthLogPanel", u"Time:", None))
        self.mealLabel.setText(QCoreApplication.translate("HealthLogPanel", u"Meal Type:", None))
        self.mealCombo.setItemText(0, QCoreApplication.translate("HealthLogPanel", u"Breakfast", None))
        self.mealCombo.setItemText(1, QCoreApplication.translate("HealthLogPanel", u"Lunch", None))
        self.mealCombo.setItemText(2, QCoreApplication.translate("HealthLogPanel", u"Dinner", None))
        self.mealCombo.setItemText(3, QCoreApplication.translate("HealthLogPanel", u"Snack", None))
        self.mealCombo.setItemText(4, QCoreApplication.translate("HealthLogPanel", u"Other", None))

        self.itemsLabel.setText(QCoreApplication.translate("HealthLogPanel", u"Items Consumed:", None))
        self.itemsEdit.setPlaceholderText(QCoreApplication.translate("HealthLogPanel", u"Enter items consumed...", None))
        self.symptomsGroup.setTitle(QCoreApplication.translate("HealthLogPanel", u"Symptoms & Assessment", None))
        self.riskLabel.setText(QCoreApplication.translate("HealthLogPanel", u"Risk Level:", None))
        self.riskCombo.setItemText(0, QCoreApplication.translate("HealthLogPanel", u"none", None))
        self.riskCombo.setItemText(1, QCoreApplication.translate("HealthLogPanel", u"low", None))
        self.riskCombo.setItemText(2, QCoreApplication.translate("HealthLogPanel", u"med", None))
        self.riskCombo.setItemText(3, QCoreApplication.translate("HealthLogPanel", u"high", None))

        self.onsetLabel.setText(QCoreApplication.translate("HealthLogPanel", u"Onset (minutes):", None))
        self.severityLabel.setText(QCoreApplication.translate("HealthLogPanel", u"Severity (0-10):", None))
        self.symptomsTextLabel.setText(QCoreApplication.translate("HealthLogPanel", u"Symptoms:", None))
        self.symptomsEdit.setPlaceholderText(QCoreApplication.translate("HealthLogPanel", u"Describe symptoms...", None))
        self.bristolGroup.setTitle(QCoreApplication.translate("HealthLogPanel", u"Bristol Stool Scale", None))
        self.bristol1Radio.setText(QCoreApplication.translate("HealthLogPanel", u"1 - Separate hard lumps (constipation)", None))
        self.bristol2Radio.setText(QCoreApplication.translate("HealthLogPanel", u"2 - Lumpy sausage", None))
        self.bristol3Radio.setText(QCoreApplication.translate("HealthLogPanel", u"3 - Cracked sausage", None))
        self.bristol4Radio.setText(QCoreApplication.translate("HealthLogPanel", u"4 - Smooth sausage (normal)", None))
        self.bristol5Radio.setText(QCoreApplication.translate("HealthLogPanel", u"5 - Soft blobs", None))
        self.bristol6Radio.setText(QCoreApplication.translate("HealthLogPanel", u"6 - Fluffy pieces", None))
        self.bristol7Radio.setText(QCoreApplication.translate("HealthLogPanel", u"7 - Watery (diarrhea)", None))
        self.ggGroup.setTitle(QCoreApplication.translate("HealthLogPanel", u"Gluten Guardian Tracking", None))
        self.hydrationLabel.setText(QCoreApplication.translate("HealthLogPanel", u"Hydration (L):", None))
        self.hydrationSpin.setSuffix(QCoreApplication.translate("HealthLogPanel", u" L", None))
        self.fiberLabel.setText(QCoreApplication.translate("HealthLogPanel", u"Fiber (g):", None))
        self.fiberSpin.setSuffix(QCoreApplication.translate("HealthLogPanel", u" g", None))
        self.moodLabel.setText(QCoreApplication.translate("HealthLogPanel", u"Mood:", None))
        self.moodCombo.setItemText(0, QCoreApplication.translate("HealthLogPanel", u"\U0001f60a", None))
        self.moodCombo.setItemText(1, QCoreApplication.translate("HealthLogPanel", u"\U0001f610", None))
        self.moodCombo.setItemText(2, QCoreApplication.translate("HealthLogPanel", u"\U0001f623", None))
        self.moodCombo.setItemText(3, QCoreApplication.translate("HealthLogPanel", u"\U0001f622", None))
        self.moodCombo.setItemText(4, QCoreApplication.translate("HealthLogPanel", u"\U0001f621", None))

        self.energyLabel.setText(QCoreApplication.translate("HealthLogPanel", u"Energy Level (1-10):", None))
        self.energyValueLabel.setText(QCoreApplication.translate("HealthLogPanel", u"5", None))
        self.notesGroup.setTitle(QCoreApplication.translate("HealthLogPanel", u"Notes", None))
        self.notesEdit.setPlaceholderText(QCoreApplication.translate("HealthLogPanel", u"Additional notes...", None))
        self.saveButton.setText(QCoreApplication.translate("HealthLogPanel", u"Save Entry", None))
        self.clearButton.setText(QCoreApplication.translate("HealthLogPanel", u"Clear Form", None))
        self.analyzeButton.setText(QCoreApplication.translate("HealthLogPanel", u"Analyze Patterns", None))
        pass
    # retranslateUi

