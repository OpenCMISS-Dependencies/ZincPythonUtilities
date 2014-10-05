# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'zincinteractivewidget.ui'
#
# Created: Tue Sep 23 15:04:49 2014
#      by: PyQt4 UI code generator 4.10.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

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

class Ui_ZincInteractiveDialog(object):
    def setupUi(self, zincInteractiveDialog):
        zincInteractiveDialog.setObjectName(_fromUtf8("zincInteractiveDialog"))
        zincInteractiveDialog.resize(161, 199)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(zincInteractiveDialog.sizePolicy().hasHeightForWidth())
        zincInteractiveDialog.setSizePolicy(sizePolicy)
        self.linesSelection = QtGui.QCheckBox(zincInteractiveDialog)
        self.linesSelection.setGeometry(QtCore.QRect(20, 110, 94, 22))
        self.linesSelection.setObjectName(_fromUtf8("linesSelection"))
        self.surfacesSelection = QtGui.QCheckBox(zincInteractiveDialog)
        self.surfacesSelection.setGeometry(QtCore.QRect(20, 140, 94, 22))
        self.surfacesSelection.setObjectName(_fromUtf8("surfacesSelection"))
        self.nodeSelectionWidget = QtGui.QWidget(zincInteractiveDialog)
        self.nodeSelectionWidget.setEnabled(True)
        self.nodeSelectionWidget.setGeometry(QtCore.QRect(20, 30, 121, 71))
        self.nodeSelectionWidget.setObjectName(_fromUtf8("nodeSelectionWidget"))
        self.enableSelection = QtGui.QCheckBox(self.nodeSelectionWidget)
        self.enableSelection.setGeometry(QtCore.QRect(10, 0, 94, 22))
        self.enableSelection.setChecked(False)
        self.enableSelection.setObjectName(_fromUtf8("enableSelection"))
        self.enableEdit = QtGui.QCheckBox(self.nodeSelectionWidget)
        self.enableEdit.setGeometry(QtCore.QRect(10, 20, 94, 22))
        self.enableEdit.setObjectName(_fromUtf8("enableEdit"))
        self.enableCreate = QtGui.QCheckBox(self.nodeSelectionWidget)
        self.enableCreate.setGeometry(QtCore.QRect(10, 40, 94, 22))
        self.enableCreate.setObjectName(_fromUtf8("enableCreate"))
        self.line = QtGui.QFrame(zincInteractiveDialog)
        self.line.setGeometry(QtCore.QRect(20, 90, 118, 16))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.nodeLabel = QtGui.QLabel(zincInteractiveDialog)
        self.nodeLabel.setGeometry(QtCore.QRect(20, 10, 62, 17))
        self.nodeLabel.setObjectName(_fromUtf8("nodeLabel"))

        self.retranslateUi(zincInteractiveDialog)
        QtCore.QMetaObject.connectSlotsByName(zincInteractiveDialog)

    def retranslateUi(self, zincInteractiveDialog):
        zincInteractiveDialog.setWindowTitle(_translate("zincInteractiveDialog", "Dialog", None))
        self.linesSelection.setText(_translate("zincInteractiveDialog", "Lines", None))
        self.surfacesSelection.setText(_translate("zincInteractiveDialog", "Surfaces", None))
        self.enableSelection.setText(_translate("zincInteractiveDialog", "Select", None))
        self.enableEdit.setText(_translate("zincInteractiveDialog", "Edit", None))
        self.enableCreate.setText(_translate("zincInteractiveDialog", "Create", None))
        self.nodeLabel.setText(_translate("zincInteractiveDialog", "Nodes", None))

