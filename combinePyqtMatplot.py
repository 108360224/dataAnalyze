import copy
import inspect
import sys
import time

import numpy as np
import pandas
import pandas as pd
from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, \
    QPushButton, QSizeGrip, QHBoxLayout, QListWidget, QCheckBox, QListWidgetItem, QStyleOption, QStyle, QLabel
from PyQt5.QtGui import QIcon, QColor, QPainter, QFont, QPen
from PyQt5.QtCore import Qt, QPoint
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets
import seaborn as sns
import random
from numpy.random import randn
#from pyqt5_plugins.examplebutton import QtWidgets

from DragAndDrop import DropWidget,Button

widgetForm, baseClass = uic.loadUiType("plot.ui")
from functools import partial
class PlotWindow(widgetForm, baseClass):
    SCATTER = 1
    BOX_PLOT = 2
    BOX_GROUP_PLOT = 3
    GROUP_PLOT = 4
    HISTOGRAM_PLOT = 5
    PLOT = 6
    def __init__(self):
        super(baseClass, self).__init__()
        self.setupUi(self)
        self.plotCanvas = PlotCanvas()

        #self.splitter.splitterMoved.connect(self.splitterResize)
        

        navi_toolbar = NavigationToolbar(self.plotCanvas, self)

        self.pltLayout.addWidget(navi_toolbar)

        penPB = Button("pen")
        self.pltLayout.addWidget(penPB)
        penPB.clicked.connect(self.plotCanvas.on_penPB_clicked)

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
        self.plotParameterDict = {}

        self.currentColor = list(np.random.choice(range(256), size=3))
        self.currentSetItem=[]
    def runPlotFunction(self,funcname,df):

        if funcname == self.SCATTER:

            if len(df.columns) < 2:
                print("warning select 2 columns")
                return
            try:
                val = int(df[df.columns[0]].values[0])
            except ValueError:
                print("select only number")
                return
            colors = ['#FF0000', '#00FF00', '#0000FF', '#F00000', '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                      '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
            mStyles = ["*", "+", "x", ".", ",", "o", "v", "^", "<", ">", "1", "2", "3", "4", "8", "s", "p", "P", "h",
                       "H",
                       "X", "D", "d", "|", "_", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
                       ]
            if len(df.columns) >= 2:
                for i in range(1, len(df.columns)):
                    # plt.scatter(df[selectedCols[0]], df[selectedCols[i]], c=colors[i], marker=mStyles[i], label=selectedCols[i])
                    self.addPlotFunction(plt.scatter, x=df[df.columns[0]], y=df[df.columns[i]],
                                                    c=colors[i], marker=mStyles[i], label=str(df.columns[i]))
                    d = {df.columns[0]:df[df.columns[0]],df.columns[i]:df[df.columns[i]]}
                    self.plotParameterDict[str(df.columns[i])]={'funcname':funcname,'df':pd.DataFrame(d)}

        if funcname == self.BOX_PLOT:
            self.plotParameterDict['BOX'] = {'funcname': funcname, 'df': df}


            self.addPlotFunction(sns.boxplot,data=df,setYourLabel='BOX')

        if funcname == self.BOX_GROUP_PLOT:
            if len(df.columns) < 2:
                print("warning select 2 columns")
                return
            self.plotParameterDict[str(df.columns[0])] = {'funcname': funcname, 'df': df}


            self.addPlotFunction(sns.boxplot,x=df.columns[0],y=df.columns[1],data=df,setYourLabel=df.columns[0])

        if funcname == self.GROUP_PLOT:
            if len(df.columns) < 3:
                print("warning select 3 columns")
                return
            df = df.sort_values(by=df.columns[0])
            dfgb = df.groupby(df.columns[0])
            dfgb_dict = dfgb.indices
            for key, group in dfgb_dict.items():
                print(key)
                X = df[df.columns[1]][group].values
                Y = df[df.columns[2]][group].values
                idx = list(dfgb_dict.keys()).index(key)
                # plt.scatter(X,Y,label=str(key))
                self.addPlotFunction(plt.scatter, x=X, y=Y, label=str(key))
                d = {df.columns[0]:key,df.columns[1]:X,df.columns[2]:Y}
                self.plotParameterDict[key] = {'funcname': funcname, 'df': pd.DataFrame(d)}
        if funcname == self.HISTOGRAM_PLOT:
            if len(df.columns) > 1:
                print("select only one column")
                return
            try:
                val = int(df[df.columns[0]].values[0])
            except ValueError:
                print("select only number")
                return
            self.plotParameterDict[str(df.columns[0])] = {'funcname': funcname, 'df': df}
            self.addPlotFunction(sns.distplot,a=df[df.columns[0]], hist=True, kde=True, rug=False, bins=int(180/5),
                     color='darkblue',hist_kws={'edgecolor':'black'},
                     kde_kws={'linewidth': 3},
                     rug_kws={'color': 'black'},label=df.columns[0])
        if funcname == self.PLOT:

            for col in df.columns:
                d={col:df[col]}
                self.plotParameterDict[col] = {'funcname': funcname, 'df':pd.DataFrame(d)}
                self.addPlotFunction(plt.plot,df[col],label=col)
    def addPlotFunction(self,func, *args, setYourLabel=None, **kwargs):


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
            pass
        #print(self.plotFuncDict)

    def onLayoutChange(self):
        self.plotCanvas.fig.clf()


        if self.secAxisLayout.count() > 0 and self.fstAxisLayout.count() > 0:
            self.plotCanvas.isOnlyOneAxes = False
            plt.axes(self.plotCanvas.axes121)
            for i in range(self.fstAxisLayout.count()):
                key = self.fstAxisLayout.itemAt(i).widget().text()
                # print("key",key)
                item = self.plotFuncDict[str(key)]
                item['func'](*item['args'], **item['kwargs'])
            plt.legend(loc='upper left')
            plt.axes(self.plotCanvas.axes122)
            for i in range(self.secAxisLayout.count()):
                key = self.secAxisLayout.itemAt(i).widget().text()
                #print("key",key)
                item = self.plotFuncDict[str(key)]
                item['func'](*item['args'],**item['kwargs'])
            plt.legend(loc='upper left')
        else:
            self.plotCanvas.isOnlyOneAxes = True
            plt.axes(self.plotCanvas.axes111)
            for i in range(self.fstAxisLayout.count()):
                key = self.fstAxisLayout.itemAt(i).widget().text()
                # print("key",key)
                item = self.plotFuncDict[str(key)]
                item['func'](*item['args'], **item['kwargs'])
            for i in range(self.secAxisLayout.count()):
                key = self.secAxisLayout.itemAt(i).widget().text()
                # print("key",key)
                item = self.plotFuncDict[str(key)]
                item['func'](*item['args'], **item['kwargs'])
            plt.legend(loc='upper left')
        self.plotCanvas.draw()

    def utils_recognize_type(self,df, col, max_cat=20):
        if (df[col].dtype == "O") | (df[col].nunique() < max_cat):
            return "cat"
        else:
            return "num"
    def creatDfFromTable(self,df):
        df = df.dropna()

        # print(df.head())
        # fig, ax = plt.subplots(nrows=1, ncols=1, sharex=False, sharey=False)
        # print(df.index)
        selected = self.tableWidget.selectedItems()
        selectedCols = []
        selectedRows = []
        if selected:
            for item in selected:
                if df.columns[item.column()] not in selectedCols:
                    selectedCols.append(df.columns[item.column()])
                if item.row() not in selectedRows:
                    selectedRows.append(item.row())
            df = df[selectedCols]
            df = pd.DataFrame(df, index=selectedRows)
        else:
            for col in df.columns:
                if self.utils_recognize_type(df, col) != 'cat':
                    selectedCols.append(col)
            df = df[selectedCols]

        return df,selectedCols,selectedRows
    def setItem(self,list):
        for item in list:
            b = Button(str(item))
            b.setToolTip("Use right mouse button to drag this button")
            b.setStyleSheet("background-color:rgb("+str(self.currentColor[0])+","+
                            str(self.currentColor[1])+","+
                            str(self.currentColor[2])+")")
            b.clicked.connect(partial(self.onButtonClicked, item))
            self.currentSetItem.append(b)
            #self.fstAxisLayout.addWidget(b)

    def onButtonClicked(self,key):


        self.plotCanvas.fig.clf()

        selected = self.tableWidget.selectedItems()
        if selected:

            df, c, r = self.creatDfFromTable(self.eternalplotParameterDict[str(key)]['df'])
            print(df)


            self.runPlotFunction(self.plotParameterDict[str(key)]['funcname'],df)



        df = self.eternalplotParameterDict[str(key)]['df']
        print(df)
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setColumnCount(len(df.columns))
        for i in range(len(df.columns)):
            for j in range(len(df[df.columns[i]])):
                print(df[df.columns[i]][j])
                if i == 0:
                    self.tableWidget.insertRow(self.tableWidget.rowCount())
                self.tableWidget.setItem(j, i, QtWidgets.QTableWidgetItem(str(df[df.columns[i]][j])))

        self.tableWidget.setHorizontalHeaderLabels(df.columns)

        self.onLayoutChange()



    def clearPlot(self):
        self.plotCanvas.fig.clf()
        self.plotFuncDict = {}
        self.plotParameterDict={}
        self.eternalplotParameterDict={}
        self.tableWidget.clear()
        for i in range(self.fstAxisLayout.count()-1,-1,-1):
            self.fstAxisLayout.itemAt(i).widget().setParent(None)
        for i in range(self.itemLayout.count()-1,-1,-1):
            self.itemLayout.itemAt(i).widget().setParent(None)
        for i in range(self.secAxisLayout.count()-1,-1,-1):
            self.secAxisLayout.itemAt(i).widget().setParent(None)


    def show(self):
        super().show()
        self.eternalplotParameterDict = copy.deepcopy(self.plotParameterDict)
        self.tableWidget.clear()




        for i in range(self.secAxisLayout.count()-1,-1,-1):
            print(i)
            self.itemLayout.addWidget(self.secAxisLayout.itemAt(i).widget())
            #self.secAxisLayout.itemAt(i).widget().setParent(None)

        for i in range(self.fstAxisLayout.count()-1,-1,-1):
            print(i)
            self.itemLayout.addWidget(self.fstAxisLayout.itemAt(i).widget())
            #self.fstAxisLayout.itemAt(i).widget().setParent(None)
        for b in self.currentSetItem:
            self.fstAxisLayout.addWidget(b)
        self.onLayoutChange()
        self.currentSetItem = []
        self.currentColor = list(np.random.choice(range(125,256), size=3))
    def closeEvent(self, event):
        # do stuff
        self.clearPlot()
        event.accept()  # let the window close






class PlotCanvas(FigureCanvas):

    def __init__(self, width=8, height=6, dpi=100):
        self.fig = plt.figure(figsize=(width, height), dpi=dpi)
        self.axes111 = self.fig.add_subplot(111)
        self.axes121 = self.fig.add_subplot(121)
        self.axes122 = self.fig.add_subplot(122)
        super(FigureCanvas, self).__init__(self.fig)
        self.fig.canvas.mpl_connect('button_press_event', self.button_press_event)
        self.fig.canvas.mpl_connect('motion_notify_event', self.motion_notify_event)
        self.fig.canvas.mpl_connect('button_release_event', self.button_release_event)
        self.isOnlyOneAxes = True
        self.drawList = []
        self.xx, self.yy=0,0
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.drawing = False
        self.lastPoint = QPoint()
        self.isButtonPress = False
        self.havePen = False
    def draw(self):
        if self.isOnlyOneAxes:
            for d in self.drawList:
                plt.axes(self.axes111)
                d['func'](*d['args'], **d['kwargs'])
        else:
            for d in self.drawList:
                plt.axes(self.axes121)
                d['func'](*d['args'], **d['kwargs'])
                plt.axes(self.axes122)
                d['func'](*d['args'], **d['kwargs'])
        super(FigureCanvas, self).draw()

    def on_penPB_clicked(self):
        self.havePen = not self.havePen

    def button_press_event(self, event):
        if self.havePen:
            self.isButtonPress = True
            self.currentPos = np.array([[event.xdata, event.ydata]])
            print(self.currentPos)
    def motion_notify_event(self,event):

        if self.isButtonPress:
            if self.isOnlyOneAxes:
                plt.axes(self.axes111)
                plt.plot([self.currentPos[-1,0], event.xdata], [self.currentPos[-1,1], event.ydata], 'g--')
            else:
                plt.axes(self.axes121)
                plt.plot([self.currentPos[-1,0], event.xdata], [self.currentPos[-1,1], event.ydata], 'g--')
                plt.axes(self.axes122)
                plt.plot([self.currentPos[-1,0], event.xdata], [self.currentPos[-1,1], event.ydata], 'g--')

            self.currentPos = np.concatenate([self.currentPos,np.array([[event.xdata, event.ydata]])])
            print(self.currentPos)
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()


    def button_release_event(self, event):
        self.isButtonPress = False
        self.appendDrawList(plt.plot, self.currentPos[:,0], self.currentPos[:,1],'g--')
    def appendDrawList(self,func,*args,**kwargs):
        self.drawList.append({'func': func, 'args':args,'kwargs':kwargs})

if __name__ == '__main__':

    '''
    app = QtWidgets.QApplication([])
    window = PlotWindow()
    window.setWindowFlags(QtCore.Qt.Window)
    window.show()  # é¡¯ç¤ºè¦– ?
    sys.exit(app.exec_())
    '''
