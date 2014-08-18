# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QgisMarkerCluster
                                 A QGIS plugin
 Combines points in a defined distance into a cluster point.

                             -------------------
        begin                : 2014-08-15
        copyright            : (C) 2014 by Matthias Ludwig - Datalyze Solutions
        email                : m.ludwig@datalyze-solutions.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

import resources_rc

from QgisMarkerClusterWidget import QgisMarkerClusterDockWidget
from libs.QgsClusterLayer import QgsClusterCalculator, CustomClusterColumnWrapper
from libs.tilemapscalelevels import TileMapScaleLevels
from libs.QgsLayerStyles import *

from ui_info import Ui_info

import os.path

class QgisMarkerCluster(object):

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.registry = QgsMapLayerRegistry.instance()
        
        # initialize plugin directory
        self.workingDir = os.path.dirname(os.path.abspath(__file__))
        self.datasetDir = os.path.join(self.workingDir, "datasets")
        self.config = ConfigurationSettings(self.workingDir)
        
        if not os.path.exists(self.datasetDir):
            self.iface.messageBar().pushMessage("Error", "Can't find %s. You wont't be able to load any datasets." % self.datasetDir, QgsMessageBar.CRITICAL)
            
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.workingDir, 'i18n', 'tilemapscaleplugin_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.basePointLayer = QgsVectorLayer()
        self.canvas.scaleCalculator = TileMapScaleLevels(maxZoomlevel=18, minZoomlevel=0, dpi=self.iface.mainWindow().physicalDpiX())
        self.clusterLayers = []
        self.symbolLib = SymbolLibrary(self.config)
        self.clusterCalculator = None

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/icons/icon.png"),
            u"QgisMarkerCluster Plugin", self.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect(self.showDock)

        self.dock = QgisMarkerClusterDockWidget()
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dock)
        self.projection = self.canvas.mapRenderer().destinationCrs()
        self.canvas.enableAntiAliasing(True)

        #self.readStatus()
        
        ## Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&QgisMarkerCluster Plugin", self.action)

        self.dock.buttonInfo.clicked.connect(self.showInfo)

        self.dock.buttonLoadTestDataset.clicked.connect(self.addTestPoints)
        self.dock.buttonClusterPoints.clicked.connect(self.addClusterPoints)
        self.dock.doubleSpinBoxClusterDistance.valueChanged.connect(self.distanceChanged)
        self.dock.buttonLoadClusterDataset.clicked.connect(self.addClusterShape)

        ## set distance dependeding on srs of new layer loaded
        self.registry.layerWasAdded.connect(self.setInitalClusterDistance)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&QgisMarkerCluster Plugin", self.action)
        self.iface.removeToolBarIcon(self.action)
        del self.dock
        del self.clusterCalculator

    def showDock(self):
        if self.dock.isVisible():
            self.dock.hide()
        else:
            self.dock.show()

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&Tile Map Scale Plugin", self.action)
        self.iface.removeToolBarIcon(self.action)
        self.iface.removeDockWidget(self.dock)

    def showInfo(self):
        self.dialogInfo = dialogInfo(self.workingDir)
        self.dialogInfo.setParent(self.iface.mainWindow(), self.dialogInfo.windowFlags())
        self.dialogInfo.exec_()

    def addTestPoints(self):
        datasetPath = os.path.join(self.datasetDir, 'stations_3857.shp')
        self.basePointLayer = QgsVectorLayer(datasetPath, "stations", "ogr")
        self.symbolLib.setSymbol(
            self.basePointLayer,
            self.symbolLib.getSymbolColorCircle(
                QGis.Point,
                angle=0,
                color=self.symbolLib.colors.blues[0],
                colorBorder=self.symbolLib.colors.blues[2],
                size=1,
                offset='0,0',
                shadow=False
            )
        )
        self.registry.addMapLayer(self.basePointLayer)

    ## cluster stuff
    #
    def dropClusterLayers(self):
        for layer in self.clusterLayers:
            try:
                self.registry.removeMapLayer(layer.id())
            except RuntimeError:
                self.clusterLayers.remove(layer)
        self.clusterLayers = []
        self.clusterCalculator = None        
        
    def addClusterPoints(self):
        layer = self.iface.activeLayer()
        ## no selected layer return None
        if layer:      
            if layer.type() == 0:
                if layer.geometryType() == 0:
                    maxPoints = 20000
                    if layer.featureCount() <= maxPoints:

                        self.dropClusterLayers()

                        if layer.isValid():
                            customColumnWrapper = CustomClusterColumnWrapper()
                            self.clusterCalculator = QgsClusterCalculator(layer, self.canvas, self.config, customColumnWrapper, version=3, pixelDistance=self.dock.doubleSpinBoxClusterDistance.value())
                            self.dock.lineEditClusterShapePath.setText(self.clusterCalculator.tmpClusterShapePath)

                            self.addClusterShape()
                    else:
                        QMessageBox.information(self.iface.mainWindow(), 'QGIS', u"the selected layer has more than {} points. The cluster algorithm doesn't support that much points at the moment (limit is {} points).".format(maxPoints, maxPoints))
                else:
                    QMessageBox.warning(self.iface.mainWindow(), 'QGIS', u"No point layer selected in the layer tree")
            else:
                QMessageBox.warning(self.iface.mainWindow(), 'QGIS', u"Clusters only work for vector point layer")
        else:
            QMessageBox.warning(self.iface.mainWindow(), 'QGIS', u"You have to select a point layer in the layer tree to calculate clusters")

    def addClusterShape(self):
        if self.clusterCalculator:
            clusterCount = len(self.clusterLayers)
            
            clusterLayer = self.clusterCalculator.getClusterLayer('Cluster')

            fillColor = self.symbolLib.colors.reds[2]
            borderColor = self.symbolLib.colors.reds[1]
            angle = clusterCount * 45
            if clusterCount == 0:
                xOffset = 0
                size = 6
            else:
                xOffset = 6
                size = 4
            offset = '0,{}'.format(xOffset)
            valueColumn = 'count'
            self.symbolLib.setSymbol(
                clusterLayer,
                self.symbolLib.getSymbolColorCircle(
                    QGis.Point,
                    angle=angle,
                    color=fillColor,
                    colorBorder=borderColor,
                    size=size,
                    offset=offset,
                    shadow=False
                )
            )

            #self.symbolLib.setSymbolGraduated(
                #clusterLayer,
                #[
                    #QgsRendererRangeV2(0, 99, self.symbolLib.getSymbolColorCircle(QGis.Point, angle, '250,250,250', borderColor, size, offset=offset, shadow=False), '0'),
                    #QgsRendererRangeV2(100, 99999999999, self.symbolLib.getSymbolColorCircle(QGis.Point, angle, fillColor, borderColor, size, offset=offset, shadow=False), '>0')
                #],
                #valueColumn
            #)
            self.symbolLib.setLabeling(clusterLayer, valueColumn, xOffset=xOffset, angle=angle)

            self.clusterLayers.append(clusterLayer)
            self.registry.addMapLayer(clusterLayer)

            self.iface.zoomFull()

    def distanceChanged(self, distance):
        if self.clusterCalculator:
            self.clusterCalculator.pixelDistance = distance
            self.clusterCalculator.updateClusters(self.canvas.scale())
            self.canvas.refresh()

    def setInitalClusterDistance(self, layer):
        if layer.isValid():
            # vector            
            if layer.type() == 0:
                # point
                if layer.geometryType() == 0:
                    if layer.crs().postgisSrid() == 4326:
                        self.dock.doubleSpinBoxClusterDistance.setMinimum(0.0001)
                        self.dock.doubleSpinBoxClusterDistance.setMaximum(10)
                        self.dock.doubleSpinBoxClusterDistance.setValue(0.0005)
                    elif layer.crs().postgisSrid() == 3857:
                        self.dock.doubleSpinBoxClusterDistance.setMinimum(1)
                        self.dock.doubleSpinBoxClusterDistance.setMaximum(100)
                        self.dock.doubleSpinBoxClusterDistance.setValue(60)
                    else:
                        self.dock.doubleSpinBoxClusterDistance.setMinimum(0.0001)
                        self.dock.doubleSpinBoxClusterDistance.setMaximum(1000)
                        self.dock.doubleSpinBoxClusterDistance.setValue(60)                        


class dialogInfo(QDialog, Ui_info):

    def __init__(self, workingDir, infoHtml="README.html"):
        super(dialogInfo, self).__init__()
        self.setupUi(self)

        self.workingDir = workingDir
        self.infoHtml = infoHtml
        self.goHome()
        self.buttonHome.clicked.connect(self.goHome)

    def goHome(self):
        url = os.path.join(self.workingDir, self.infoHtml)
        self.webView.setUrl(QUrl(url))

## object contains all configurations...just to dont break my other code :D
#
class ConfigurationSettings(object):

    def __init__(self, appPath):
        self.appPath = appPath