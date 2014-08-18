# -*- coding: utf-8 -*-
#  @file QgsLayerStyles
#       Contains methods for typical symbols

from qgis.gui import *
from qgis.core import *
import os
import math

class ColorLibrary(object):

    def __init__(self):
        self.reds = [
            '215,25,28', # dunkel
            '251,128,114', # mittel
            '251,180,174' # hell
        ]

        self.blues = [
            '55,126,184', # dunkel
            '128,177,211', # mittel
            '179,205,227', # hell
        ]
        
        self.yellows = [
            '255,255,153', # mittel
            '255,255,51', # kräftig
            '255,255,179', # hell
        ]

class SymbolLibrary(object):

    def __init__(self, config):
        self.config = config
        self.colors = ColorLibrary()

    #####################
    ### apply symbols ###
    #####################
    def setSymbol(self, layer, symbol):
        renderer = QgsSingleSymbolRendererV2(symbol)
        layer.setRendererV2(renderer)
    
    def setSymbolGraduated(self, layer, rangeList, valueField):
        renderer = QgsGraduatedSymbolRendererV2('', rangeList)
        #renderer.setMode(QgsGraduatedSymbolRendererV2.EqualInterval)
        renderer.setClassAttribute(valueField)
        layer.setRendererV2(renderer)

    def setLabeling(self, layer, labelField, xOffset, angle, fontSize='8'):
        labelSettings = QgsPalLayerSettings()
        labelSettings.readFromLayer(layer)

        labelSettings.enabled = True
        labelSettings.fieldName = labelField
        labelSettings.placement = QgsPalLayerSettings.OverPoint

        #print "units", labelSettings.labelOffsetInMapUnits, labelSettings.DistanceUnits
        labelSettings.setDataDefinedProperty(QgsPalLayerSettings.OffsetUnits,True,True,'1','')

        labelSettings.xOffset = math.cos(math.radians(angle-30.0+120)) * xOffset
        labelSettings.yOffset = math.sin(math.radians(angle-30.0+120)) * xOffset
        #print "units", labelSettings.labelOffsetInMapUnits

        # font size
        labelSettings.setDataDefinedProperty(QgsPalLayerSettings.Size, True, True, fontSize, '')

        labelSettings.writeToLayer(layer)
        #layer.setCustomProperty("labeling/fontFamily", "Arial")
        #layer.setCustomProperty("labeling/fontSize", "8")

    ####################
    ### symbol layer ###
    ####################
    def getSymbolLayerCircle(self, angle, color, colorBorder, size, offset):
        symbolLayer = QgsSimpleMarkerSymbolLayerV2.create({
            'color': color,
            'color_border': colorBorder,
            'size': str(size),
            'offset': offset,
            'angle': str(angle)
        })
        return symbolLayer
        
    def getSymbolLayerShadowCircle(self, size, angle, offset):
        symbolLayer = QgsSvgMarkerSymbolLayerV2.create({
            'size': str(size),
            'angle': str(angle),
            'offset': offset
        })
        print os.path.join(self.config.appPath, "datasets/styles/svg", "shadow_circle.svg")
        symbolLayer.setPath(os.path.join(self.config.appPath, "datasets/styles/svg", "shadow_circle.svg"))
        return symbolLayer

    ###############
    ### symbols ###
    ###############
    def getSymbolColorWhiteCircle(self, geometryType, angle, color, colorBorder, size, offset='0,0', shadow=True, shadowMulti=2.3):
        symbol = QgsSymbolV2.defaultSymbol(geometryType)
        colorLayer = self.getSymbolLayerCircle(angle, color, colorBorder, size, offset)
        symbol.changeSymbolLayer(0, colorLayer)

        whiteTransparent = '255,255,255,200'
        whiteLayer = self.getSymbolLayerCircle(angle, whiteTransparent, whiteTransparent, size*1.33, offset)
        #symbol.insertSymbolLayer(0, whiteLayer)

        if shadow:
            shadowLayer = self.getSymbolLayerShadowCircle(size*shadowMulti, angle, offset)
            symbol.insertSymbolLayer(0, shadowLayer)
        return symbol

    def getSymbolColorCircle(self, geometryType, angle, color, colorBorder, size, offset='0,0', shadow=True, shadowMulti=2.3):
        print "geometryType", geometryType
        symbol = QgsSymbolV2.defaultSymbol(geometryType)
        colorLayer = self.getSymbolLayerCircle(angle, color, colorBorder, size, offset)
        symbol.changeSymbolLayer(0, colorLayer)
        
        if shadow:
            shadowLayer = self.getSymbolLayerShadowCircle(size*shadowMulti, angle, offset)
            symbol.insertSymbolLayer(0, shadowLayer)
        return symbol

#def setAttributeSymbol(layer, angle, color, colorBorder='150,150,150', size=2.8, offset='0, 4.2', shadow=False):
    #symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
    #renderer = QgsSingleSymbolRendererV2(symbol)

    #properties = {
        #'color': color,
        #'color_border': colorBorder,
        #'size': str(size),
        #'offset': offset,
        #'angle': str(angle)
    #}
    #symbol_layer = QgsSimpleMarkerSymbolLayerV2.create(properties)
    #renderer.symbols()[0].changeSymbolLayer(0, symbol_layer)
    ##renderer.symbols()[0].appendSymbolLayer(symbol_layer)

    #if shadow:
        #properties = {
            #'size': str(size*2.0),
            #'offset': offset,
            #'angle': str(angle)
        #}
        #symbol_layer = QgsSvgMarkerSymbolLayerV2.create(properties)
        #symbol_layer.setPath("/home/kaotika/.qgis2/svg/black_fill2.svg")
        ##symbol_layer.setPath("/home/kaotika/.qgis2/svg/shadow_black.svg")
        ##renderer.symbols()[0].changeSymbolLayer(0, symbol_layer)
        #renderer.symbols()[0].insertSymbolLayer(0, symbol_layer)

    #layer.setRendererV2(renderer)

#def setClusterSymbol(layer, color, colorBorder='255,255,255, 200', size=8, offset='0,0', shadow=True):
    #symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
    #renderer = QgsSingleSymbolRendererV2(symbol)

    ##properties = {
        ###'color': 'rgb(237, 248, 233)',
        ##'color': color,
        ##'color_border': colorBorder,
        ##'size': str(size)
    ##}
    ##symbol_layer = QgsSimpleMarkerSymbolLayerV2.create(properties)
    ##renderer.symbols()[0].changeSymbolLayer(0, symbol_layer)
    ##renderer.symbols()[0].appendSymbolLayer(symbol_layer)   

    #properties = {
        ##'color': 'white',
        #'color': colorBorder,
        #'color_border': colorBorder,
        #'size': str(size*1.8)        
    #}
    #symbol_layer = QgsSimpleMarkerSymbolLayerV2.create(properties)
    #renderer.symbols()[0].changeSymbolLayer(0, symbol_layer)
    ##renderer.symbols()[0].insertSymbolLayer(0, symbol_layer)

    #if shadow:
        #properties = {
            #'size': str(size*2.8)
        #}
        #symbol_layer = QgsSvgMarkerSymbolLayerV2.create(properties)
        #symbol_layer.setPath("/home/kaotika/.qgis2/svg/black_fill2.svg")
        ##symbol_layer.setPath("/home/kaotika/.qgis2/svg/shadow_black.svg")
        #renderer.symbols()[0].insertSymbolLayer(0, symbol_layer)

    ##layer.setCustomProperty("labeling", "pal")
    ##layer.setCustomProperty("labeling/enabled", "true")
    ###layer.setCustomProperty("labeling/fontFamily", "Arial")
    ##layer.setCustomProperty("labeling/fontSize", "8")
    ##layer.setCustomProperty("labeling/fieldName", "v1_count")
    ### cet centered position
    ##layer.setCustomProperty("labeling/placement", "1")

    #layer.setRendererV2(renderer)
    
#def setGraduatedSymbol(layer, angle, color, colorBorder='150,150,150', size=6, offset='0,4', shadow=False, labeling=True, labelField='id'):

    #rangeList = []
    
    ## Make our first symbol and range...
    #myMin = 0.0
    #myMax = 0.0
    #myLabel = 'Group 1'

    ##symbol = getPointSymbolWithShadow(layer.geometryType(), )
    
    #mySymbol1 = QgsSymbolV2.defaultSymbol(layer.geometryType())

    #properties = {
        #'color': 'white',
        #'color_border': colorBorder,
        #'size': str(size),
        #'offset': offset,
        #'angle': str(angle)
    #}
    #symbolLayer1 = QgsSimpleMarkerSymbolLayerV2.create(properties)    
    #mySymbol1.changeSymbolLayer(0, symbolLayer1)
    
    #myRange1 = QgsRendererRangeV2(myMin, myMax, mySymbol1, myLabel)
    #rangeList.append(myRange1)

    ##now make another symbol and range...
    #myMin = 0
    #myMax = 9999999
    #myLabel = 'Group 2'

    #mySymbol2 = QgsSymbolV2.defaultSymbol(layer.geometryType())
    #properties = {
        #'color': color,
        #'color_border': colorBorder,
        #'size': str(size),
        #'offset': offset,
        #'angle': str(angle)
    #}
    #symbolLayer2 = QgsSimpleMarkerSymbolLayerV2.create(properties)
    #mySymbol2.changeSymbolLayer(0, symbolLayer2)
    
    #myRange2 = QgsRendererRangeV2(myMin, myMax, mySymbol2, myLabel)
    #rangeList.append(myRange2)
    #myRenderer = QgsGraduatedSymbolRendererV2('', rangeList)
    #myRenderer.setMode(QgsGraduatedSymbolRendererV2.EqualInterval)
    #myRenderer.setClassAttribute(labelField)
    
    ##layer.setCustomProperty("labeling", "pal")
    ##print "enabled", layer.customProperty("labeling/fieldName").toString()
    ###layer.setCustomProperty("labeling/fontFamily", "Arial")
    ##layer.setCustomProperty("labeling/fontSize", "8")

    #if labeling:        
        #layer.setCustomProperty("labeling/enabled", "true")
        #layer.setCustomProperty("labeling/fieldName", labelField)
    
    ### cet centered position enum QgsPalLayerSettings::Placement)
    ##layer.setCustomProperty("labeling/placement", "1")

    #layer.setRendererV2(myRenderer)