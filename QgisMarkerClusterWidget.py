from ui_QgisMarkerClusterDockWidget import Ui_QgisMarkerClusterDockWidget
from PyQt4 import QtGui

class QgisMarkerClusterDockWidget(QtGui.QDockWidget, Ui_QgisMarkerClusterDockWidget):

    def __init__(self):
        super(QgisMarkerClusterDockWidget, self).__init__()        
        self.setupUi(self)
        self.show()