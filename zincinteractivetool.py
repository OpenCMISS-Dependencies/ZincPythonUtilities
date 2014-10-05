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
import math


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
    EDIT_POSITION = 2
    EDIT_VECTOR = 3
# selectionMode end

class ZincInteractiveTool():
    
    def __init__(self, zincwidget):
        
        # Selection attributes
        self._nodeSelectMode = False
        self._nodeEditMode = False
        self._nodeEditVectorMode = True
        self._nodeCreateMode = False
        self._dataSelectMode = False
        self._1delemSelectMode = False
        self._2delemSelectMode = False
        self._elemSelectMode = False
        self._selection_mode = SelectionMode.NONE
        self._selectionGroup = None
        self._selection_box = None
        self._ignore_mouse_events = False
        self._editModifier = QtCore.Qt.CTRL
        self._editReferenceNode = None
        self._editGraphics = None
        self._selectedCoordinateField = None
        self._selectedOrientationField = None
        self._sceneviewer = None
        self._zincwidget = zincwidget
        self._variable_scale_field = None;
        self._editGlyphCentre = [0.0, 0.0, 0.0]
        self._editGlyphSize = [0.0, 0.0, 0.0]
        self._editGlyphScaleFactors = [0.0, 0.0, 0.0]
        self._editVariableScaleField = Field()
                                       
    def setSceneviewer(self, sceneviewer):    
        self._sceneviewer = sceneviewer
        if self._sceneviewer.isValid():
            scene = self._sceneviewer.getScene()
            graphics_filter = self._sceneviewer.getScenefilter()
            self._scenepicker = scene.createScenepicker()
            region = scene.getRegion()

            fieldmodule = region.getFieldmodule()

            self._selectionGroup = fieldmodule.createFieldGroup()
            scene.setSelectionField(self._selectionGroup)

            self._scenepicker = scene.createScenepicker()
            self._scenepicker.setScenefilter(graphics_filter)

            # If the standard glyphs haven't been defined then the
            # selection box will not be visible
            self.createSelectionBox(scene)

    def setNodeSelection(self, enabled):
        self._nodeSelectMode = enabled
                           
    def setNodeEdit(self, enabled):
        self._nodeEditMode = enabled
        
    def setNodeCreateMode(self, enabled):
        self._nodeCreateMode = enabled
        
    def setSelectionModeAdditive(self):
        self._selectionAlwaysAdditive = True
        
    def setLineSelection(self, enabled):
        self._1delemSelectMode = enabled
        
    def setSurfacesSelection(self, enabled):
        self._2delemSelectMode = enabled

    def setSelectModeAll(self):
        self._nodeSelectMode = True
        self._dataSelectMode = True
        self._elemSelectMode = True
        
    def createSelectionBox(self, scene):
        if self._selection_box:
            previousScene = self._selection_box.getScene()
            previousScene.removeGraphics(self._selection_box)
        
        self._selection_box = scene.createGraphicsPoints()
        self._selection_box.setName(SELECTION_RUBBERBAND_NAME)
        self._selection_box.setScenecoordinatesystem(SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT)
        
        attributes = self._selection_box.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_CUBE_WIREFRAME)
        attributes.setBaseSize([10, 10, 0.9999])
        attributes.setGlyphOffset([1, -1, 0])
        self._selectionBox_setBaseSize = attributes.setBaseSize
        self._selectionBox_setGlyphOffset = attributes.setGlyphOffset   
        self._selection_box.setVisibilityFlag(False)
    
    def getScenefilter(self):
        result, scenefilter = self._sceneviewer.getScenefilter()
        if result == OK:
            return scenefilter
        return None

    def setScenefilter(self, scenefilter):
        self._sceneviewer.setScenefilter(scenefilter)

    def getScenepicker(self):
        return self._scenepicker

    def setPickingRectangle(self, coordinate_system, left, bottom, right, top):
        self._scenepicker.setSceneviewerRectangle(self._sceneviewer, coordinate_system, left, bottom, right, top);

    def setSelectionfilter(self, scenefilter):
        self._scenepicker.setScenefilter(scenefilter)

    def getSelectionfilter(self):
        result, scenefilter = self._scenepicker.getScenefilter()
        if result == OK:
            return scenefilter
        return None
    
    def setScene(self, scene):
        scenefilter = self._scenepicker.getScenefilter()
        self._scenepicker = scene.createScenepicker()
        self._scenepicker.setScenefilter(scenefilter)
        self.createSelectionBox(scene)
        
    def _getNearestGraphic(self, x, y, domain_type):
        self._scenepicker.setSceneviewerRectangle(self._sceneviewer, SCENECOORDINATESYSTEM_LOCAL, x - 0.5, y - 0.5, x + 0.5, y + 0.5)
        nearest_graphics = self._scenepicker.getNearestGraphics()
        if nearest_graphics.isValid() and nearest_graphics.getFieldDomainType() == domain_type:
            return nearest_graphics

        return None

    def getNeareshGraphics(self):
        return self._scenepicker.getNearestGraphics()

    def getNearestGraphicsNode(self, x, y):
        return self._getNearestGraphic(x, y, Field.DOMAIN_TYPE_NODES)

    def getNearestGraphicsPoint(self, x, y):
        '''
        Assuming given x and y is in the sending widgets coordinates 
        which is a parent of this widget.  For example the values given 
        directly from the event in the parent widget.
        '''
        return self._getNearestGraphic(x, y, Field.DOMAIN_TYPE_POINT)

    def getNearestNode(self, x, y):
        self._scenepicker.setSceneviewerRectangle(self._sceneviewer, SCENECOORDINATESYSTEM_LOCAL, x - 0.5, y - 0.5, x + 0.5, y + 0.5)
        node = self._scenepicker.getNearestNode()

        return node

    def addPickedNodesToFieldGroup(self, selection_group):
        self._scenepicker.addPickedNodesToFieldGroup(selection_group)

    def setIgnoreMouseEvents(self, value):
        self._ignore_mouse_events = value
        
    def createCoordinatesVectorsGraphics(self, scene, coordinateField, valueLabel, \
                                             versionNumber, baseSizes, scaleFactors, selectMode, \
                                             material, selectedMaterial):
        fieldmodule = scene.getRegion().getFieldmodule()
        derivativeField =  fieldmodule.createFieldNodeValue(coordinateField, valueLabel, versionNumber)
        if derivativeField.isValid():
            nodes = scene.createGraphicsPoints()
            nodes.setCoordinateField(coordinateField)
            nodes.setFieldDomainType(Field.DOMAIN_TYPE_NODES)
            nodes.setSelectMode(selectMode)
            nodes.setMaterial(material)
            nodes.setSelectedMaterial(selectedMaterial)
            attributes = nodes.getGraphicspointattributes()
            attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_ARROW_SOLID)
            attributes.setBaseSize(baseSizes)
            attributes.setScaleFactors(scaleFactors)
            attributes.setOrientationScaleField(derivativeField)
            #gfx modify g_element bicubic_linear node_points coordinate coordinates glyph arrow_solid size "0*0.1*0.1" scale_factors "0.5*0*0" orientation dx_ds1 mat gold selected_mat gold draw_selected
        return None
    
    def makeGlyphOrientationScaleAxes(self, orientationScaleValues):
        num = len(orientationScaleValues)
        size = [0.0, 0.0, 0.0]
        axis1 = [0.0, 0.0, 0.0]
        axis2 = [0.0, 0.0, 0.0]
        axis3 = [0.0, 0.0, 0.0]
        if num == 0:
            size = [0.0, 0.0, 0.0]
            axis1 = [1.0, 0.0, 0.0]
            axis2 = [0.0, 1.0, 0.0]
            axis3 = [0.0, 0.0, 1.0]
        elif num == 1:
            size = [orientationScaleValues[0], orientationScaleValues[1],orientationScaleValues[2]];
            axis1 = [1.0, 0.0, 0.0]
            axis2 = [0.0, 1.0, 0.0]
            axis3 = [0.0, 0.0, 1.0]
        elif num == 2:
            axis1 = [orientationScaleValues[0], orientationScaleValues[1], 0.0]
            magnitude = math.sqrt(axis1[0]*axis1[0]+axis1[1]*axis1[1])
            if magnitude > 0.0:
                axis1[0] /= magnitude
                axis1[1] /= magnitude                
            size = [magnitude, magnitude, magnitude] 
            axis2 = [-axis1[1], axis1[0], 0.0]
            axis3 = [0.0, 0.0, 1.0];
        elif num == 3:
            axis1 = orientationScaleValues
            magnitude = math.sqrt(axis1[0]*axis1[0]+axis1[1]*axis1[1]+axis1[2]*axis1[2])
            if magnitude > 0.0:
                axis1[0] /= magnitude
                axis1[1] /= magnitude
                axis1[2] /= magnitude 
                size = [magnitude, magnitude, magnitude]
                axis3 = [0.0, 0.0, 0.0]
                if math.fabs(axis1[0]) < math.fabs(axis1[1]):
                    if math.fabs(axis1[2]) < math.fabs(axis1[0]):
                        axis3[2]=1.0
                    else:
                        axis3[0]=1.0
                else:
                    if math.fabs(axis1[2]) < math.fabs(axis1[1]):
                        axis3[2]=1.0
                    else:
                        axis3[1]=1.0
                axis2[0]=axis3[1]*axis1[2]-axis3[2]*axis1[1]
                axis2[1]=axis3[2]*axis1[0]-axis3[0]*axis1[2]
                axis2[2]=axis3[0]*axis1[1]-axis3[1]*axis1[0]
                magnitude=math.sqrt(axis2[0]*axis2[0]+axis2[1]*axis2[1]+axis2[2]*axis2[2])
                axis2[0] /= magnitude
                axis2[1] /= magnitude
                axis2[2] /= magnitude
                axis3[0]=axis1[1]*axis2[2]-axis1[2]*axis2[1]
                axis3[1]=axis1[2]*axis2[0]-axis1[0]*axis2[2]
                axis3[2]=axis1[0]*axis2[1]-axis1[1]*axis2[0]
            else:
                axis2=[0.0, 0.0, 0.0]
                axis3=[0.0, 0.0, 0.0]
                size=[0.0, 0.0, 0.0]
        elif num == 4 or num == 6:
            if num == 4:
                axis1 = [orientationScaleValues[0], orientationScaleValues[1], 0.0]
                axis2 = [orientationScaleValues[2], orientationScaleValues[3], 0.0]
            else:
                axis1 = [orientationScaleValues[0], orientationScaleValues[1], orientationScaleValues[2]]
                axis2 = [orientationScaleValues[3], orientationScaleValues[4], orientationScaleValues[5]]
            axis3[0]=axis1[1]*axis2[2]-axis1[2]*axis2[1]
            axis3[1]=axis1[2]*axis2[0]-axis1[0]*axis2[2]
            axis3[2]=axis1[0]*axis2[1]-axis1[1]*axis2[0]
            magnitude=math.sqrt(axis1[0]*axis1[0]+axis1[1]*axis1[1]+axis1[2]*axis1[2])
            if magnitude > 0.0:
                axis1[0] /= magnitude
                axis1[1] /= magnitude
                axis1[2] /= magnitude
            size[0]=magnitude;
            magnitude=math.sqrt(axis2[0]*axis2[0]+axis2[1]*axis2[1]+axis2[2]*axis2[2])
            if magnitude > 0.0:
                axis2[0] /= magnitude
                axis2[1] /= magnitude
                axis2[2] /= magnitude
            size[1]=magnitude;
            magnitude=math.sqrt(axis3[0]*axis3[0]+axis3[1]*axis3[1]+axis3[2]*axis3[2])
            if magnitude > 0.0:
                axis3[0] /= magnitude
                axis3[1] /= magnitude
                axis3[2] /= magnitude
            size[2]=magnitude;
        elif num == 9:
            axis1=[orientationScaleValues[0],orientationScaleValues[1],orientationScaleValues[2]]
            magnitude=math.sqrt(axis1[0]*axis1[0]+axis1[1]*axis1[1]+axis1[2]*axis1[2])
            if magnitude > 0.0:
                axis1[0] /= magnitude
                axis1[1] /= magnitude
                axis1[2] /= magnitude   
            size[0]=magnitude;
            axis2=[orientationScaleValues[3],orientationScaleValues[4],orientationScaleValues[5]]
            magnitude=math.sqrt(axis2[0]*axis2[0]+axis2[1]*axis2[1]+axis2[2]*axis2[2])
            if magnitude > 0.0:
                axis2[0] /= magnitude
                axis2[1] /= magnitude
                axis2[2] /= magnitude   
            size[1]=magnitude
            axis3=[orientationScaleValues[6],orientationScaleValues[7],orientationScaleValues[8]]
            magnitude=math.sqrt(axis3[0]*axis3[0]+axis3[1]*axis3[1]+axis3[2]*axis3[2])
            if magnitude > 0.0:
                axis3[0] /= magnitude
                axis3[1] /= magnitude
                axis3[2] /= magnitude  
            size[2]=magnitude;
        return axis1, axis2, axis3, size
 
    def getVectorDelta(self, x, y):
        '''
        Get the delta of position between selected nodes and provided windows coordinates
        '''
        delta = [0.0, 0.0, 0.0]
        fieldmodule = self._editReferenceNode.getNodeset().getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        fieldcache.setNode(self._editReferenceNode)
        numberOfComponents = self._selectedOrientationField.getNumberOfComponents()
        
        if numberOfComponents > 0 and numberOfComponents <= 9 and self._selectedOrientationField.isValid() and \
            self._selectedCoordinateField.isValid() and self._editGlyphScaleFactors[0] != 0.0 and \
            self._editGlyphCentre[0] == 0.0 and self._editGlyphSize[0] == 0.0 and \
            False == self._editVariableScaleField.isValid():
            return_code, orientation = self._selectedOrientationField.evaluateReal(fieldcache, numberOfComponents)
            return_code, coordinates = self._selectedCoordinateField.evaluateReal(fieldcache, 3)
            axis1, axis2, axis3, num = self.makeGlyphOrientationScaleAxes(orientation)
            oldCoordinates = [coordinates[0], coordinates[1], coordinates[2]]
            endCoordinates = [0.0, 0.0, 0.0]
            endCoordinates[0] = coordinates[0]+self._editGlyphSize[0]*self._editGlyphScaleFactors[0]*axis1[0];
            endCoordinates[1] = coordinates[1]+self._editGlyphSize[0]*self._editGlyphScaleFactors[0]*axis1[1];
            endCoordinates[2] = coordinates[2]+self._editGlyphSize[0]*self._editGlyphScaleFactors[0]*axis1[2];
            projectCoordinates = self._zincwidget.project(endCoordinates[0], endCoordinates[1], endCoordinates[2])
            endCoordinates = self._zincwidget.unproject(x, y * -1.0, projectCoordinates[2])
            a = [0.0, 0.0, 0.0]
            a[0]=(endCoordinates[0]-oldCoordinates[0])/self._editGlyphScaleFactors[0]
            a[1]=(endCoordinates[1]-oldCoordinates[1])/self._editGlyphScaleFactors[0]
            a[2]=(endCoordinates[2]-oldCoordinates[2])/self._editGlyphScaleFactors[0]
            if numberOfComponents == 1:
                delta[0] = a[0]
            elif numberOfComponents == 2 or numberOfComponents == 4:
                delta[0] = a[0]
                delta[1] = a[1]
            elif numberOfComponents == 3 or numberOfComponents == 6 or numberOfComponents == 9:
                delta[0] = a[0]
                delta[1] = a[1]
                delta[2] = a[2]

        return delta
        
    def getCoordinatesDelta(self, x, y):
        '''
        Get the delta of position between selected nodes and provided windows coordinates
        '''
        fieldmodule = self._editReferenceNode.getNodeset().getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        fieldcache.setNode(self._editReferenceNode)
        return_code, coordinates = self._selectedCoordinateField.evaluateReal(fieldcache, 3)
        projectCoordinates = self._zincwidget.project(coordinates[0], coordinates[1], coordinates[2])
        unprojectCoordinates = self._zincwidget.unproject(x, y * -1.0, projectCoordinates[2])
        #print "coordinates " + str(coordinates)
        #print "x, y " + str(x) + " " + str(y)
        #print "projectCoordinates " + str(projectCoordinates)
        #print "unprojectCoordinates " + str(unprojectCoordinates)
        delta = [unprojectCoordinates[0] - coordinates[0], unprojectCoordinates[1] - coordinates[1], \
                 unprojectCoordinates[2] - coordinates[2]]
        return delta
    
    def updateNodePositionWithDelta(self, fieldcache, coordinateField, node, xdiff, ydiff, zdiff):
        fieldcache.setNode(node)
        return_code, coordinates = coordinateField.evaluateReal(fieldcache, 3)
        coordinateField.assignReal(fieldcache, [coordinates[0]+xdiff, \
                                                coordinates[1]+ydiff, \
                                                coordinates[2]+zdiff])
#    def updateSelectedNodesInRegionWithDelta(self, region, xdiff, ydiff, zdiff):
#        childRegion = region.getFirstChild()
#        while childRegion.isValid():
#            updateSelectedNodesInRegion(self, childRegion, xdiff, ydiff, zdiff)
#            childRegion = childRegion.getNextSibling()
#        nodeset = region.getFieldmodule().findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
#        if nodeset.isValid():
#            nodegroup = self._selectionGroup.getFieldNodeGroup(nodeset)
#            if nodegroup.isValid():
#                nodesetgroup = nodegroup.getNodesetGroup()
#                if nodesetgroup.isValid():
#                    iterator = nodesetgroup.createNodeiterator()
#                    node = iterator.next()
#                    while node.isValid():                        
#                        node = iterator.next()
            
    def updateSelectedNodesCoordinatesWithDelta(self, xdiff, ydiff, zdiff):
        nodegroup = self._selectionGroup.getFieldNodeGroup(self._editReferenceNode.getNodeset())
        if nodegroup.isValid():
            group = nodegroup.getNodesetGroup()
            if group.isValid():
                fieldmodule = nodegroup.getFieldmodule()
                fieldmodule.beginChange()
                fieldcahce = fieldmodule.createFieldcache()
                iterator = group.createNodeiterator()
                node = iterator.next()
                while node.isValid():            
                    self.updateNodePositionWithDelta(fieldcahce, self._selectedCoordinateField, \
                                                     node, xdiff, ydiff, zdiff)            
                    node = iterator.next()
                fieldmodule.endChange()
                
    def updateNodeVectorWithDelta(self, fieldcache, orientationField, node, xdiff, ydiff, zdiff):
        fieldcache.setNode(node)
        numberOfComponents = self._selectedOrientationField.getNumberOfComponents()
        return_code, orientationScale = orientationField.evaluateReal(fieldcache, numberOfComponents)
        if numberOfComponents == 1:
            orientationScale[0] = xdiff
        elif numberOfComponents == 2 or numberOfComponents == 4:
            orientationScale[0] = xdiff
            orientationScale[1] = ydiff
        elif numberOfComponents == 3 or numberOfComponents == 6 or numberOfComponents == 9:
            orientationScale[0] = xdiff
            orientationScale[1] = ydiff
            orientationScale[2] = zdiff
        orientationField.assignReal(fieldcache, orientationScale)
                
    def updateSelectedNodesVectorWithDelta(self, xdiff, ydiff, zdiff):
        nodegroup = self._selectionGroup.getFieldNodeGroup(self._editReferenceNode.getNodeset())
        if nodegroup.isValid():
            group = nodegroup.getNodesetGroup()
            if group.isValid():
                fieldmodule = nodegroup.getFieldmodule()
                fieldmodule.beginChange()
                fieldcahce = fieldmodule.createFieldcache()
                iterator = group.createNodeiterator()
                node = iterator.next()
                while node.isValid():            
                    self.updateNodeVectorWithDelta(fieldcahce, self._selectedOrientationField, \
                                                     node, xdiff, ydiff, zdiff)            
                    node = iterator.next()
                fieldmodule.endChange()            
    
        
#  Not applicable at the current point in time.
#     def _zincSelectionEvent(self, event):
#         print(event.getChangeFlags())
#         print('go the selection change')


    def nodeIsSelectedAtCoordinates(self, x, y):
        '''
        Return node and its coordinates field if its valid
        '''
        self._scenepicker.setSceneviewerRectangle(self._sceneviewer, SCENECOORDINATESYSTEM_LOCAL, \
                                                  x - 3.5, y - 3.5, \
                                                  x + 3.5, y + 3.5);
        node = self._scenepicker.getNearestNode()
        print node.isValid()
        if node.isValid():
            nodeset = node.getNodeset()
            nodegroup = self._selectionGroup.getFieldNodeGroup(nodeset)
            if nodegroup.isValid():
                group = nodegroup.getNodesetGroup()
                if group.containsNode(node):
                    graphics = self._scenepicker.getNearestGraphics()
                    if graphics.getFieldDomainType() == Field.DOMAIN_TYPE_NODES:
                        return True, node, graphics.getCoordinateField(), graphics
        return False, None, None, None
        
    def proceedSceneViewerMousePressEvent(self, event):
        '''
        Inform the scene viewer of a mouse press event.
        '''
        self._handle_mouse_events = False  # Track when the zinc should be handling mouse events
        if not self._ignore_mouse_events and (event.modifiers() & QtCore.Qt.SHIFT) and (self._nodeSelectMode or self._elemSelectMode) and button_map[event.button()] == Sceneviewerinput.BUTTON_TYPE_LEFT:
            self._selection_position_start = (event.x(), event.y())
            self._selection_mode = SelectionMode.EXCLUSIVE
            if event.modifiers() & QtCore.Qt.ALT:
                self._selection_mode = SelectionMode.ADDITIVE
        elif not self._ignore_mouse_events and (event.modifiers() & self._editModifier) and (self._nodeEditMode or self._nodeEditVectorMode) and button_map[event.button()] == Sceneviewerinput.BUTTON_TYPE_LEFT:
            return_code, selectedNode, selectedCoordinateField, selectedGraphics = \
                self.nodeIsSelectedAtCoordinates(event.x(), event.y())
            if return_code:
                self._selection_mode = SelectionMode.EDIT_POSITION
                self._editReferenceNode = selectedNode
                self._selectedCoordinateField = selectedCoordinateField
                self._editGraphics = selectedGraphics
                self._selection_position_start = (event.x(), event.y())
                if self._nodeEditVectorMode:
                    attributes = self._editGraphics.getGraphicspointattributes()
                    if attributes.isValid():
                        self._selectedOrientationField = attributes.getOrientationScaleField()
                        if self._selectedOrientationField and self._selectedOrientationField.isValid():
                            self._variable_scale_field = attributes.getSignedScaleField()
                            self._selection_mode = SelectionMode.EDIT_VECTOR
                            return_code, self._editGlyphCentre = attributes.getGlyphOffset(3)
                            return_code, self._editGlyphSize = attributes.getBaseSize(3)
                            return_code, self._editGlyphScaleFactors = attributes.getScaleFactors(3)
                            self._editVariableScaleField = attributes.getSignedScaleField()
        elif not self._ignore_mouse_events and not event.modifiers() or (event.modifiers() & QtCore.Qt.SHIFT and button_map[event.button()] == Sceneviewerinput.BUTTON_TYPE_RIGHT):
            scene_input = self._sceneviewer.createSceneviewerinput()
            scene_input.setPosition(event.x(), event.y())
            scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_BUTTON_PRESS)
            scene_input.setButtonType(button_map[event.button()])
            scene_input.setModifierFlags(modifier_map(event.modifiers()))

            self._sceneviewer.processSceneviewerinput(scene_input)

            self._handle_mouse_events = True
        else:
            event.ignore()

    def proceedSceneViewerMouseReleaseEvent(self, event):
        '''
        Inform the scene viewer of a mouse release event.
        '''
        if not self._ignore_mouse_events and ( self._selection_mode == SelectionMode.EDIT_POSITION or \
                                              self._selection_mode == SelectionMode.EDIT_VECTOR):
            self._editReferenceNode = None
            self._editGraphics = None
            self._selection_mode = SelectionMode.NONE
            self._selectedCoordinateField = None
            self._selectedOrientationField = None
            self._variable_scale_field = None
            self._editVariableScaleField = Field()
        elif not self._ignore_mouse_events and self._selection_mode != SelectionMode.NONE:
            x = event.x()
            y = event.y()
            # Construct a small frustum to look for nodes in.
            top_region = self._sceneviewer.getScene().getRegion()
            top_region.beginHierarchicalChange()
            self._selection_box.setVisibilityFlag(False)
            
            if (x != self._selection_position_start[0] and y != self._selection_position_start[1]):
                left = min(x, self._selection_position_start[0])
                right = max(x, self._selection_position_start[0])
                bottom = min(y, self._selection_position_start[1])
                top = max(y, self._selection_position_start[1])
                self._scenepicker.setSceneviewerRectangle(self._sceneviewer, SCENECOORDINATESYSTEM_LOCAL, left, bottom, right, top);
                if self._selection_mode == SelectionMode.EXCLUSIVE:
                    self._selectionGroup.clear()
                if self._nodeSelectMode or self._dataSelectMode:
                    self._scenepicker.addPickedNodesToFieldGroup(self._selectionGroup)
                if self._elemSelectMode:
                    self._scenepicker.addPickedElementsToFieldGroup(self._selectionGroup)
            else:

                self._scenepicker.setSceneviewerRectangle(self._sceneviewer, SCENECOORDINATESYSTEM_LOCAL, x - 3.5, y - 3.5, x + 3.5, y + 3.5)
                if self._nodeSelectMode and self._elemSelectMode and self._selection_mode == SelectionMode.EXCLUSIVE and not self._scenepicker.getNearestGraphics().isValid():
                    self._selectionGroup.clear()

                if self._nodeSelectMode and (self._scenepicker.getNearestGraphics().getFieldDomainType() == Field.DOMAIN_TYPE_NODES):
                    node = self._scenepicker.getNearestNode()
                    nodeset = node.getNodeset()

                    nodegroup = self._selectionGroup.getFieldNodeGroup(nodeset)
                    if not nodegroup.isValid():
                        nodegroup = self._selectionGroup.createFieldNodeGroup(nodeset)

                    group = nodegroup.getNodesetGroup()
                    if self._selection_mode == SelectionMode.EXCLUSIVE:
                        remove_current = group.getSize() == 1 and group.containsNode(node)
                        self._selectionGroup.clear()
                        if not remove_current:
                            group.addNode(node)
                    elif self._selection_mode == SelectionMode.ADDITIVE:
                        if group.containsNode(node):
                            group.removeNode(node)
                        else:
                            group.addNode(node)

                if self._elemSelectMode and (self._scenepicker.getNearestGraphics().getFieldDomainType() in [Field.DOMAIN_TYPE_MESH1D, Field.DOMAIN_TYPE_MESH2D, Field.DOMAIN_TYPE_MESH3D, Field.DOMAIN_TYPE_MESH_HIGHEST_DIMENSION]):
                    elem = self._scenepicker.getNearestElement()
                    mesh = elem.getMesh()

                    elementgroup = self._selectionGroup.getFieldElementGroup(mesh)
                    if not elementgroup.isValid():
                        elementgroup = self._selectionGroup.createFieldElementGroup(mesh)

                    group = elementgroup.getMeshGroup()
                    if self._selection_mode == SelectionMode.EXCLUSIVE:
                        remove_current = group.getSize() == 1 and group.containsElement(elem)
                        self._selectionGroup.clear()
                        if not remove_current:
                            group.addElement(elem)
                    elif self._selection_mode == SelectionMode.ADDITIVE:
                        if group.containsElement(elem):
                            group.removeElement(elem)
                        else:
                            group.addElement(elem)

            top_region.endHierarchicalChange()
            self._selection_mode = SelectionMode.NONE
        elif not self._ignore_mouse_events and self._handle_mouse_events:
            scene_input = self._sceneviewer.createSceneviewerinput()
            scene_input.setPosition(event.x(), event.y())
            scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_BUTTON_RELEASE)
            scene_input.setButtonType(button_map[event.button()])

            self._sceneviewer.processSceneviewerinput(scene_input)
        else:
            event.ignore()

    def proceedSceneViewerMouseMoveEvent(self, event):
        '''
        Inform the scene viewer of a mouse move event and update the OpenGL scene to reflect this
        change to the viewport.
        '''
        
        if not self._ignore_mouse_events and self._selection_mode != SelectionMode.NONE:
            x = event.x()
            y = event.y()
            xdiff = float(x - self._selection_position_start[0])
            ydiff = float(y - self._selection_position_start[1])
            if abs(xdiff) < 0.0001:
                xdiff = 1
            if abs(ydiff) < 0.0001:
                ydiff = 1            
            if self._selection_mode == SelectionMode.EDIT_POSITION:
                delta = self.getCoordinatesDelta(x, y)
                self.updateSelectedNodesCoordinatesWithDelta(delta[0], delta[1], delta[2])
            elif self._selection_mode == SelectionMode.EDIT_VECTOR:
                if self._selectedOrientationField and self._selectedOrientationField.isValid():
                    delta = self.getVectorDelta(x, y)
                    self.updateSelectedNodesVectorWithDelta(delta[0], delta[1], delta[2])
            else:
                xoff = float(self._selection_position_start[0]) / xdiff + 0.5
                yoff = float(self._selection_position_start[1]) / ydiff + 0.5
                scene = self._selection_box.getScene()
                scene.beginChange()
                self._selectionBox_setBaseSize([xdiff, ydiff, 0.999])
                self._selectionBox_setGlyphOffset([xoff, -yoff, 0])
                self._selection_box.setVisibilityFlag(True)
                scene.endChange()

        elif not self._ignore_mouse_events and self._handle_mouse_events:
            scene_input = self._sceneviewer.createSceneviewerinput()
            scene_input.setPosition(event.x(), event.y())
            scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_MOTION_NOTIFY)
            if event.type() == QtCore.QEvent.Leave:
                scene_input.setPosition(-1, -1)
            self._sceneviewer.processSceneviewerinput(scene_input)
        else:
            event.ignore()

