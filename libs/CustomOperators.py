# -*- coding: utf-8 -*-
#  @file
#       Contains methods to add numpy and custom operators to clusterpoints

from PyQt4 import QtGui 
from PyQt4 import QtCore
from PyQt4.QtCore import Qt
import numpy

class CustomOperator(object):

    def __init__(self, description, operator):
        self.description = description
        self.operator = operator

    def __repr__(self):
        string = u"CustomOperator({0}): {1} ({2})".format(hex(id(self)), self.description, self.operator)
        string = string.encode("utf-8")
        return string

customOperators = [
    CustomOperator(u"Zähle Werte die nicht Null sind", numpy.count_nonzero),
    #CustomOperator(u"Durchschnitt", numpy.mean),
    #CustomOperator(u"Minimum", numpy.max),
    #CustomOperator(u"Maximum", numpy.min),
    CustomOperator(u"Zähle alles (inklusive Null Werten)", lambda x: len(x)),
    #CustomOperator(u"Liste eindeutige Werte auf", lambda x: ";".join(set(str(x)))),
]

class CustomOperatorModel(QtCore.QAbstractTableModel):

    def __init__(self):
        super(CustomOperatorModel, self).__init__()
        self.header = ['Beschreibung']
        self.operators = customOperators

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self.operators)

    def columnCount(self, index=QtCore.QModelIndex()):
        return len(self.header)

    def headerData(self, column, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QtCore.QVariant(self.header[column])
        return None

    def data(self, index, role=Qt.DisplayRole):
        column = index.column()
        operator = self.operators[index.row()]
        if role == Qt.DisplayRole:
            if column == 0:
                return QtCore.QVariant(operator.description)
        elif role == Qt.UserRole:
            return operator

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable


class CustomOperatorComboDelegate(QtGui.QItemDelegate):

    def __init__(self, parent):
        super(CustomOperatorComboDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        combo = QtGui.QComboBox(parent)
        self.model = CustomOperatorModel()
        combo.setModel(self.model)

        combo.currentIndexChanged.connect(self.currentIndexChanged)
        return combo

    def setEditorData(self, editor, index):
        editor.blockSignals(True)
        editor.setCurrentIndex(0)
        editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentIndex())

    @QtCore.pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())