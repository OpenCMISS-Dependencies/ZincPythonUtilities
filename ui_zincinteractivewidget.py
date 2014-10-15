# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'zincinteractivewidget.ui'
#
# Created: Tue Oct  7 11:20:02 2014
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
    def setupUi(self, ZincInteractiveDialog):
        ZincInteractiveDialog.setObjectName(_fromUtf8("ZincInteractiveDialog"))
        ZincInteractiveDialog.resize(225, 186)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ZincInteractiveDialog.sizePolicy().hasHeightForWidth())
        ZincInteractiveDialog.setSizePolicy(sizePolicy)
        self.linesSelection = QtGui.QCheckBox(ZincInteractiveDialog)
        self.linesSelection.setGeometry(QtCore.QRect(20, 130, 94, 22))
        self.linesSelection.setObjectName(_fromUtf8("linesSelection"))
        self.surfacesSelection = QtGui.QCheckBox(ZincInteractiveDialog)
        self.surfacesSelection.setGeometry(QtCore.QRect(20, 150, 94, 22))
        self.surfacesSelection.setObjectName(_fromUtf8("surfacesSelection"))
        self.nodeSelectionWidget = QtGui.QWidget(ZincInteractiveDialog)
        self.nodeSelectionWidget.setEnabled(True)
        self.nodeSelectionWidget.setGeometry(QtCore.QRect(20, 30, 181, 91))
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
        self.enableConstrain = QtGui.QCheckBox(self.nodeSelectionWidget)
        self.enableConstrain.setGeometry(QtCore.QRect(10, 60, 161, 21))
        self.enableConstrain.setObjectName(_fromUtf8("enableConstrain"))
        self.line = QtGui.QFrame(ZincInteractiveDialog)
        self.line.setGeometry(QtCore.QRect(20, 120, 181, 16))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.nodeLabel = QtGui.QLabel(ZincInteractiveDialog)
        self.nodeLabel.setGeometry(QtCore.QRect(20, 10, 62, 17))
        self.nodeLabel.setObjectName(_fromUtf8("nodeLabel"))

        self.retranslateUi(ZincInteractiveDialog)
        QtCore.QMetaObject.connectSlotsByName(ZincInteractiveDialog)

    def retranslateUi(self, ZincInteractiveDialog):
        ZincInteractiveDialog.setWindowTitle(_translate("ZincInteractiveDialog", "Dialog", None))
        self.linesSelection.setText(_translate("ZincInteractiveDialog", "Lines", None))
        self.surfacesSelection.setText(_translate("ZincInteractiveDialog", "Surfaces", None))
        self.enableSelection.setText(_translate("ZincInteractiveDialog", "Select", None))
        self.enableEdit.setText(_translate("ZincInteractiveDialog", "Edit", None))
        self.enableCreate.setText(_translate("ZincInteractiveDialog", "Create", None))
        self.enableConstrain.setText(_translate("ZincInteractiveDialog", "Constrain to surfaces", None))
        self.nodeLabel.setText(_translate("ZincInteractiveDialog", "Nodes", None))

