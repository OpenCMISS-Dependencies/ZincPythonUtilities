# This python module is intended to facilitate users creating their own applications that use OpenCMISS-Zinc
# See the examples at https://svn.physiomeproject.org/svn/cmiss/zinc/bindings/trunk/python/ for further
# information.

try:
    from PySide import QtCore, QtOpenGL
except ImportError:
    from PyQt4 import QtCore, QtOpenGL

# from opencmiss.zinc.glyph import Glyph
from opencmiss.zinc.sceneviewer import Sceneviewer, Sceneviewerevent
from opencmiss.zinc.sceneviewerinput import Sceneviewerinput
from opencmiss.zinc.scenecoordinatesystem import SCENECOORDINATESYSTEM_LOCAL, SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT, SCENECOORDINATESYSTEM_WORLD
from opencmiss.zinc.field import Field
from opencmiss.zinc.glyph import Glyph
from opencmiss.zinc.status import OK

# mapping from qt to zinc start
# Create a button map of Qt mouse buttons to Zinc input buttons
button_map = {QtCore.Qt.LeftButton: Sceneviewerinput.BUTTON_TYPE_LEFT, QtCore.Qt.MidButton: Sceneviewerinput.BUTTON_TYPE_MIDDLE, QtCore.Qt.RightButton: Sceneviewerinput.BUTTON_TYPE_RIGHT}
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

# projectionMode start
class ProjectionMode(object):

    PARALLEL = 0
    PERSPECTIVE = 1
# projectionMode end


# selectionMode start
class SelectionMode(object):

    NONE = -1
    EXCULSIVE = 0
    ADDITIVE = 1
# selectionMode end


class ZincWidget(QtOpenGL.QGLWidget):

    # Create a signal to notify when the sceneviewer is ready.
    graphicsInitialized = QtCore.Signal()

    # init start
    def __init__(self, parent=None, shared=None):
        '''
        Call the super class init functions, set the  Zinc context and the scene viewer handle to None.
        Initialise other attributes that deal with selection and the rotation of the plane.
        '''
        QtOpenGL.QGLWidget.__init__(self, parent, shared)
        # Create a Zinc context from which all other objects can be derived either directly or indirectly.
        self._context = None
        self._sceneviewer = None

        # Selection attributes
        self._nodeSelectMode = True
        self._elemSelectMode = True
        self._selection_mode = SelectionMode.NONE
        self._selectionGroup = None
        self._selection_box = None
        self._ignore_mouse_events = False
        # init end

    def setContext(self, context):
        '''
        Sets the context for this ZincWidget.  This should be set before the initializeGL()
        method is called otherwise the scene viewer cannot be created.
        '''
        self._context = context

    def getSceneviewer(self):
        '''
        Get the scene viewer for this ZincWidget.
        '''
        return self._sceneviewer

    def setSelectModeNode(self):
        self._nodeSelectMode = True
        self._elemSelectMode = False

    def setSelectModeElement(self):
        self._elemSelectMode = True
        self._nodeSelectMode = False

    def setSelectModeAll(self):
        self._nodeSelectMode = True
        self._elemSelectMode = True

    # initializeGL start
    def initializeGL(self):
        '''
        Initialise the Zinc scene for drawing the axis glyph at a point.  
        '''
        if self._sceneviewer is None:
            # Get the scene viewer module.
            scene_viewer_module = self._context.getSceneviewermodule()

            # From the scene viewer module we can create a scene viewer, we set up the
            # scene viewer to have the same OpenGL properties as the QGLWidget.
            self._sceneviewer = scene_viewer_module.createSceneviewer(Sceneviewer.BUFFERING_MODE_DOUBLE, Sceneviewer.STEREO_MODE_DEFAULT)
            self._sceneviewer.setProjectionMode(Sceneviewer.PROJECTION_MODE_PERSPECTIVE)

            # Create a filter for visibility flags which will allow us to see our graphic.
            filter_module = self._context.getScenefiltermodule()
            # By default graphics are created with their visibility flags set to on (or true).
            graphics_filter = filter_module.createScenefilterVisibilityFlags()

            # Set the graphics filter for the scene viewer otherwise nothing will be visible.
            self._sceneviewer.setScenefilter(graphics_filter)
            region = self._context.getDefaultRegion()
            scene = region.getScene()
            fieldmodule = region.getFieldmodule()

            self._sceneviewer.setScene(scene)

            self._selectionGroup = fieldmodule.createFieldGroup()
    #         scene.setSelectionField(self._selectionGroup)

            self._scenepicker = scene.createScenepicker()
            self._scenepicker.setScenefilter(graphics_filter)

            # If the standard glyphs haven't been defined then the
            # selection box will not be visible
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

            # Set up unproject pipeline
            self._window_coords_from = fieldmodule.createFieldConstant([0, 0, 0])
            self._global_coords_from = fieldmodule.createFieldConstant([0, 0, 0])
            unproject = fieldmodule.createFieldSceneviewerProjection(self._sceneviewer, SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT, SCENECOORDINATESYSTEM_WORLD)
            project = fieldmodule.createFieldSceneviewerProjection(self._sceneviewer, SCENECOORDINATESYSTEM_WORLD, SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT)

    #         unproject_t = fieldmodule.createFieldTranspose(4, unproject)
            self._global_coords_to = fieldmodule.createFieldProjection(self._window_coords_from, unproject)
            self._window_coords_to = fieldmodule.createFieldProjection(self._global_coords_from, project)


            self._sceneviewer.viewAll()

    #  Not really applicable to us yet.
    #         self._selection_notifier = scene.createSelectionnotifier()
    #         self._selection_notifier.setCallback(self._zincSelectionEvent)

            self._sceneviewernotifier = self._sceneviewer.createSceneviewernotifier()
            self._sceneviewernotifier.setCallback(self._zincSceneviewerEvent)

            self.graphicsInitialized.emit()
            # initializeGL end

    def setProjectionMode(self, mode):
        if mode == ProjectionMode.PARALLEL:
            self._sceneviewer.setProjectionMode(Sceneviewer.PROJECTION_MODE_PARALLEL)
        elif mode == ProjectionMode.PERSPECTIVE:
            self._sceneviewer.setProjectionMode(Sceneviewer.PROJECTION_MODE_PERSPECTIVE)

    def getProjectionMode(self):
        if self._sceneviewer.getProjectionMode() == Sceneviewer.PROJECTION_MODE_PARALLEL:
            return ProjectionMode.PARALLEL
        elif self._sceneviewer.getProjectionMode() == Sceneviewer.PROJECTION_MODE_PERSPECTIVE:
            return ProjectionMode.PERSPECTIVE

    def getViewParameters(self):
        result, eye, lookat, up = self._sceneviewer.getLookatParameters()
        if result == OK:
            angle = self._sceneviewer.getViewAngle()
            return (eye, lookat, up, angle)

        return None

    def setViewParameters(self, eye, lookat, up, angle):
        self._sceneviewer.beginChange()
        self._sceneviewer.setLookatParametersNonSkew(eye, lookat, up)
        self._sceneviewer.setViewAngle(angle)
        self._sceneviewer.endChange()

    def setScenefilter(self, scenefilter):
        self._sceneviewer.setScenefilter(scenefilter)

    def getScenefilter(self):
        result, scenefilter = self._sceneviewer.getScenefilter()
        if result == OK:
            return scenefilter

        return None

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

    def project(self, x, y, z):
        in_coords = [x, y, z]
        fieldmodule = self._global_coords_from.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        self._global_coords_from.assignReal(fieldcache, in_coords)
        result, out_coords = self._window_coords_to.evaluateReal(fieldcache, 3)
        if result == OK:
            return out_coords  # [out_coords[0] / out_coords[3], out_coords[1] / out_coords[3], out_coords[2] / out_coords[3]]

        return None

    def unproject(self, x, y, z):
        in_coords = [x, y, z]
        fieldmodule = self._window_coords_from.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        self._window_coords_from.assignReal(fieldcache, in_coords)
        result, out_coords = self._global_coords_to.evaluateReal(fieldcache, 3)
        if result == OK:
            return out_coords  # [out_coords[0] / out_coords[3], out_coords[1] / out_coords[3], out_coords[2] / out_coords[3]]

        return None

    def getViewportSize(self):
        result, width, height = self._sceneviewer.getViewportSize()
        if result == OK:
            return (width, height)

        return None

    def setTumbleRate(self, rate):
        self._sceneviewer.setTumbleRate(rate)

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

    def viewAll(self):
        '''
        Helper method to set the current scene viewer to view everything
        visible in the current scene.
        '''
        self._sceneviewer.viewAll()

    # paintGL start
    def paintGL(self):
        '''
        Render the scene for this scene viewer.  The QGLWidget has already set up the
        correct OpenGL buffer for us so all we need do is render into it.  The scene viewer
        will clear the background so any OpenGL drawing of your own needs to go after this
        API call.
        '''
        self._sceneviewer.renderScene()
        # paintGL end

    def _zincSceneviewerEvent(self, event):
        '''
        Process a scene viewer event.  The updateGL() method is called for a
        repaint required event all other events are ignored.
        '''
        if event.getChangeFlags() & Sceneviewerevent.CHANGE_FLAG_REPAINT_REQUIRED:
            QtCore.QTimer.singleShot(0, self.updateGL)

#  Not applicable at the current point in time.
#     def _zincSelectionEvent(self, event):
#         print(event.getChangeFlags())
#         print('go the selection change')

    # resizeGL start
    def resizeGL(self, width, height):
        '''
        Respond to widget resize events.
        '''
        self._sceneviewer.setViewportSize(width, height)
        # resizeGL end

    def mousePressEvent(self, event):
        '''
        Inform the scene viewer of a mouse press event.
        '''
        event.accept()
        self._handle_mouse_events = False  # Track when the zinc should be handling mouse events
        if not self._ignore_mouse_events and (event.modifiers() & QtCore.Qt.SHIFT) and (self._nodeSelectMode or self._elemSelectMode) and button_map[event.button()] == Sceneviewerinput.BUTTON_TYPE_LEFT:
            self._selection_position_start = (event.x(), event.y())
            self._selection_mode = SelectionMode.EXCULSIVE
            if event.modifiers() & QtCore.Qt.ALT:
                self._selection_mode = SelectionMode.ADDITIVE
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

    def mouseReleaseEvent(self, event):
        '''
        Inform the scene viewer of a mouse release event.
        '''
        event.accept()
        if not self._ignore_mouse_events and self._selection_mode != SelectionMode.NONE:
            x = event.x()
            y = event.y()
            # Construct a small frustrum to look for nodes in.
            root_region = self._context.getDefaultRegion()
            root_region.beginHierarchicalChange()
            self._selection_box.setVisibilityFlag(False)

            if (x != self._selection_position_start[0] and y != self._selection_position_start[1]):
                left = min(x, self._selection_position_start[0])
                right = max(x, self._selection_position_start[0])
                bottom = min(y, self._selection_position_start[1])
                top = max(y, self._selection_position_start[1])
                self._scenepicker.setSceneviewerRectangle(self._sceneviewer, SCENECOORDINATESYSTEM_LOCAL, left, bottom, right, top);
                if self._selection_mode == SelectionMode.EXCULSIVE:
                    self._selectionGroup.clear()
                if self._nodeSelectMode:
                    self._scenepicker.addPickedNodesToFieldGroup(self._selectionGroup)
                if self._elemSelectMode:
                    self._scenepicker.addPickedElementsToFieldGroup(self._selectionGroup)
            else:

                self._scenepicker.setSceneviewerRectangle(self._sceneviewer, SCENECOORDINATESYSTEM_LOCAL, x - 0.5, y - 0.5, x + 0.5, y + 0.5)
                if self._nodeSelectMode and self._elemSelectMode and self._selection_mode == SelectionMode.EXCULSIVE and not self._scenepicker.getNearestGraphics().isValid():
                    self._selectionGroup.clear()

                if self._nodeSelectMode and (self._scenepicker.getNearestGraphics().getFieldDomainType() == Field.DOMAIN_TYPE_NODES):
                    node = self._scenepicker.getNearestNode()
                    nodeset = node.getNodeset()

                    nodegroup = self._selectionGroup.getFieldNodeGroup(nodeset)
                    if not nodegroup.isValid():
                        nodegroup = self._selectionGroup.createFieldNodeGroup(nodeset)

                    group = nodegroup.getNodesetGroup()
                    if self._selection_mode == SelectionMode.EXCULSIVE:
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
                    if self._selection_mode == SelectionMode.EXCULSIVE:
                        remove_current = group.getSize() == 1 and group.containsElement(elem)
                        self._selectionGroup.clear()
                        if not remove_current:
                            group.addElement(elem)
                    elif self._selection_mode == SelectionMode.ADDITIVE:
                        if group.containsElement(elem):
                            group.removeElement(elem)
                        else:
                            group.addElement(elem)


            root_region.endHierarchicalChange()
            self._selection_mode = SelectionMode.NONE
        elif not self._ignore_mouse_events and self._handle_mouse_events:
            scene_input = self._sceneviewer.createSceneviewerinput()
            scene_input.setPosition(event.x(), event.y())
            scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_BUTTON_RELEASE)
            scene_input.setButtonType(button_map[event.button()])

            self._sceneviewer.processSceneviewerinput(scene_input)
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        '''
        Inform the scene viewer of a mouse move event and update the OpenGL scene to reflect this
        change to the viewport.
        '''

        event.accept()
        if not self._ignore_mouse_events and self._selection_mode != SelectionMode.NONE:
            x = event.x()
            y = event.y()
            xdiff = float(x - self._selection_position_start[0])
            ydiff = float(y - self._selection_position_start[1])
            if abs(xdiff) < 0.0001:
                xdiff = 1
            if abs(ydiff) < 0.0001:
                ydiff = 1
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


