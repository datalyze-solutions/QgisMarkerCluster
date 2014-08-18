# -*- coding: utf-8 -*-
#  @file QgsClusterLayer
#       Takes a point vector layer and calculates a new layer with clusters

import os
import tempfile
from PyQt4.QtCore import QVariant
from qgis.core import *

#from pyspatialite import dbapi2 as db
import numpy
#import rtree
#from copy import deepcopy

#import timeit
import time
#import pandas
from uuid import uuid4
#import types
import warnings

## helpful aggregation functions
#def timeDiff(timeList):
    #timeSet = set(timeList)
    #times = []
    #for t in timeList:
        #times.append(numpy.datetime64(t))
    #return str(numpy.timedelta64(numpy.max(times) - numpy.min(times), 'h'))

class CustomClusterColumnWrapper(object):

    def __init__(self):
        self.columns = []
        self.existingNames = {}

    def addCustomColumn(self, columnName, operator, dataType):
        self.columns.append(CustomClusterColumn(columnName, operator, dataType))

    def createShapeColumnNames(self):
        # shape columns restricted to 10 characters
        self.existingNames = {}
        for i, column in enumerate(self.columns):
            columnName = self.__defaultReplacement(column.name)[:10]
            if columnName in self.existingNames.values():
                columnName = u"{0}{1}".format(columnName[:9], i)
                self.existingNames[column.name] = columnName
                column.shapeName = columnName
            else:
                self.existingNames[column.name] = columnName
                column.shapeName = columnName

        print self.existingNames

    def __defaultReplacement(self, columnName):
        return columnName.replace('count', 'cnt').replace('_', '').replace(' ', '')

    def __repr__(self):
        return str(self.columns)

    def translateColumnName(self, columnName):
        if columnName in self.existingNames.keys():
            return self.existingNames[columnName]
        else:
            # if empty, the column will not be shown in qgis BUT doesnt raises an error!
            return ''

class CustomClusterColumn(object):

    def __init__(self, columnName, operator, dataType, shapeName=''):
        self.name = columnName
        # shape files limit this to 10 characters...
        self.shapeName = shapeName
        self.__valueList = []
        self.operator = operator

        assert dataType in [QVariant.Int, QVariant.Double, QVariant.String, QVariant.DateTime]
        self.dataType = dataType

    def evaluate(self):
        try:
            return self.operator(self.__valueList)
        except:
            raise

    def addValue(self, x):
        try:
            # test if we can convert the value to a numeric one
            self.__valueList.append(x)
        except:
            raise

    def __repr__(self):
        return u"{0}(shp: {1}): {2}".format(self.name, self.shapeName, self.__valueList)


class ClusterPoint(object):

    def __init__(self, clusterId, scale, distance, customColumnWrapper=None):
        self.clusterId = clusterId
        self.scale = scale
        self.distance = distance
        self.count = 0
        self.xList = []
        self.yList = []
        #self.features = []

        if customColumnWrapper is None:
            customColumnWrapper = CustomClusterColumnWrapper()
        else:
            customColumnWrapper = customColumnWrapper

        # create a new instance of CustomClusterColumn to add values, otherwise each cluster shares the same CustomClusterColumn
        self.customColumns = []
        for column in customColumnWrapper.columns:
            #print "init cluster", column.name, column.shapeName
            self.customColumns.append(CustomClusterColumn(column.name, column.operator, column.dataType, shapeName=column.shapeName))
            #print self.customColumns

    def __repr__(self):
        values = {
            "x": self.x,
            "y": self.y,
            "count": self.count,
            "scale": self.scale,
            "distance": self.distance
        }
        return u"ClusterPoint {x};{y} - features: {count} | scale: {scale} | distance: {distance}".format(**values)

    @property
    def x(self):
        return numpy.mean(self.xList)

    def addX(self, x):
        self.xList.append(x)

    @property
    def y(self):
        return numpy.mean(self.yList)

    def addY(self, y):
        try:
            float(y) or int(y)
            self.yList.append(y)
        except:
            raise TypeError, 'value has to be numeric'

class ClusterStore(object):

    def __init__(self, basePointLayer):
        self.basePointLayer = basePointLayer
        self.store = {}

    def __repr__(self):
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        return u"{}".format(pp.pprint(self.store))        

    def addClusters(self, clusters, scale, distance):
        key = self.getKey(scale, distance)

        foundClusters = self.getClusters(scale, distance)
        if foundClusters is None:
            self.store[key] = clusters
        
        #subsetString = str(self.basePointLayer.subsetString())
        #"""
        #{
            #scale: {
                #distance: {
                    #subsetString: {
                        #ClusterPoint a,
                        #ClusterPoint b
                    #}
                #}
            #}
        #}
        #"""
        #foundClusters = self.getClusters(scale, distance)
        #if foundClusters is None:
            #tmp = {}
            #tmp[subsetString] = clusters
            #tmp[distance] = tmp
            #self.store[scale] = tmp
        #elif isinstance(foundClusters, dict):
            #self.store[scale][distance][subsetString] = clusters

    def getKey(self, scale, distance):
        #print "getKey", scale, distance, self.basePointLayer
        try:
            if self.basePointLayer.isValid():
                subsetString = str(self.basePointLayer.subsetString())
                return u"{0}_{1}_{2}".format(scale, distance, subsetString)
        except RuntimeError:
            pass            

    def getClusters(self, scale, distance):
        #subsetString = str(self.basePointLayer.subsetString())
        key = self.getKey(scale, distance)
        #print key, key in self.store.keys()

        if key in self.store.keys():
            #print self.store.keys()
            return self.store[key]
        else:
            return None
            
        #if scale in self.store.keys():
            #if distance in self.store[scale].keys():
                #if subsetString in self.store[scale][distance].keys():
                    #print self.store.keys()
                    #print self.store[scale].keys()
                    #print self.store[scale][distance].keys()
                    ##print self.store[scale][distance][0.15287405657035252]                    
                    
                    #return self.store[scale][distance][subsetString]
                #else:
                    #return None
            #else:
                #return None
        #else:
            #return None
        
## QGIS version
#
class QgsClusterCalculator(object):

    #pixelDistance=0.0005-0.00033       # lat lng
    #pixelDistance=50           # metrical
    def __init__(self, basePointLayer, canvas, config, customColumnWrapper=None, pixelDistance=50, version=1):
        assert version in [1, 2, 3]
        self.version = version
        self.__isActive = True
        
        self.canvas = canvas
        self.config = config

        self.featureStore = {}        
        self.baseIndex = QgsSpatialIndex()
        self.initClusterStore()

        self.basePointLayer = basePointLayer
        self.crs = self.basePointLayer.crs().authid()
        
        self.clusterStore = ClusterStore(self.basePointLayer)

        self.pixelDistance = pixelDistance

        if customColumnWrapper is None:
            self.customColumnWrapper = CustomClusterColumnWrapper()
        else:
            self.customColumnWrapper = customColumnWrapper
        #for column in customColumns:
            #if self.basePointLayer.dataProvider().fields().indexFromName(column.name) <> -1:
                #self.customColumns.append(column)

        self.tmpClusterShapePath, self.__tmpClusterPointLayer = self.createTempDataset(self.crs, self.config.appPath)       
        #self.tmpClusterShapePath = os.path.join(self.config.appPath, "tmp", u"cluster_{0}.shp".format(uuid4()))
        #self.__tmpClusterPointLayer = QgsVectorLayer("Point?crs={0}&field=id:integer&field=count:integer&field=scale:integer&field=distance:integer&index=yes".format(self.crs), "Cluster Points", "memory")
        ##error = QgsVectorFileWriter.writeAsVectorFormat(self.__tmpClusterPointLayer, self.tmpClusterShapePath, "CP1250", None, "ESRI Shapefile")
        #error = QgsVectorFileWriter.writeAsVectorFormat(self.__tmpClusterPointLayer, self.tmpClusterShapePath, "CP1250", None, "ESRI Shapefile")
        #self.__tmpClusterPointLayer = QgsVectorLayer(self.tmpClusterShapePath, "Cluster Points", "ogr")
  
        startTime = time.time()
        self.buildSpatialIndex()
        print "init time {0}ms".format((time.time() - startTime) * 1000)

        ## auto update clusters if canvases scale changes
        self.canvas.scaleChanged.connect(self.updateClusters)

    def deleteTempFiles(self):
        for extension in ["cpg", "dbf", "prj", "qpj", "shp", "shx"]:
            try:
                fileName = self.tmpClusterShapePath.replace("shp", extension)
                #print fileName
                os.remove(fileName)
            except:
                pass

    def createTempDataset(self, crs, appPath): 
        ## rewrite with tempfile
        if os.path.exists("/tmp"):
            try:
                os.mkdir("/tmp/cluster_tmp")
            except:
                pass
            tmpClusterShapePath = os.path.join("/tmp/cluster_tmp", u"cluster_{0}.shp".format(uuid4()))
        else:
            tmpClusterShapePath = os.path.join(appPath, "tmp", u"cluster_{0}.shp".format(uuid4()))
        
        #tmpClusterPointLayer = QgsVectorLayer("Point?crs={0}&field=id:integer&field=count:integer&field=scale:integer&field=distance:integer&index=yes".format(crs), "Cluster Points", "memory")
        tmpClusterPointLayer = QgsVectorLayer("Point?crs={0}&index=yes".format(crs), "Cluster Points", "memory")

        #print referenceSystem
        fields = [
            QgsField("id", QVariant.Int),
            QgsField("count", QVariant.Int),
            QgsField("scale", QVariant.Int),
            QgsField("distance", QVariant.Double)
        ]
        for column in self.customColumnWrapper.columns:
        #for column in self.customColumns:
            fields.append(QgsField(column.shapeName, column.dataType))
        provider = tmpClusterPointLayer.dataProvider()
        provider.addAttributes(fields)
        tmpClusterPointLayer.updateFields()

        #error = QgsVectorFileWriter.writeAsVectorFormat(tmpClusterPointLayer, tmpClusterShapePath, "utf-8", tmpClusterPointLayer.crs(), "ESRI Shapefile")
        error = QgsVectorFileWriter.writeAsVectorFormat(tmpClusterPointLayer, tmpClusterShapePath, "utf-8", None, "ESRI Shapefile")

        tmpClusterPointLayer = QgsVectorLayer(tmpClusterShapePath, "Cluster Points", "ogr")
        return tmpClusterShapePath, tmpClusterPointLayer
        

    def getClusterLayer(self, layerName):
        return QgsVectorLayer(self.tmpClusterShapePath, layerName, "ogr")

    ## get isActive
    #
    def isActive(self):
        return self.__isActive

    ## set isActive, auto recalc if canvas scale changes
    #   @param isActive True/False
    def setIsActive(self, isActive):
        try:
            self.__isActive = bool(isActive)
        except:
            self.__isActive = True

    def initClusterStore(self):
        self.clusters = {}
        #self.clusters = []
        self.clusterIdx = QgsSpatialIndex()

    def buildSpatialIndex(self):
        startTime = time.time()
        self.baseIndex = QgsSpatialIndex()
        self.featureStore = {}

        #print self.basePointLayer.isValid(), self.basePointLayer.geometryType(), self.basePointLayer.storageType()
        #allFeatures = self.basePointLayer.getFeatures()
        #feature = QgsFeature()
        #while allFeatures.nextFeature(feature):
            #print feature.geometry().asPoint()
        
        for feature in self.basePointLayer.getFeatures():
            #print feature, feature.id(), feature.geometry().asPoint()
            self.baseIndex.insertFeature(feature)
            #index.insert(feature.id(), [feature.geometry().asPoint().x(), feature.geometry().asPoint().y()])
            #featureStore[feature.id()] = [feature.geometry().asPoint().x(), feature.geometry().asPoint().y(), feature.id()]
            self.featureStore[feature.id()] = feature
            #featureStore.append(feature.id())

        print "time to buildSpatialIndex {0}ms".format((time.time() - startTime) * 1000)
        return self.featureStore, self.baseIndex        

    ## return a search box
    #   @param p point as [x, y]
    #   @param tx distance in +/- x direction
    #   @param ty distance in +/- y direction
    def searchRect(self, p, tx, ty):
        p = p.geometry().asPoint()
        return QgsRectangle(p.x() - tx, p.y() - ty, p.x() + tx, p.y() + ty)        

    def createCluster(self, feature, scale, distance):
        cluster = ClusterPoint(len(self.clusters), scale, distance, self.customColumnWrapper)

        self.addToCluster(cluster, feature)
        
        #self.clusters.append(cluster)
        self.clusters[feature.id()] = cluster
        
        #self.clusterIdx.insert(len(self.clusters) - 1, [feature.geometry().asPoint().x(), feature.geometry().asPoint().y()])
        self.clusterIdx.insertFeature(feature)
        return cluster

    def addToCluster(self, cluster, feature):
        #cluster.features.append(feature)
        cluster.addX(feature.geometry().asPoint().x())
        cluster.addY(feature.geometry().asPoint().y())

        for column in cluster.customColumns:
            #print "add value", column.shapeName, feature.attribute(column.shapeName).toDouble()
            try:
                if column.dataType == QVariant.String:
                    column.addValue(feature.attribute(column.shapeName).toString())
                elif column.dataType == QVariant.Double:
                    column.addValue(feature.attribute(column.shapeName).toDouble()[0])
                elif column.dataType == QVariant.Int:
                    column.addValue(feature.attribute(column.shapeName).toInt()[0])
                else:
                    column.addValue(feature.attribute(column.shapeName).toString())
                #print column
            except:
                raise
                column.addValue(0)
        
        cluster.count += 1

    def buildCluster(self, scale, distance=100000, pixelSize=None):
        try:
            #self.dropClusterGeometry()
            #self.initClusterStore()

            if pixelSize is not None:
                distance = pixelSize * self.pixelDistance

            foundClusters = self.clusterStore.getClusters(scale, distance)
            #print "foundClusters", foundClusters, type(foundClusters)
            if foundClusters is None:

                self.dropClusterGeometry()
                self.initClusterStore()

                print "calculating new cluster"
                #print self.basePointLayer.featureCount(), len(self.featureStore)
                if self.basePointLayer.featureCount() != len(self.featureStore):
                    self.buildSpatialIndex()

                nonClustered = self.featureStore.copy()

                unbalancedPoints = {}

                while len(nonClustered) > 0:
                    firstFeatureId = nonClustered.keys()[0]
                    #print "firstFeatureId", firstFeatureId
                    firstFeature = nonClustered[firstFeatureId]

                    nonClustered.pop(firstFeatureId)
                    cluster = self.createCluster(firstFeature, scale, distance)

                    if self.version == 1:
                        searchRects = [
                            self.searchRect(firstFeature, distance, distance)
                        ]
                    elif self.version == 2:
                        searchRects = [
                            self.searchRect(firstFeature, distance*0.2, distance),
                            self.searchRect(firstFeature, distance, distance*0.2),
                            self.searchRect(firstFeature, distance*0.5, distance*0.88),
                            self.searchRect(firstFeature, distance*0.88, distance*0.5),
                            self.searchRect(firstFeature, distance*0.5, distance*0.5)
                        ]
                    elif self.version == 3:
                        searchRects = [
                            self.searchRect(firstFeature, distance*0.66, distance*0.66),
                            self.searchRect(firstFeature, distance, distance)
                        ]

                    for i, searchRect in enumerate(searchRects):
                        #hitIds = list(self.baseIndex.intersection( (searchRect), objects=False))
                        hitIds = self.baseIndex.intersects(searchRect)

                        for pId in hitIds:
                            if pId in nonClustered.keys():
                                feature = self.featureStore[pId]
                                nonClustered.pop(pId)
                                if i == 0:
                                    self.addToCluster(cluster, feature)
                                elif i == 1 and self.version == 3:
                                    unbalancedPoints[pId] = feature

                while len(unbalancedPoints) > 0:
                    pId = unbalancedPoints.keys()[0]
                    unbalancedPoint = unbalancedPoints[pId]
                    #print unbalancedPoint
                    unbalancedPoints.pop(pId)
                    #nearestCluster = list(self.clusterIdx.nearest( (unbalancedPoint[0], unbalancedPoint[1]) ))
                    nearestCluster = self.clusterIdx.nearestNeighbor(QgsPoint(unbalancedPoint.geometry().asPoint().x(), unbalancedPoint.geometry().asPoint().y()), 1)

                    #print nearestCluster
                    for cId in nearestCluster:
                        #print cId
                        cluster = self.clusters[cId]
                        self.addToCluster(cluster, unbalancedPoint)

                self.clusterStore.addClusters(self.clusters, scale, distance)
                self.buildClusterGeometry()

            elif isinstance(foundClusters, dict):
                print "using existing cluster"
                if self.clusters <> foundClusters:
                    self.clusters = foundClusters

                    self.dropClusterGeometry()
                    self.buildClusterGeometry()

            #self.buildClusterGeometry()
            return True
        except RuntimeError:
            warnings.warn("RuntimeError")


    def buildClusterGeometry(self):
        provider = self.__tmpClusterPointLayer.dataProvider()
        fields = provider.fields()

        for cluster in self.clusters.values():
            #print cluster
            feature = QgsFeature()
            feature.setFields(fields)
            feature.setGeometry( QgsGeometry.fromPoint(QgsPoint(cluster.x, cluster.y) ) )
            #print "cluster.scale", type(cluster.scale)
            feature.setAttribute("count", cluster.count)
            feature.setAttribute("scale", cluster.scale)
            feature.setAttribute("distance", cluster.distance)
            feature.setAttribute("id", cluster.clusterId)

            #print "cluster.customColumns", cluster.customColumns
            try:
                for column in cluster.customColumns:
                    print "set attribute", column.shapeName
                    #print "setAttribute", column.shapeName, float(column.evaluate())
                    print "set attribute", column.evaluate()
                    feature.setAttribute(column.shapeName, column.evaluate())
            except:
                raise
                        
            provider.addFeatures([feature])
        #print self.clusterLayer.extent().toString()

        #self.clusterLayers[cluster.scale] = layer
        #return layer

        #error = QgsVectorFileWriter.writeAsVectorFormat(self.__tmpClusterPointLayer, "/tmp/cluster_points.shp", "utf8", None, "ESRI Shapefile")
        self.__tmpClusterPointLayer.reload()

        #print self.tmpClusterShapePath
        return True

    def dropClusterGeometry(self):
        #print "featureCount", self.__tmpClusterPointLayer.featureCount()
        caps = self.__tmpClusterPointLayer.dataProvider().capabilities()
        if caps & QgsVectorDataProvider.DeleteFeatures:
            ids = [feat.id() for feat in self.__tmpClusterPointLayer.getFeatures()]
            #print "all ids", ids
            res = self.__tmpClusterPointLayer.dataProvider().deleteFeatures(ids)
            #print "delete", res
            return res
        #print "featureCount", self.__tmpClusterPointLayer.featureCount()
        return False

    ## function called by canvases scaleChanged signal
    #   @param scale current scale of the canvas
    def updateClusters(self, scale):
        if self.isActive():            
            #if len(self.baseIndex.intersects(self.canvas.extent())) > 0:
            startTime = time.time()
            scale = int(scale)
            zoomlevel = self.canvas.scaleCalculator.getZoomlevel(scale)            
            pixelSize = self.canvas.scaleCalculator.pixelSize(zoomlevel)
            print zoomlevel, pixelSize
            self.buildCluster(zoomlevel, distance=None, pixelSize=pixelSize)
            print "build cluster {0}ms".format((time.time() - startTime) * 1000)
        
###      qgis + rtree
##
#class QgsClusterCalculator(object):

    #def __init__(self, basePointLayer, pixelDistance=50, crs=3857, version=3):
        ##import pandas

        #assert version in [1, 2, 3]
        #self.version = version

        #self.pixelDistance = pixelDistance

        #self.featureStore = {}
        #self.initClusterStore()
        
        ##self.cacheDb = cacheDb
        ##self.tableName = tableName
        ##self.layerName = layerName
        #self.crs = crs
        ##self.basePointLayer = QgsVectorLayer("Point?crs=EPSG:{0}&index=yes".format(self.crs), "CSV Points", "memory")
        #self.basePointLayer = basePointLayer
        #self.clusterPointLayer = QgsVectorLayer("Point?crs=EPSG:{0}&field=id:integer&field=count:integer&field=scale:integer&field=distance:integer&index=yes".format(str(self.crs)), "Cluster Points", "memory")

        ##if isinstance(baseDataFrame, pandas.DataFrame):
            ##self.baseDataFrame = baseDataFrame
        ##else:
            ##raise

        ##self.cacheDb.createClusterTable(tableName, self.crs)

        #startTime = time.time()
        #self.featureStore, self.baseIndex = self.buildSpatialIndex(self.basePointLayer)
        #print "init time {0}ms".format((time.time() - startTime) * 1000)

        ##startTime = time.time()
        ##self.buildCluster(3, distance=978393.962050)
        ##print "build cluster {0}ms".format((time.time() - startTime) * 1000)

        ##self.clusterLayer = self.cacheDb.getSpatialiteVectorLayer(tableName, layerName)

    #def initClusterStore(self):
        #self.clusters = []
        #self.clusterIdx = rtree.index.Index()

    #def buildBasePoints(self, dataFrame, crs, columnId, columnCoordX, columnCoordY, addAllColumns=False):
        #layer = QgsVectorLayer("Point?crs=EPSG:{0}&index=yes".format(str(crs)), "CSV Points", "memory")
        #index = rtree.index.Index()
        #featureStore = {}

        #provider = layer.dataProvider()
        #provider.addAttributes( [QgsField(columnId,  QVariant.Int)] )
        ## TODO:
        ##if addAllColumns:
            ##provider.addAttributes( [QgsField("count",  QVariant.Int)] )
        #fields = provider.fields()

        #for i, row in enumerate(dataFrame.iterrows()):
            #row = row[1]
            #feature = QgsFeature()
            #feature.setFields(fields)
            #feature.setGeometry( QgsGeometry.fromPoint(QgsPoint(row[columnCoordX], row[columnCoordY]) ) )
            #index.insert(row[columnId], [row[columnCoordX], row[columnCoordY]])
            #featureStore[row[columnId]] = [row[columnCoordX], row[columnCoordY], row[columnId]]
            #feature.setAttribute("id", row[columnId])
            #provider.addFeatures([feature])

        #return featureStore, layer, index

    #def buildSpatialIndex(self, layer):        #nonClustered = self.featureStore.copy()
        #unbalancedPoints = {}
        #if pixelSize is not None:
            #distance = pixelSize * self.pixelDistance

        #while len(nonClustered) > 0:
            #firstFeatureId = nonClustered.keys()[0]
            ##print "firstFeatureId", firstFeatureId
            #firstFeature = nonClustered[firstFeatureId]

            #nonClustered.pop(firstFeatureId)
            #cluster = self.createCluster(firstFeature, scale, distance)

            #if self.version == 1:
                #searchRects = [
                    #self.searchRect(firstFeature, distance, distance)
                #]
            #elif self.version == 2:
                #searchRects = [
                    #self.searchRect(firstFeature, distance*0.2, distance),
                    #self.searchRect(firstFeature, distance, distance*0.2),
                    #self.searchRect(firstFeature, distance*0.5, distance*0.88),
                    #self.searchRect(firstFeature, distance*0.88, distance*0.5),
                    #self.searchRect(firstFeature, distance*0.5, distance*0.5)
                #]
            #elif self.version == 3:
                #searchRects = [
                    #self.searchRect(firstFeature, distance*0.66, distance*0.66),
                    #self.searchRect(firstFeature, distance, distance)
                #]

            #for i, searchRect in enumerate(searchRects):
                #hitIds = list(self.baseIndex.intersection( (searchRect), objects=False))

                #for pId in hitIds:
                    #if pId in nonClustered.keys():
                        #feature = self.featureStore[pId]
                        #nonClustered.pop(pId)
                        #if i == 0:
                            #self.addToCluster(cluster, feature)
                        #else:
                            #unbalancedPoints[pId] = feature
        #index = rtree.index.Index()
        #featureStore = {}

        #for feature in layer.getFeatures():
            #index.insert(feature.id(), [feature.geometry().asPoint().x(), feature.geometry().asPoint().y()])
            #featureStore[feature.id()] = [feature.geometry().asPoint().x(), feature.geometry().asPoint().y(), feature.id()]
            
        #return featureStore, index

    ##def buildSpatialIndex(self, layer):
        ##index = QgsSpatialIndex()
        ##featureStore = {}

        ##for feature in layer.getFeatures():
            ##index.insertFeature(feature)
            ###index.insert(feature.id(), [feature.geometry().asPoint().x(), feature.geometry().asPoint().y()])
            ##featureStore[feature.id()] = [feature.geometry().asPoint().x(), feature.geometry().asPoint().y(), feature.id()]

        ##return featureStore, index

    ### return a search box
    ##   @param p point as [x, y]
    ##   @param tx distance in +/- x direction
    ##   @param ty distance in +/- y direction
    #def searchRect(self, p, tx, ty):
        #return (p[0] - tx, p[1] - ty, p[0] + tx, p[1] + ty)

    #def createCluster(self, feature, scale, distance):
        #cluster = ClusterPoint(len(self.clusters), scale, distance)
        #cluster.count = 1
        #cluster.features.append(feature)
        #cluster.addX(feature[0])
        #cluster.addY(feature[1])
        #self.clusters.append(cluster)
        #self.clusterIdx.insert(len(self.clusters) - 1, [feature[0], feature[1]])
        #return cluster

    #def addToCluster(self, cluster, feature):
        #cluster.features.append(feature)
        #cluster.addX(feature[0])
        #cluster.addY(feature[1])
        #cluster.count += 1

    #def buildCluster(self, scale, distance=100000, pixelSize=None):
        #self.dropClusterGeometry()
        #self.initClusterStore()

        #nonClustered = self.featureStore.copy()
        #unbalancedPoints = {}
        #if pixelSize is not None:
            #distance = pixelSize * self.pixelDistance

        #while len(nonClustered) > 0:
            #firstFeatureId = nonClustered.keys()[0]
            ##print "firstFeatureId", firstFeatureId
            #firstFeature = nonClustered[firstFeatureId]

            #nonClustered.pop(firstFeatureId)
            #cluster = self.createCluster(firstFeature, scale, distance)

            #if self.version == 1:
                #searchRects = [
                    #self.searchRect(firstFeature, distance, distance)
                #]
            #elif self.version == 2:
                #searchRects = [
                    #self.searchRect(firstFeature, distance*0.2, distance),
                    #self.searchRect(firstFeature, distance, distance*0.2),
                    #self.searchRect(firstFeature, distance*0.5, distance*0.88),
                    #self.searchRect(firstFeature, distance*0.88, distance*0.5),
                    #self.searchRect(firstFeature, distance*0.5, distance*0.5)
                #]
            #elif self.version == 3:
                #searchRects = [
                    #self.searchRect(firstFeature, distance*0.66, distance*0.66),
                    #self.searchRect(firstFeature, distance, distance)
                #]

            #for i, searchRect in enumerate(searchRects):
                #hitIds = list(self.baseIndex.intersection( (searchRect), objects=False))

                #for pId in hitIds:
                    #if pId in nonClustered.keys():
                        #feature = self.featureStore[pId]
                        #nonClustered.pop(pId)
                        #if i == 0:
                            #self.addToCluster(cluster, feature)
                        #else:
                            #unbalancedPoints[pId] = feature

        #while len(unbalancedPoints) > 0:
            #pId = unbalancedPoints.keys()[0]
            #unbalancedPoint = unbalancedPoints[pId]
            #unbalancedPoints.pop(pId)
            #nearestCluster = list(self.clusterIdx.nearest( (unbalancedPoint[0], unbalancedPoint[1]) ))

            #for cId in nearestCluster:
                #self.addToCluster(self.clusters[cId], unbalancedPoint)

        ##print "clusters created:", len(self.clusters)
        #self.buildClusterGeometry()

        #return True

    #def buildClusterGeometry(self):
        #provider = self.clusterPointLayer.dataProvider()
        #fields = provider.fields()

        #for cluster in self.clusters:
            #feature = QgsFeature()
            #feature.setFields(fields)
            #feature.setGeometry( QgsGeometry.fromPoint(QgsPoint(cluster.x, cluster.y) ) )
            ##print "cluster.scale", type(cluster.scale)
            #feature.setAttribute("count", cluster.count)
            #feature.setAttribute("scale", cluster.scale)
            #feature.setAttribute("distance", cluster.distance)
            #feature.setAttribute("id", cluster.clusterId)
            #provider.addFeatures([feature])
        ##print self.clusterLayer.extent().toString()

        ##self.clusterLayers[cluster.scale] = layer
        ##return layer

        #error = QgsVectorFileWriter.writeAsVectorFormat(self.clusterPointLayer, "/tmp/cluster_points.shp", "utf8", None, "ESRI Shapefile")
        #self.clusterPointLayer.reload()
        #return True

    #def dropClusterGeometry(self):        
        #print "featureCount", self.clusterPointLayer.featureCount()
        #caps = self.clusterPointLayer.dataProvider().capabilities()
        #if caps & QgsVectorDataProvider.DeleteFeatures:
            #ids = [feat.id() for feat in self.clusterPointLayer.getFeatures()]
            ##print "all ids", ids
            #res = self.clusterPointLayer.dataProvider().deleteFeatures(ids)
            ##print "delete", res
        #print "featureCount", self.clusterPointLayer.featureCount()
        #return res


## spatialite version
#class QgsClusterCalculator(object):

    #def __init__(self, baseDataFrame, cacheDb, tableName, layerName, columnId='id', columnCoordX='x', columnCoordY='y', pixelDistance=50, crs=3857, autoBuildLayer=True, version=3):
        #import pandas
        
        #assert version in [1, 2, 3]
        #self.version = version
        
        #self.pixelDistance = pixelDistance        
        ##self.availableScales = []
        ### {'idnr': [x, y, idnr]}
        #self.featureStore = {}
        #self.initClusterStore()
        #self.cacheDb = cacheDb
        #self.tableName = tableName
        #self.layerName = layerName
        #self.crs = crs
        #self.basePointLayer = QgsVectorLayer("Point?crs=EPSG:{0}&index=yes".format(self.crs), "CSV Points", "memory")

        #if isinstance(baseDataFrame, pandas.DataFrame):
            #self.baseDataFrame = baseDataFrame
        #else:bacterias2
            #raise

        #self.cacheDb.createClusterTable(tableName, self.crs)

        #startTime = time.time()
        #if autoBuildLayer:
            #self.featureStore, self.basePointLayer, self.baseIndex = self.buildBasePoints(self.baseDataFrame, self.crs, columnId, columnCoordX, columnCoordY)
        #else:
            #self.featureStore, self.baseIndex = self.buildSpatialIndex(self.baseDataFrame, columnId, columnCoordX, columnCoordY)
        #print "init time {0}ms".format((time.time() - startTime) * 1000)

        #self.clusterLayer = self.cacheDb.getSpatialiteVectorLayer(tableName, layerName)
        
    #def initClusterStore(self):
        #self.clusters = []
        #self.clusterIdx = rtree.index.Index()        
        
    #def buildBasePoints(self, dataFrame, crs, columnId, columnCoordX, columnCoordY, addAllColumns=False):
        #layer = QgsVectorLayer("Point?crs=EPSG:{0}&index=yes".format(str(crs)), "CSV Points", "memory")
        #index = rtree.index.Index()
        #featureStore = {}
        
        #provider = layer.dataProvider()
        #provider.addAttributes( [QgsField(columnId,  QVariant.Int)] )
        ## TODO:
        ##if addAllColumns:
            ##provider.addAttributes( [QgsField("count",  QVariant.Int)] )
        #fields = provider.fields()

        #for i, row in enumerate(dataFrame.iterrows()):
            #row = row[1]
            #feature = QgsFeature()
            #feature.setFields(fields)
            #feature.setGeometry( QgsGeometry.fromPoint(QgsPoint(row[columnCoordX], row[columnCoordY]) ) )
            #index.insert(row[columnId], [row[columnCoordX], row[columnCoordY]])
            #featureStore[row[columnId]] = [row[columnCoordX], row[columnCoordY], row[columnId]]
            #feature.setAttribute("id", row[columnId])
            #provider.addFeatures([feature])

        #return featureStore, layer, index

    #def buildSpatialIndex(self, layer, columnId, columnCoordX, columnCoordY):
        #index = rtree.index.Index()
        #featureStore = {}
        #for row in layer.iterrows():
            #row = row[1]
            #index.insert(row[columnId], [row[columnCoordX], row[columnCoordY]])
            #featureStore[row[columnId]] = [row[columnCoordX], row[columnCoordY], row[columnId]]
        #return featureStore, index

    ### return a search box
    ##   @param p point as [x, y]
    ##   @param tx distance in +/- x direction
    ##   @param ty distance in +/- y direction
    #def searchRect(self, p, tx, ty):
        #return (p[0] - tx, p[1] - ty, p[0] + tx, p[1] + ty)

    #def createCluster(self, feature, scale, distance):
        #cluster = ClusterPoint(len(self.clusters), scale, distance)
        #cluster.count = 1
        #cluster.features.append(feature)
        #cluster.addX(feature[0])
        #cluster.addY(feature[1])
        #self.clusters.append(cluster)
        #self.clusterIdx.insert(len(self.clusters) - 1, [feature[0], feature[1]])
        #return cluster

    #def addToCluster(self, cluster, feature):
        #cluster.features.append(feature)
        #cluster.addX(feature[0])
        #cluster.addY(feature[1])
        #cluster.count += 1

    #def buildCluster(self, scale, distance=100000, pixelSize=None):
        #self.dropClusterGeometry()
        #self.initClusterStore()

        #nonClustered = self.featureStore.copy()
        #unbalancedPoints = {}
        #if pixelSize is not None:
            #distance = pixelSize * self.pixelDistance

        #while len(nonClustered) > 0:
            #firstFeatureId = nonClustered.keys()[0]
            ##print "firstFeatureId", firstFeatureId
            #firstFeature = nonClustered[firstFeatureId]

            #nonClustered.pop(firstFeatureId)
            #cluster = self.createCluster(firstFeature, scale, distance)

            #if self.version == 1:
                #searchRects = [                 
                    #self.searchRect(firstFeature, distance, distance)
                #]
            #elif self.version == 2:
                #searchRects = [
                    #self.searchRect(firstFeature, distance*0.2, distance),
                    #self.searchRect(firstFeature, distance, distance*0.2),
                    #self.searchRect(firstFeature, distance*0.5, distance*0.88),
                    #self.searchRect(firstFeature, distance*0.88, distance*0.5),
                    #self.searchRect(firstFeature, distance*0.5, distance*0.5)                
                #]                
            #elif self.version == 3:
                #searchRects = [
                    #self.searchRect(firstFeature, distance*0.66, distance*0.66),
                    #self.searchRect(firstFeature, distance, distance)
                #]
                
            #for i, searchRect in enumerate(searchRects):
                #hitIds = list(self.baseIndex.intersection( (searchRect), objects=False))

                #for pId in hitIds:
                    #if pId in nonClustered.keys():
                        #feature = self.featureStore[pId]
                        #nonClustered.pop(pId)
                        #if i == 0:
                            #self.addToCluster(cluster, feature)
                        #else:
                            #unbalancedPoints[pId] = feature

        #while len(unbalancedPoints) > 0:
            #pId = unbalancedPoints.keys()[0]
            #unbalancedPoint = unbalancedPoints[pId]
            #unbalancedPoints.pop(pId)
            #nearestCluster = list(self.clusterIdx.nearest( (unbalancedPoint[0], unbalancedPoint[1]) ))

            #for cId in nearestCluster:
                #self.addToCluster(self.clusters[cId], unbalancedPoint)

        ##print "clusters created:", len(self.clusters)
        #self.buildClusterGeometry()
            ##self.availableScales.append(scale)

        #return True

    ##def buildClusterGeometry(self):
        ##provider = self.clusterLayer.dataProvider()
        ###provider = layer.dataProvider()
        ##fields = provider.fields()        

        ##for cluster in self.clusters:
            ##feature = QgsFeature()
            ##feature.setFields(fields)
            ###print feature.fields()
            ##feature.setGeometry( QgsGeometry.fromPoint(QgsPoint(cluster.x, cluster.y) ) )
            ##print "cluster.scale", type(cluster.scale)
            ##feature.setAttribute("count", cluster.count)
            ##feature.setAttribute("scale", cluster.scale)
            ##feature.setAttribute("distance", cluster.distance)
            ##feature.setAttribute("id", cluster.clusterId)
            ##provider.addFeatures([feature])
        ###print self.clusterLayer.extent().toString()

        ##self.clusterLayers[cluster.scale] = layer
        ##return layer

        ###error = QgsVectorFileWriter.writeAsVectorFormat(self.clusterLayer, "/tmp/cluster_points.shp", "utf8", None, "ESRI Shapefile")

    #def dropClusterGeometry(self):
        #self.cacheDb.queryTransaction(u"DELETE FROM {0};".format(self.tableName))           
        #return True

    #def buildClusterGeometry(self):
        #try:
            #connection = self.cacheDb.openPyConnection()
            #cursor = connection.cursor()
            #for cluster in self.clusters:
                #values = {
                    #"tableName": self.tableName,
                    #"id": cluster.clusterId,
                    #"count": cluster.count,
                    #"scale": cluster.scale,
                    #"distance": cluster.distance,
                    #"x": cluster.x,
                    #"y": cluster.y,
                    #"crs": self.crs
                #}
                #sqlCommand = u"""
                        #INSERT INTO {tableName} (id, count, scale, distance, geom)
                        #SELECT {id}, {count}, {scale}, {distance}, SetSRID(MakePoint({x}, {y}), {crs})
                    #""".format(**values)
                #cursor.execute(sqlCommand)
                #connection.commit()
        #except Exception as e:
            #connection.rollback()
            #raise e
        #finally:
            #connection.close()
            
        #self.clusterLayer = self.cacheDb.getSpatialiteVectorLayer(self.tableName, self.layerName)
        #return True