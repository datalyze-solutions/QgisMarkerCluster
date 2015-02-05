#/***************************************************************************
# TileMapScalePlugin
#
# Let you add tiled datasets (GDAL WMS) and shows them in the correct scale.
#                             -------------------
#        begin                : 2014-03-03
#        copyright            : (C) 2014 by Matthias Ludwig - Datalyze Solutions
#        email                : m.ludwig@datalyze-solutions.com
# ***************************************************************************/
#
#/***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/

# CONFIGURATION
PLUGIN_UPLOAD = $(CURDIR)/plugin_upload.py

QGISDIR=.qgis2

# Makefile for a PyQGIS plugin

# translation
SOURCES = QgisMarkerCluster.py ui_info.py __init__.py QgisMarkerClusterWidget.py
#TRANSLATIONS = i18n/tilemapscaleplugin_en.ts
TRANSLATIONS =

# global

PLUGINNAME = QgisMarkerCluster

PY_FILES = QgisMarkerCluster.py __init__.py QgisMarkerClusterWidget.py

LIBS = libs/__init__.py \
	libs/QgsClusterLayer.py \
	libs/QgsLayerStyles.py \
	libs/tilemapscalelevels.py \

EXTRAS = metadata.txt \
	INFO.html \
	README.txt \

ICONS = icons/draw-freehand.png \
	icons/ds_logo.png \
	icons/ds_made_by.png \
	icons/example.jpg \
	icons/help-about.png \
	icons/icon.png \
	icons/list-add.png \
	icons/osm.png \
	icons/view-refresh.png \

SVG = datasets/styles/svg/shadow_circle.svg

STYLES = datasets/styles/little_gray_point.qml \
	datasets/styles/simple_cluster.qml \
	
DATASETS = datasets/licence.txt \
	datasets/stations_3857.dbf \
	datasets/stations_3857.prj \
	datasets/stations_3857.qpj \
	datasets/stations_3857.shp \
	datasets/stations_3857.shx \

UI_FILES = ui_info.py ui_QgisMarkerClusterDockWidget.py

RESOURCE_FILES = resources_rc.py

HELP = help/build/html

default: compile

compile: $(UI_FILES) $(RESOURCE_FILES)

%_rc.py : %.qrc
	pyrcc4 -o $*_rc.py  $<

%.py : %.ui
	pyuic4 -o $@ $<

%.qm : %.ts
	lrelease $<

# The deploy  target only works on unix like operating system where
# the Python plugin directory is located at:
# $HOME/$(QGISDIR)/python/plugins
deploy: compile doc transcompile
	mkdir -p $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	mkdir -p $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/icons
	mkdir -p $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/libs
	mkdir -p $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/datasets/styles/svg
	cp -vf $(PY_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(LIBS) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/libs
	cp -vf $(DATASETS) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/datasets
	cp -vf $(STYLES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/datasets/styles
	cp -vf $(SVG) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/datasets/styles/svg
	cp -vf $(UI_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(RESOURCE_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(EXTRAS) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(ICONS) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/icons
	cp -vfr i18n $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vfr $(HELP) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/help

# The dclean target removes compiled python files from plugin directory
# also delets any .svn entry
dclean:
	find $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME) -iname "*.pyc" -delete
	find $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME) -iname ".svn" -prune -exec rm -Rf {} \;

# The derase deletes deployed plugin
derase:
	rm -Rf $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)

# The zip target deploys the plugin and creates a zip file with the deployed
# content. You can then upload the zip file on http://plugins.qgis.org
zip: deploy dclean
	rm -f $(PLUGINNAME).zip
	cd $(HOME)/$(QGISDIR)/python/plugins; zip -9r $(CURDIR)/$(PLUGINNAME).zip $(PLUGINNAME)

# Create a zip package of the plugin named $(PLUGINNAME).zip.
# This requires use of git (your plugin development directory must be a
# git repository).
# To use, pass a valid commit or tag as follows:
#   make package VERSION=Version_0.3.2
package: compile
		rm -f $(PLUGINNAME).zip
		git archive --prefix=$(PLUGINNAME)/ -o $(PLUGINNAME).zip $(VERSION)
		echo "Created package: $(PLUGINNAME).zip"

upload: zip
	$(PLUGIN_UPLOAD) $(PLUGINNAME).zip

# transup
# update .ts translation files
transup:
	pylupdate4 Makefile

# transcompile
# compile translation files into .qm binary format
transcompile: $(TRANSLATIONS:.ts=.qm)

# transclean
# deletes all .qm files
transclean:
	rm -f i18n/*.qm

clean:
	rm $(UI_FILES) $(RESOURCE_FILES)

# build documentation with sphinx
doc:
	cd help; make html