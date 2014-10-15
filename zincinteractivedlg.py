#!/usr/bin/python
"""
PyZinc examples

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

Created on Mar 27, 2013

@author: hsorby
"""

import sys
try:
    from PySide import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui
from ui_zincinteractivewidget import Ui_ZincInteractiveDialog

# from opencmiss.zinc.glyph import Glyph
from opencmiss.zinc.sceneviewer import Sceneviewer, Sceneviewerevent
from opencmiss.zinc.sceneviewerinput import Sceneviewerinput
from opencmiss.zinc.scenecoordinatesystem import \
        SCENECOORDINATESYSTEM_LOCAL, \
        SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT,\
        SCENECOORDINATESYSTEM_WORLD
from opencmiss.zinc.field import Field
from opencmiss.zinc.glyph import Glyph
from opencmiss.zinc.status import OK

# mapping from qt to zinc start
# Create a button map of Qt mouse buttons to Zinc input buttons
button_map = {QtCore.Qt.LeftButton: Sceneviewerinput.BUTTON_TYPE_LEFT,
              QtCore.Qt.MidButton: Sceneviewerinput.BUTTON_TYPE_MIDDLE,
              QtCore.Qt.RightButton: Sceneviewerinput.BUTTON_TYPE_RIGHT}

# Create a modifier map of Qt modifier keys to Zinc modifier keys
def modifier_map(qt_modifiers):
    '''
    Return a Zinc SceneViewerInput modifiers object that is created from
    the Qt modifier flags passed in.
    '''
    modifiers = Sceneviewerinput.MODIFIER_FLAG_NONE
    if qt_modifiers & QtCore.Qt.SHIFT:
        modifiers = modifiers | Sceneviewerinput.MODIFIER_FLAG_SHIFT

    return modifiers
# mapping from qt to zinc end

SELECTION_RUBBERBAND_NAME = 'selection_rubberband'

# selectionMode start
class SelectionMode(object):

    NONE = -1
    EXCLUSIVE = 0
    ADDITIVE = 1
# selectionMode end

class ZincInteractiveDlg(QtGui.QWidget):
    
    def __init__(self, parent=None):
        '''
        Initiaise the interactive dialog first calling the QWidget __init__ function.
        '''
        QtGui.QWidget.__init__(self, parent)
        
        # Using composition to include the visual element of the GUI.
        self.ui = Ui_ZincInteractiveDialog()
        self.ui.setupUi(self)
#        self.setWindowIcon(QtGui.QIcon(":/cmiss_icon.ico"))

        self.ui.linesSelection.stateChanged.connect(self.lineSelectionToggle)
        self.ui.surfacesSelection.stateChanged.connect(self.surfacesSelectionToggle)
        self.ui.enableSelection.stateChanged.connect(self.enableSelectionToggle)
        self.ui.enableEdit.stateChanged.connect(self.enableEditToggle)
        self.ui.enableCreate.stateChanged.connect(self.enableCreateToggle)
        self.ui.enableConstrain.stateChanged.connect(self.enableConstrainToggle)
             
    def enableSelectionToggle(self):
        self.interactiveTool.setNodeSelection(self.ui.enableSelection.isChecked())
                       
    def enableEditToggle(self):
        self.interactiveTool.setNodeEdit(self.ui.enableEdit.isChecked())
            
    def enableCreateToggle(self):
        self.interactiveTool.setNodeCreateMode(self.ui.enableCreate.isChecked())
        
    def enableConstrainToggle(self):
        self.interactiveTool.setNodeConstrainToSurfacesMode(self.ui.enableConstrain.isChecked())
    
    def lineSelectionToggle(self):
        self.interactiveTool.setLineSelection(self.ui.linesSelection.isChecked())
            
    def surfacesSelectionToggle(self):
        self.interactiveTool.setSurfacesSelection(self.ui.surfacesSelection.isChecked())
    
    def initializeInteractiveDlg(self, interactiveTool):
        self.interactiveTool = interactiveTool
