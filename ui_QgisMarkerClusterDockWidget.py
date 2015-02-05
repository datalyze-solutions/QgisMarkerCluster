# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_QgisMarkerClusterDockWidget.ui'
#
# Created: Thu Feb  5 14:51:37 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_QgisMarkerClusterDockWidget(object):
    def setupUi(self, QgisMarkerClusterDockWidget):
        QgisMarkerClusterDockWidget.setObjectName(_fromUtf8("QgisMarkerClusterDockWidget"))
        QgisMarkerClusterDockWidget.resize(274, 293)
        QgisMarkerClusterDockWidget.setMinimumSize(QtCore.QSize(0, 0))
        QgisMarkerClusterDockWidget.setMaximumSize(QtCore.QSize(16777215, 293))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonLoadTestDataset = QtGui.QToolButton(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonLoadTestDataset.sizePolicy().hasHeightForWidth())
        self.buttonLoadTestDataset.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/list-add.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonLoadTestDataset.setIcon(icon)
        self.buttonLoadTestDataset.setIconSize(QtCore.QSize(22, 22))
        self.buttonLoadTestDataset.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.buttonLoadTestDataset.setObjectName(_fromUtf8("buttonLoadTestDataset"))
        self.gridLayout.addWidget(self.buttonLoadTestDataset, 0, 0, 1, 1)
        self.buttonInfo = QtGui.QToolButton(self.dockWidgetContents)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/help-about.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonInfo.setIcon(icon1)
        self.buttonInfo.setIconSize(QtCore.QSize(22, 22))
        self.buttonInfo.setObjectName(_fromUtf8("buttonInfo"))
        self.gridLayout.addWidget(self.buttonInfo, 0, 2, 1, 1)
        self.buttonClusterPoints = QtGui.QToolButton(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonClusterPoints.sizePolicy().hasHeightForWidth())
        self.buttonClusterPoints.setSizePolicy(sizePolicy)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonClusterPoints.setIcon(icon2)
        self.buttonClusterPoints.setIconSize(QtCore.QSize(24, 24))
        self.buttonClusterPoints.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.buttonClusterPoints.setObjectName(_fromUtf8("buttonClusterPoints"))
        self.gridLayout.addWidget(self.buttonClusterPoints, 1, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 1, 1, 1)
        self.verticalLayout_3.addLayout(self.gridLayout)
        self.groupBox = QtGui.QGroupBox(self.dockWidgetContents)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.lineEditClusterShapePath = QtGui.QLineEdit(self.groupBox)
        self.lineEditClusterShapePath.setReadOnly(True)
        self.lineEditClusterShapePath.setObjectName(_fromUtf8("lineEditClusterShapePath"))
        self.verticalLayout_2.addWidget(self.lineEditClusterShapePath)
        self.buttonLoadClusterDataset = QtGui.QToolButton(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonLoadClusterDataset.sizePolicy().hasHeightForWidth())
        self.buttonLoadClusterDataset.setSizePolicy(sizePolicy)
        self.buttonLoadClusterDataset.setIcon(icon)
        self.buttonLoadClusterDataset.setIconSize(QtCore.QSize(22, 22))
        self.buttonLoadClusterDataset.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.buttonLoadClusterDataset.setObjectName(_fromUtf8("buttonLoadClusterDataset"))
        self.verticalLayout_2.addWidget(self.buttonLoadClusterDataset)
        self.verticalLayout_3.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(self.dockWidgetContents)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.doubleSpinBoxClusterDistance = QtGui.QDoubleSpinBox(self.groupBox_2)
        self.doubleSpinBoxClusterDistance.setSuffix(_fromUtf8(""))
        self.doubleSpinBoxClusterDistance.setDecimals(4)
        self.doubleSpinBoxClusterDistance.setMinimum(0.0)
        self.doubleSpinBoxClusterDistance.setMaximum(999999999.0)
        self.doubleSpinBoxClusterDistance.setProperty("value", 50.0)
        self.doubleSpinBoxClusterDistance.setObjectName(_fromUtf8("doubleSpinBoxClusterDistance"))
        self.verticalLayout.addWidget(self.doubleSpinBoxClusterDistance)
        self.verticalLayout_3.addWidget(self.groupBox_2)
        QgisMarkerClusterDockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(QgisMarkerClusterDockWidget)
        QtCore.QMetaObject.connectSlotsByName(QgisMarkerClusterDockWidget)

    def retranslateUi(self, QgisMarkerClusterDockWidget):
        QgisMarkerClusterDockWidget.setWindowTitle(_translate("QgisMarkerClusterDockWidget", "Qgis Marker Cluster", None))
        self.buttonLoadTestDataset.setToolTip(_translate("QgisMarkerClusterDockWidget", "load selected dataset", None))
        self.buttonLoadTestDataset.setStatusTip(_translate("QgisMarkerClusterDockWidget", "load selected dataset", None))
        self.buttonLoadTestDataset.setText(_translate("QgisMarkerClusterDockWidget", "1. Load Point Layer", None))
        self.buttonInfo.setToolTip(_translate("QgisMarkerClusterDockWidget", "Show information", None))
        self.buttonInfo.setStatusTip(_translate("QgisMarkerClusterDockWidget", "Show information", None))
        self.buttonInfo.setText(_translate("QgisMarkerClusterDockWidget", "OSM", None))
        self.buttonClusterPoints.setToolTip(_translate("QgisMarkerClusterDockWidget", "Show information", None))
        self.buttonClusterPoints.setStatusTip(_translate("QgisMarkerClusterDockWidget", "Cluster Points", None))
        self.buttonClusterPoints.setText(_translate("QgisMarkerClusterDockWidget", "2. Setup First Cluster", None))
        self.groupBox.setTitle(_translate("QgisMarkerClusterDockWidget", "Cluster Shape", None))
        self.buttonLoadClusterDataset.setToolTip(_translate("QgisMarkerClusterDockWidget", "load selected dataset", None))
        self.buttonLoadClusterDataset.setStatusTip(_translate("QgisMarkerClusterDockWidget", "add cluster shape", None))
        self.buttonLoadClusterDataset.setText(_translate("QgisMarkerClusterDockWidget", "3. Add more cluster shapes", None))
        self.groupBox_2.setTitle(_translate("QgisMarkerClusterDockWidget", "Cluster Distance", None))

import resources_rc
