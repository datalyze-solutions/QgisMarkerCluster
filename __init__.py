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

def classFactory(iface):
    from QgisMarkerCluster import QgisMarkerCluster
    return QgisMarkerCluster(iface)