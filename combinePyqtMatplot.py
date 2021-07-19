import copy
import inspect
import sys
import time

import numpy as np
from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, \
    QPushButton, QSizeGrip, QHBoxLayout, QListWidget, QCheckBox, QListWidgetItem
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import random
from numpy.random import randn
from pyqt5_plugins.examplebutton import QtWidgets
from DragAndDrop import DropWidget,Button
widgetForm, baseClass = uic.loadUiType("plot.ui")
from functools import partial

class PlotWindow(widgetForm, baseClass):
    def __init__(self):
        super(baseClass, self).__init__()
        self.setupUi(self)
        self.plotCanvas = PlotCanvas()

        #self.splitter.splitterMoved.connect(self.splitterResize)
        

        navi_toolbar = NavigationToolbar(self.plotCanvas, self)

        self.pltLayout.addWidget(navi_toolbar)
        self.pltLayout.addWidget(self.plotCanvas)

        self.fstAxisLayout = QHBoxLayout()
        self.fstAxisLayout.setAlignment(Qt.AlignLeft)
        fstWidget = DropWidget(self, self.fstAxisLayout)
        fstWidget.setLayout(self.fstAxisLayout)


        self.secAxisLayout = QHBoxLayout()
        self.secAxisLayout.setAlignment(Qt.AlignLeft)
        secWidget = DropWidget(self, self.secAxisLayout)
        secWidget.setLayout(self.secAxisLayout)


        self.itemLayout = QVBoxLayout()
        self.itemLayout.setAlignment(Qt.AlignTop)
        itemWidget = DropWidget(self, self.itemLayout)
        itemWidget.setLayout(self.itemLayout)

        self.SecLayout.addWidget(secWidget)
        self.FstLayout.addWidget(fstWidget)
        self.ListLayout.addWidget(itemWidget)

        self.plotFuncDict = {}
        self.funcList = []
        self.currentColor = list(np.random.choice(range(256), size=3))


    def runPlotFunction(self,func, *args, setYourLabel=None, **kwargs):

        if not setYourLabel == None:
            if not str(setYourLabel) in self.plotFuncDict:
                self.setItem([str(setYourLabel)])
                self.plotFuncDict[str(setYourLabel)] = {'func': func, 'args': args, 'kwargs': kwargs}
            else:
                self.plotFuncDict[str(setYourLabel)] = {'func': func, 'args': args, 'kwargs': kwargs}

        elif 'label' in kwargs:
            if not str(kwargs['label']) in self.plotFuncDict:
                self.setItem([str(kwargs['label'])])
                self.plotFuncDict[str(kwargs['label'])] = {'func': func, 'args':args, 'kwargs':kwargs}
            else:
                self.plotFuncDict[str(kwargs['label'])] = {'func': func, 'args': args, 'kwargs': kwargs}

        else:
            self.funcList.append({'func': func, 'args':args, 'kwargs':kwargs})
        #print(self.plotFuncDict)

    def onLayoutChange(self):
        self.plotCanvas.fig.clf()


        if self.secAxisLayout.count() > 0:
            plt.subplot(1, 2, 1)
            for i in range(self.fstAxisLayout.count()):
                key = self.fstAxisLayout.itemAt(i).widget().text()
                # print("key",key)
                item = self.currentPlotFuncDict[str(key)]
                item['func'](*item['args'], **item['kwargs'])
            for f in self.funcList:
                f['func'](*f['args'], **f['kwargs'])
            plt.subplot(1, 2, 2)
            for i in range(self.secAxisLayout.count()):
                key = self.secAxisLayout.itemAt(i).widget().text()
                #print("key",key)
                item = self.currentPlotFuncDict[str(key)]
                item['func'](*item['args'],**item['kwargs'])
            for f in self.funcList:
                f['func'](*f['args'], **f['kwargs'])
        else:
            plt.subplot(1, 1, 1)
            for i in range(self.fstAxisLayout.count()):
                key = self.fstAxisLayout.itemAt(i).widget().text()
                # print("key",key)
                item = self.currentPlotFuncDict[str(key)]
                item['func'](*item['args'], **item['kwargs'])
            for f in self.funcList:
                f['func'](*f['args'], **f['kwargs'])
        self.plotCanvas.draw()



    def setItem(self,list):
        for item in list:
            b = Button(str(item))
            b.setToolTip("Use right mouse button to drag this button")
            b.setStyleSheet("background-color:rgb("+str(self.currentColor[0])+","+
                            str(self.currentColor[1])+","+
                            str(self.currentColor[2])+")")
            b.clicked.connect(partial(self.onButtonClicked, item))
            self.fstAxisLayout.addWidget(b)

    def onButtonClicked(self,key):


        self.plotCanvas.fig.clf()

        selects = self.tableWidget.selectedItems()
        if selects:
            self.currentPlotFuncDict[str(key)]['kwargs']['x'] = np.zeros(int(len(selects)/2))
            self.currentPlotFuncDict[str(key)]['kwargs']['y'] = np.zeros(int(len(selects)/2))
            col0count=0
            col1count=0
            for select in selects:
                row = select.row()
                if select.column() == 0:
                    self.currentPlotFuncDict[str(key)]['kwargs']['x'][col0count] = copy.deepcopy(self.plotFuncDict[str(key)]['kwargs']['x'][row])
                    col0count = col0count + 1
                if select.column() == 1:
                    self.currentPlotFuncDict[str(key)]['kwargs']['y'][col1count] = copy.deepcopy(self.plotFuncDict[str(key)]['kwargs']['y'][row])
                    col1count = col1count + 1

            if not len(self.currentPlotFuncDict[str(key)]['kwargs']['x']) == len(self.currentPlotFuncDict[str(key)]['kwargs']['y']):
                msg = QMessageBox()
                msg.setText("X and Y must be the same size")
                msg.setWindowTitle("hint")
                msg.exec_()
                return

            plt.subplot(1, 2, 1)
            for i in range(self.fstAxisLayout.count()):
                key = self.fstAxisLayout.itemAt(i).widget().text()
                # print("key",key)
                item = self.currentPlotFuncDict[str(key)]
                item['func'](*item['args'], **item['kwargs'])
            for f in self.funcList:
                f['func'](*f['args'], **f['kwargs'])

            plt.subplot(1, 2, 2)
            for i in range(self.secAxisLayout.count()):
                key = self.secAxisLayout.itemAt(i).widget().text()
                # print("key",key)
                item = self.currentPlotFuncDict[str(key)]
                item['func'](*item['args'], **item['kwargs'])
            for f in self.funcList:
                f['func'](*f['args'], **f['kwargs'])

            self.plotCanvas.draw()



        else:
            item = self.plotFuncDict[str(key)]

            if 'y' in item['kwargs']:
                ydata = item['kwargs']['y']
            if 'x' in item['kwargs']:
                xdata = item['kwargs']['x']
            try:
                print('args ', item['args'])
                data = item['args'][0]
            except:
                pass

            self.tableWidget.clear()
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)

            for i in range(len(xdata)):
                self.tableWidget.insertRow(self.tableWidget.rowCount())
                self.tableWidget.setColumnCount(2)
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 0, QtWidgets.QTableWidgetItem(str(xdata[i])))
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 1, QtWidgets.QTableWidgetItem(str(ydata[i])))

        '''
        box = QCheckBox(str(i))
        item = QListWidgetItem()
        self.ValuelistWidget.addItem(item)
        #self.ValueListWidget.addItem(str(i))
        box.stateChanged.connect(self.filterCheckBoxChangeState)
        self.ValuelistWidget.setItemWidget(item, box)
        '''



    def clearPlot(self):
        self.plotCanvas.fig.clf()
        self.plotFuncDict = {}
        self.funcList = []
        self.tableWidget.clear()
        for i in reversed(range(self.fstAxisLayout.count())):
            self.fstAxisLayout.itemAt(i).widget().setParent(None)
        for i in reversed(range(self.itemLayout.count())):
            self.itemLayout.itemAt(i).widget().setParent(None)
        for i in reversed(range(self.secAxisLayout.count())):
            self.secAxisLayout.itemAt(i).widget().setParent(None)


    def show(self):
        super().show()

        self.currentPlotFuncDict = copy.deepcopy(self.plotFuncDict)
        self.onLayoutChange()
        self.plotCanvas.draw()
        self.currentColor = list(np.random.choice(range(256), size=3))

    def closeEvent(self, event):
        # do stuff
        self.clearPlot()
        event.accept()  # let the window close





class PlotCanvas(FigureCanvas):

    def __init__(self, width=8, height=6, dpi=100):
        self.fig = plt.figure(figsize=(width, height), dpi=dpi)
        self.axes2 = self.fig.add_subplot(1, 2, 2)
        self.axes1 = self.fig.add_subplot(1, 2, 1)

        FigureCanvas.__init__(self, self.fig)


        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)



if __name__ == '__main__':

    '''
    app = QtWidgets.QApplication([])
    window = PlotWindow()
    window.setWindowFlags(QtCore.Qt.Window)
    window.show()  # é¡¯ç¤ºè¦– ?
    sys.exit(app.exec_())
    '''
