import sys
import pandas as pd
import numpy as np
## for plotting
import matplotlib
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QPushButton, QScrollArea, QCheckBox, QListWidgetItem, QListWidget, QVBoxLayout, QWidget, \
    QMessageBox, QAbstractItemView, QLabel, QLineEdit, QHBoxLayout,QGroupBox
from sklearn.model_selection import train_test_split
from lmfit import Model, report_fit, Parameters
import pyqtgraph as pg
import matplotlib.pyplot as plt
import seaborn as sns
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5 import uic
import shutil
import re
import os
from datetime import datetime
from PyQt5.QtCore import QDir, pyqtSignal, QObject
from combinePyqtMatplot import PlotWindow
class FileReader():
    def __init__(self):
        self.IndexFileMap = []
        self.IndexDataframeMap = {}
        self.filename = ''

    def openFile(self, name):
        if name == '':
            return -1
        print("File Name:",name)
        index = -1
        if self.fileHavingMultipleDataFormat(name):
            print(name," have multiple data format")
            return index
        self.filename = name
        self.getFullPath()
        index = self.getFileIndex()
        if index < 0:
            self.IndexFileMap.append(self.filename)
            try:
                df = pd.read_csv(self.filename)
                self.IndexDataframeMap[len(self.IndexFileMap)-1] = df
                index = len(self.IndexFileMap)-1
            except:
                print('Exception in read file Panda')

        return index

    def fileHavingMultipleDataFormat(self, name):
        base, ext = os.path.splitext(name)
        if(ext == ".csv"):
            lineCount = 0
            wordCount = 0
            formats = []
            with open(name) as fp:
                for line in fp:
                    line = line.strip()
                    if(lineCount == 0):
                        formats.append(line)

                    tempList = line.split(",")
                    while '' in tempList:
                        tempList.remove('')

                    if lineCount and len(tempList) != wordCount:
                        print("Format changed, row %d, column %d"%(lineCount, wordCount))
                        print(line)
                        formats.append(line)
                    lineCount += 1
                    wordCount = len(tempList)
            if len(formats) > 1:
                return True
            else:
                return False
        return False

    def getFullPath(self):
        try:
            if not os.path.isabs(self.filename):
                self.filename = QtCore.QDir.currentPath()+"/"+self.filename
                print(self.filename)
        except:
            print("Exception in filename:", self.filename)
        if not os.path.exists(self.filename):
            print(self.filename, " does not exists")

    def getFileIndex(self):
        if self.filename == '':
            return -1
        self.getFullPath()
        index = -1
        if self.filename in self.IndexFileMap:
            for i in range(0, len(self.IndexFileMap)):
                if self.filename == self.IndexFileMap[i]:
                    index = i
            if (os.path.samefile(self.filename, self.IndexFileMap[i])):
                print("File already open in tab:", index)
                #self.openFilesTabWidget.setCurrentIndex(index)
            else:
                index = -1
        return index

    def getCurrentDataFrame(self):
        print("getCurrentDataFrame")

    def getDataFrame(self, index):
        print("getDataFrame")
    def getDataFrame(self, fileName):
        print("getDataFrame")
    def getCurrentFileIndex(self, tab):
        print("getDataFrame")
    def closeFile(self,index):
        print("Closing file")

widgetForm, baseClass = uic.loadUiType("test.ui")
def utils_recognize_type(dtf, col, max_cat=20):
    if (dtf[col].dtype == "O") | (dtf[col].nunique() < max_cat):
        return "cat"
    else:
        return "num"


class table_dragFile_injector():
    def __init__(self, table, auto_inject = True):
        self.table = table
        self.handler = None
        if auto_inject:
            self.inject_dragFile()

    def inject_dragFile( self ):
        self.table.setDragEnabled(True)
        self.table.viewport().setAcceptDrops(True)
        self.table.setDragDropOverwriteMode(False)
        self.table.setDropIndicatorShown(True)
        self.table.dragEnterEvent = self._dragEnterEvent
        self.table.dragMoveEvent = self._dragMoveEvent
        self.table.dropEvent = self._dropEvent

    def _dragEnterEvent( self, event ):
        data = event.mimeData()
        urls = data.urls()
        if ( urls and urls[0].scheme() == 'file' ):
            filepath = str(urls[0].path())[1:]
            filename, file_extension = os.path.splitext(filepath)
            if file_extension == ".csv" or file_extension == ".CSV":
                event.acceptProposedAction()

    def _dragMoveEvent( self, event ):
        data = event.mimeData()
        urls = data.urls()
        if ( urls and urls[0].scheme() == 'file' ):
            event.acceptProposedAction()

    def _dropEvent( self, event ):
        data = event.mimeData()
        urls = data.urls()
        if ( urls and urls[0].scheme() == 'file' ):
            # for some reason, this doubles up the intro slash
            filepath = str(urls[0].path())[1:]
            print(filepath)
            if self.handler != None:
                self.handler(filepath)

            #self.lineEdit.setText(filepath)
    def registerHandle(self,handler):
        self.handler = handler


class lineEdit_dragFile_injector():
    def __init__(self, lineEdit, auto_inject = True):
        self.lineEdit = lineEdit
        if auto_inject:
            self.inject_dragFile()

    def inject_dragFile( self ):
        self.lineEdit.setDragEnabled(True)
        self.lineEdit.dragEnterEvent = self._dragEnterEvent
        self.lineEdit.dragMoveEvent = self._dragMoveEvent
        self.lineEdit.dropEvent = self._dropEvent

    def _dragEnterEvent( self, event ):
        data = event.mimeData()
        urls = data.urls()
        if ( urls and urls[0].scheme() == 'file' ):
            event.acceptProposedAction()

    def _dragMoveEvent( self, event ):
        data = event.mimeData()
        urls = data.urls()
        if ( urls and urls[0].scheme() == 'file' ):
            event.acceptProposedAction()

    def _dropEvent( self, event ):
        data = event.mimeData()
        urls = data.urls()
        if ( urls and urls[0].scheme() == 'file' ):
            # for some reason, this doubles up the intro slash
            filepath = str(urls[0].path())[1:]
            self.lineEdit.setText(filepath)

class Dialog(QtWidgets.QDialog):
    def __init__(self, dics, parent):
        QtWidgets.QDialog.__init__(self, parent)
        self.layout = QtWidgets.QGridLayout()
        i = 0
        for key in list(dics.keys()):
            hbox = QtWidgets.QHBoxLayout()
            xL = QtWidgets.QLabel()
            xL.setText(key)
            hbox.addWidget(xL)
            xLE = QtWidgets.QLineEdit()
            hbox.addWidget(xLE)
            self.layout.addLayout(hbox, i, 0, 1, 1)
            i=i+1

        '''
        self.hbox = QtWidgets.QHBoxLayout()
        self.okPB = QtWidgets.QPushButton()
        self.okPB.setText("OK")
        self.hbox.addWidget(self.okPB)
        self.cancelPB = QtWidgets.QPushButton()
        self.cancelPB.setText("Cancel")
        self.hbox.addWidget(self.cancelPB)
        self.layout.addLayout(self.hbox, 1, 0, 1, 1)
        '''
        self.setLayout(self.layout)

        #self.graphWidget = QtWidgets.PlotWidget()
        #self.layout.addWidget(self.graphWidget) # add the widget to the layout
        #self.setLayout(self.layout) # and set the layout on the dialog
        #self.graphWidget.plot(x, y)
formula = "x[i][0] * p1 + x[i][1] * p2 + x[i][2] * p3"

def myModel(x, p1=1.0, p2=1.0, p3=1.0, p4=1.0, p5=1.0, p6=1.0, p7=1.0, p8=1.0, p9=1.0, p10=1.0, p11=1.0, p12=1.0, p13=1.0, p14=1.0, p15=1.0,
            p16=1.0, p17=1.0, p18=1.0, p19=1.0, p20=1.0, p21=1.0, p22=1.0, p23=1.0, p24=1.0, p25=1.0, p26=1.0, p27=1.0, p28=1.0, p29=1.0, p30=1.0, p31=1.0,
            p32=1.0, p33=1.0, p34=1.0, p35=1.0, p36=1.0, p37=1.0, p38=1.0, p39=1.0, p40=1.0, p41=1.0, p42=1.0, p43=1.0, p44=1.0, p45=1.0, p46=1.0, p47=1.0, p48=1.0, p49=1.0, p50=1.0, p51=1.0):
    global formula
    y = np.zeros(len(x))
    for i in range(0, len(x)):
        y[i] = eval(formula)
        #y[i] = x[i][0] * p1 + x[i][1] * p2 + x[i][2] * p3
    return y

class LearnDialog(QtWidgets.QDialog):
    def __init__(self, df, inputs, output, parent):
        QtWidgets.QDialog.__init__(self, parent)
        QtWidgets.QDialog.setWindowFlags(self,QtCore.Qt.Dialog)
        self.inputs = inputs
        self.output = output
        self.df = df
        self.layout = QtWidgets.QGridLayout()
        self.tabWidget = QtWidgets.QTabWidget(self)
        self.layout.addWidget(self.tabWidget,0,1)
        vbox = QtWidgets.QVBoxLayout()
        self.b1 = QtWidgets.QPushButton()
        self.b1.setText("TEST AND TRAIN")
        self.b1.setObjectName("testAndTrainPB")
        self.b1.clicked.connect(self.on_testAndTrainPB_clicked)
        vbox.addWidget(self.b1)

        self.formulaLE = QtWidgets.QLineEdit()
        self.formulaLE.setText("R * p1 + G * p2 + B * p3")
        vbox.addWidget(self.formulaLE)

        self.b2 = QtWidgets.QPushButton()
        self.b2.setText("Start Learning")
        self.b2.setObjectName("startLearningPB")
        self.b2.clicked.connect(self.on_startLearningPB_clicked)
        vbox.addWidget(self.b2)

        verticalSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        vbox.addItem(verticalSpacer)
        self.layout.addLayout(vbox,0, 0)

        '''
        self.hbox = QtWidgets.QHBoxLayout()
        self.okPB = QtWidgets.QPushButton()
        self.okPB.setText("OK")
        self.hbox.addWidget(self.okPB)
        self.cancelPB = QtWidgets.QPushButton()
        self.cancelPB.setText("Cancel")
        self.hbox.addWidget(self.cancelPB)
        self.layout.addLayout(self.hbox, 1, 0, 1, 1)
        '''
        self.setLayout(self.layout)

        #self.graphWidget = QtWidgets.PlotWidget()
        #self.layout.addWidget(self.graphWidget) # add the widget to the layout
        #self.setLayout(self.layout) # and set the layout on the dialog
        #self.graphWidget.plot(x, y)

    def on_startLearningPB_clicked(self):
        global formula
        print("Learning started")
        print(formula)
        formula = self.formulaLE.text()
        l = re.split("([-()+*/])", formula)
        for i in range(0, len(l)):
            l[i] = l[i].strip()

        for i in range(0,len(self.inputs)):
            if self.inputs[i] in l:
                print(self.inputs[i],"x[i][",i,"]")
                formula = formula.replace(self.inputs[i],"x[i]["+str(i)+"]")
        print("Final Formula:",formula)
        X = np.hstack((np.vstack(self.df[head]) for head in self.inputs))
        Y = self.df[self.output]
        # print(Y)
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.13, random_state=42)
        gmodel = Model(myModel)
        result = gmodel.fit(y_train, x=X_train, verbose=True)
        print(result.params)
        print(result.fit_report())
        #print(result.eval_uncertainty())
        w = QtWidgets.QWidget(self.tabWidget)
        self.tabWidget.addTab(w,"Learning Results")
        self.tabWidget.setTabsClosable(True)
        layout1 = QtWidgets.QVBoxLayout(w)
        label = QtWidgets.QTextEdit()
        label.setText(result.fit_report())
        layout1.addWidget(label)


    @QtCore.pyqtSlot()
    def on_testAndTrainPB_clicked(self):
        print("Test and train")
        self.tabWidget.removeTab(0)
        self.tabWidget.removeTab(0)

        w1 = QtWidgets.QWidget(self.tabWidget)
        self.tabWidget.addTab(w1,"Train")
        self.tabWidget.setTabsClosable(True)
        w2 = QtWidgets.QWidget(self.tabWidget)
        self.tabWidget.addTab(w2,"Test")
        self.tabWidget.setTabsClosable(True)

        #print(self.df.head())
        #X = np.hstack((np.vstack(self.df['R']), np.vstack(self.df['G']), np.vstack(self.df['B'])))
        X = np.hstack((np.vstack(self.df[head]) for head in self.inputs))
        Y = self.df[self.output]
        #print(Y)
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.13, random_state=42)
        print(y_train)
        headers = self.inputs
        headers.append(self.output)
        self.addTableOnTab(self.tabWidget.widget(0), X_train, y_train,headers)
        self.addTableOnTab(self.tabWidget.widget(1),X_test,y_test,headers)


    def addTableOnTab(self,tab, x, y, headers):
        layout1 = QtWidgets.QVBoxLayout(tab)
        table = QtWidgets.QTableWidget()
        layout1.addWidget(table)
        table.setRowCount(0)
        table.setColumnCount(0)
        y_temp = np.array(y)
        table.insertRow(table.rowCount())
        table.setColumnCount(len(headers))
        for j in range(0, len(headers)):
            table.setItem(table.rowCount() - 1, j, QtWidgets.QTableWidgetItem(str(headers[j])))
        for i in range(0,len(x)):
            table.insertRow(table.rowCount())
            table.setColumnCount(len(x[i]) + 1)
            for j in range(0, len(x[i])):
                table.setItem(table.rowCount() - 1, j, QtWidgets.QTableWidgetItem(str(x[i][j])))
            #print(i, y_train[i])
            table.setItem(table.rowCount() - 1, len(x[i]), QtWidgets.QTableWidgetItem(str(y_temp[i])))
class MergeFileDialog(QtWidgets.QDialog):
    def __init__(self, fileList, parent):
        QtWidgets.QDialog.__init__(self, parent)
        QtWidgets.QDialog.setWindowFlags(self,QtCore.Qt.Window)
        self.dir = QDir.currentPath()
        self.fileList = fileList
        self.addControls()
        self.listFiles()

    def listFiles(self):
        for name in self.fileList:
            checkBox = QCheckBox(name)
            checkBox.setChecked(True)
            item = QListWidgetItem()
            self.listWidget.addItem(item)
            #box.stateChanged.connect(self.filterCheckBoxChangeState)
            self.listWidget.setItemWidget(item, checkBox)

    def handleMergeFile(self):
        print("handleSearchFile")

    def handleCancel(self):
        QtWidgets.QDialog.reject()

    def addControls(self):
        vBoxLayout = QVBoxLayout()
        hbox = QHBoxLayout()
        lb = QLabel("Select the files to be merged")
        hbox.addWidget(lb)
        vBoxLayout.addLayout(hbox)

        self.listWidget = QListWidget()
        vBoxLayout.addWidget(self.listWidget)

        gb = QtWidgets.QButtonGroup(self)
        ckb = QCheckBox("Merge Common Columns")
        vBoxLayout.addWidget(ckb)
        gb.addButton(ckb)
        ckb = QCheckBox("Merge All Columns")
        gb.addButton(ckb)
        vBoxLayout.addWidget(ckb)

        hbox = QHBoxLayout()
        pb = QPushButton("Merge")
        pb.clicked.connect(self.handleMergeFile)
        hbox.addWidget(pb)
        pb = QPushButton("Cancel")
        pb.clicked.connect(self.handleCancel)
        vBoxLayout.addLayout(hbox)

        self.setLayout(vBoxLayout)

class SearchFileDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent)
        QtWidgets.QDialog.setWindowFlags(self,QtCore.Qt.Dialog)
        self.dir = QDir.currentPath()
        self.addControls()

    def handleSearchFileOpen(self):
        print("handleSearchFileOpen")
        self.dir = QtWidgets.QFileDialog.getExistingDirectory(self,"Open Directory", QDir.currentPath(),
                                                QtWidgets.QFileDialog.ShowDirsOnly
                                                             | QtWidgets.QFileDialog.DontResolveSymlinks)
        self.folderLE.setText(self.dir)
        f = []
        for (dirpath, dirnames, filenames) in os.walk(self.dir):
            f.extend(filenames)
            break

        for name in filenames:
            base, ext = os.path.splitext(name)
            if ext == ".csv":
                checkBox = QCheckBox(name)
                checkBox.setChecked(True)
                item = QListWidgetItem()
                self.listWidget.addItem(item)
                #box.stateChanged.connect(self.filterCheckBoxChangeState)
                self.listWidget.setItemWidget(item, checkBox)

    def handleSearchFile(self):
        print("handleSearchFile")

    def addControls(self):
        vBoxLayout = QVBoxLayout()
        hbox = QHBoxLayout()
        lb = QLabel("Open Folder:")
        self.folderLE = QLineEdit()
        self.folderLE.setText(self.dir)
        pb = QPushButton("Browse")
        pb.clicked.connect(self.handleSearchFileOpen)
        hbox.addWidget(lb)
        hbox.addWidget(self.folderLE)
        hbox.addWidget(pb)
        vBoxLayout.addLayout(hbox)

        hbox = QHBoxLayout()
        lb = QLabel("Keywords:")
        le = QLineEdit()
        hbox.addWidget(lb)
        hbox.addWidget(le)
        vBoxLayout.addLayout(hbox)

        hbox = QHBoxLayout()
        button = QPushButton("Search File")
        button.clicked.connect(self.handleSearchFile)

        hbox.addWidget(button)
        vBoxLayout.addLayout(hbox)

        self.listWidget = QListWidget()
        vBoxLayout.addWidget(self.listWidget)

        hbox = QHBoxLayout()
        searchFileOkPB = QPushButton("Ok")
        searchFileCancelPB = QPushButton("Cancel")
        hbox.addWidget(searchFileOkPB)
        hbox.addWidget(searchFileCancelPB)
        vBoxLayout.addLayout(hbox)
        self.setLayout(vBoxLayout)

class MainWindow(widgetForm,baseClass):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        reader = FileReader()
        reader.openFile("als_data_variation.csv")
        self.viewlist = {}
        self.filename = ""
        lt = QtWidgets.QHBoxLayout(self.widget)
        lt.setContentsMargins(0,0,0,0)
        self.openFilesTabWidget = QtWidgets.QTabWidget(self.widget)
        self.openFilesTabWidget.setTabsClosable(False)
        lt.addWidget(self.openFilesTabWidget)
        self.openFilesTabWidget.tabCloseRequested.connect(self.handleTabClose)
        self.openFilesTabWidget.currentChanged.connect(self.on_tabchange)
        self.plotGB.setHidden(True)
        #Make lineEdit drag&drop feature
        self.dragnDrop = lineEdit_dragFile_injector(self.addressLE)

        self.tabIndexFileNameList = []
        self.dflist=[]
        self.filterListWidgetHiddenState = True
        self.filterListWidget.setHidden(self.filterListWidgetHiddenState)
        button_group = QtWidgets.QButtonGroup(self)
        button_group.addButton(self.inputCKB)
        button_group.addButton(self.outputCKB)

        self.filterListWidget.itemClicked.connect(self.filterListWidgetClicked)
        self.splitter.splitterMoved.connect(self.splitterResize)
        '''
 
        #self.plotPB.clicked.connect(self.on_plotPB_clicked)
        '''
        self.plotWindow = PlotWindow()

    def splitterResize(self, pos, index):
        print("Splitter:",pos,"x",index)

    def contextMenuEvent(self, event):
        print("Context Menu")

    def handleTabClose(self, index):
        print("Handle tab close",index)
        self.openFilesTabWidget.removeTab(index)
        self.tabIndexFileNameList.pop(index)

    @QtCore.pyqtSlot()
    def on_searchFilePB_clicked(self):
        dialog = SearchFileDialog(self)
        dialog.exec()

    @QtCore.pyqtSlot()
    def on_filterPB_clicked(self):
        print("filter PB clicked")
        self.selectAllCheckBoxState = True
        self.filterListWidget.setHidden(False)
        filename = self.tabIndexFileNameList[self.openFilesTabWidget.currentIndex()]
        if filename == "":
            msg = QMessageBox()
            msg.setText("please select a file")
            msg.setWindowTitle("hint")
            msg.exec_()
            return

        if self.dflist == []:
            print(self.tabIndexFileNameList[self.openFilesTabWidget.currentIndex()])
            df = pd.read_csv(self.tabIndexFileNameList[self.openFilesTabWidget.currentIndex()])
            df = df.dropna()
            self.dflist = [df.columns.values.tolist()] + df.values.tolist()
        self.filterListWidget.clear()
        if not (self.openFilesTabWidget.currentIndex() in self.viewlist):
            self.viewlist[self.openFilesTabWidget.currentIndex()] = self.dflist
            print(self.viewlist[self.openFilesTabWidget.currentIndex()])

        selected = self.table.selectedItems()
        if selected:
            print("currentTabIndex" + str(self.openFilesTabWidget.currentIndex()))
            print("selected row " + str(selected[0].row()))
            for col in self.viewlist[self.openFilesTabWidget.currentIndex()][selected[0].row()]:
                self.filterListWidget.addItem(str(col))

            df = pd.DataFrame(self.dflist[1:]).T
            output1 = [[element for element in row] for row in df.values]
            # if not np.isnan(element)
            print("ok")
            df = pd.DataFrame(self.viewlist[self.openFilesTabWidget.currentIndex()][1:]).T
            print("ok")
            output2 = [[element for element in row] for row in df.values]
            print("ok")
            for i in range(len(output1)):
                if not set(output2[i]) == set(output1[i]):
                    self.filterListWidget.item(i).setBackground(QColor('blue'))
                    self.filterListWidget.item(i).setForeground(QColor('white'))
        else:
            msg = QMessageBox()
            msg.setText("please select a row")
            msg.setWindowTitle("hint")
            msg.exec_()
        print("self.table.objectName is " + str(self.table.objectName()))

    def showError(self,error):
        msg = QMessageBox()
        msg.setText(error)
        msg.setWindowTitle("Error")
        msg.exec_()

    @QtCore.pyqtSlot()
    def on_runPB_clicked(self):
        print("Test and Train data")
        df = pd.read_csv(self.filename)
        #print(df.head())
        #X = np.hstack((np.vstack(df['R']), np.vstack(df['G']), np.vstack(df['B'])))
        #Y = df['LUX']
        #print(Y)
        #X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.13, random_state=42)
        #x = [15,10,3,4,5,6,7,8,9]
        #print(y_test)
        inputs = self.inputsLE.text().split(",")
        output = self.outputLE.text()
        d = LearnDialog(df,inputs, output, self)
        d.setWindowFlags(QtCore.Qt.Window)
        d.exec()
        #df = pd.read_csv(self.filename)
        #for i in range(0,len(x)):
        #    print("Result:",eval("x[i]*np.log(10.0) + 1.5"))

    @QtCore.pyqtSlot()
    def on_loadFilePB_clicked(self):
        filename = self.addressLE.text()
        if filename =="":
            filename,option = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file',
                                                                    QDir.currentPath(), "Image files (*.csv *.gif)")
            self.addressLE.setText(filename)
        filename = self.getFullPath(filename)
        if(self.openFilesTabWidget.count() == 0):
            self.on_addTabPB_clicked()
        else:
            print("Tab Count:", self.openFilesTabWidget.count(), " Current Tab:",
                  self.openFilesTabWidget.currentIndex())
            tabIndex = self.getFileIndex(filename)
            if tabIndex == self.openFilesTabWidget.currentIndex():
                return
            elif tabIndex >= 0:
                self.openFilesTabWidget.setCurrentIndex(tabIndex)
            elif tabIndex < 0:
                self.tabIndexFileNameList[self.openFilesTabWidget.currentIndex()] = filename
                self.openFilesTabWidget.setTabText(self.openFilesTabWidget.currentIndex(),os.path.basename(filename))
            self.addTableOnTab(self.openFilesTabWidget.widget(self.openFilesTabWidget.currentIndex()), filename)

    @QtCore.pyqtSlot()
    def on_addTabPB_clicked(self):
        filename = self.addressLE.text()
        if filename == "":
            w1 = QtWidgets.QWidget(self.openFilesTabWidget)
            tabNameList = []
            for i in range(0,self.openFilesTabWidget.count()):
                tabNameList.append(self.openFilesTabWidget.tabText(i))
            tabName = "TXC"
            for i in range(1,10000):
                if tabName not in tabNameList:
                    break
                tabName = "TXC_" + str(i)

            self.openFilesTabWidget.addTab(w1, tabName)
            self.openFilesTabWidget.setTabsClosable(True)
            self.tabIndexFileNameList.append("")
            self.openFilesTabWidget.setCurrentIndex(self.openFilesTabWidget.count() - 1)
            self.addTableOnTab(self.openFilesTabWidget.widget(self.openFilesTabWidget.count() - 1), '')
            return

        filename = self.getFullPath(filename)
        tabIndex = self.getFileIndex(filename)
        if tabIndex >= 0:
            print("File already open in tab:", tabIndex)
            self.openFilesTabWidget.setCurrentIndex(tabIndex)
            return

        self.tabIndexFileNameList.append(filename)
        w1 = QtWidgets.QWidget(self.openFilesTabWidget)
        self.openFilesTabWidget.addTab(w1,os.path.basename(filename))
        self.openFilesTabWidget.setTabsClosable(True)
        self.openFilesTabWidget.setCurrentIndex(self.openFilesTabWidget.count()-1)
        '''
        self.filename = name.split(".")[0] + "_temp." + name.split(".")[1]
        shutil.copy2(name, self.filename)
        columns = self.findMaxColumns()
        headers = ""
        for i in range(0, columns):
            if i == 0:
                headers = "0"
            else:
                headers = headers + "," + str(i)
        with open(name, 'r') as original:
            data = original.read()
        with open(self.filename, 'w') as modified:
            modified.write(headers + "\n" + data)
        '''
        self.addTableOnTab(self.openFilesTabWidget.widget(self.openFilesTabWidget.count()-1),filename)
        #lineEdit = QtWidgets.QLineEdit()
        #lineEdit.setText(name)
        #layout.addWidget(lineEdit)

    def on_tabchange(self,index):
        self.filterListWidget.setHidden(True)
        self.dflist = []
        print("Tab changed to :",index)
        if len(self.tabIndexFileNameList) == 0:

            return
        if index < 0:
            self.addressLE.setText("")
        else:
            self.addressLE.setText(self.tabIndexFileNameList[index])
            # add by Max
            try:
                self.table = self.openFilesTabWidget.findChild(QtWidgets.QWidget, str(index) + "_table")
                print(self.table.objectName())
            except:
                pass
        self.filename = self.addressLE.text()

    def getFullPath(self, filename):
        try:
            if not os.path.isabs(filename):
                filename = QtCore.QDir.currentPath()+"/"+filename
                print(filename)
        except:
            print("Exception in filename:", filename)
        if not os.path.exists(filename):
            self.showError(filename + " does not exist!!!")
            raise NameError('InvalidFile')
        return filename

    def getFileIndex(self,filename):
        if filename == '':
            return -1
        filename = self.getFullPath(filename)
        index = -1
        if filename in self.tabIndexFileNameList:
            for i in range(0, len(self.tabIndexFileNameList)):
                if filename == self.tabIndexFileNameList[i]:
                    index = i
            if (os.path.samefile(filename, self.tabIndexFileNameList[i])):
                print("File already open in tab:", index)
                self.openFilesTabWidget.setCurrentIndex(index)
            else:
                index = -1
        return index

    def groupBy(self,select_list,sortby=0):
        df = pd.read_csv(self.filename)
        df = df.sort_values(by=df.columns[select_list[sortby]])
        dfgb = df.groupby(df.columns[select_list[0]])

        return df,dfgb

    @QtCore.pyqtSlot()
    def on_boxGroupbyPlotPB_clicked(self):
        print("on_pppb_clicked")
        selected = self.table.selectedItems()
        select_list = []
        for sel in selected:
            if not (sel.column() in select_list):
                select_list.append(sel.column())
        print(select_list)
        if len(select_list) >= 2:
            df = pd.read_csv(self.filename)

            df, dfgb = self.groupBy(select_list,sortby=1)
            dfgb_dict=dfgb.indices

            print(df.columns[select_list[1]])

            # dfgb.boxplot(subplots=False,column=df.columns[select_list[1]])
            self.plotWindow.runPlotFunction(dfgb.boxplot, subplots=False,column=df.columns[select_list[1]],setYourLabel=df.columns[select_list[1]])


            self.plotWindow.show()

        else:
            print("no selected")

    @QtCore.pyqtSlot()
    def on_groupbyPB_clicked(self):
        print("groupByPB clicked")
        #df = pd.DataFrame(self.viewlist[self.openFilesTabWidget.currentIndex()])

        selected = self.table.selectedItems()
        select_list = []
        for sel in selected:
            if not(sel.column() in select_list):
                select_list.append(sel.column())
        print(select_list)
        if len(select_list) >= 3:
            df=pd.read_csv(self.filename)
            self.pg = pg.PlotWidget()
            self.pg.setWindowTitle("group by "+df.columns[select_list[0]])
            self.pg.setLabel(axis='bottom', text=df.columns[select_list[1]])
            self.pg.setLabel(axis='left', text=df.columns[select_list[2]])
            self.pg.addLegend()
            df, dfgb = self.groupBy(select_list)
            dfgb_dict=dfgb.indices
            for key,group in dfgb_dict.items():
                print(key)
                X=df[df.columns[select_list[1]]][group].values
                Y=df[df.columns[select_list[2]]][group].values
                idx = list(dfgb_dict.keys()).index(key)
                #plt.scatter(X,Y,label=str(key))
                self.plotWindow.runPlotFunction(plt.scatter,x=X,y=Y,label=str(key))

            #plt.legend()
            self.plotWindow.runPlotFunction(plt.legend)

            self.plotWindow.show()

        else:
            print("no selected")
    @QtCore.pyqtSlot()
    def on_xyPlotPB_clicked(self):
        print("xyPlotPB clicked")
        df = pd.read_csv(self.filename)
        df = df.dropna()
        #df.plot('PS', 'PRX1', kind='scatter')
        #df.plot('PS1', 'PRX1', kind='scatter')
        selected = self.table.selectedItems()
        selectedCols = []
        selectedRows = []
        if selected:
            for item in selected:
                #print(item.column(),"X",item.row())
                if df.columns[item.column()] not in selectedCols:
                    selectedCols.append(df.columns[item.column()])
                if item.row() not in selectedRows:
                    selectedRows.append(item.row())
            df = df[selectedCols]
            df = pd.DataFrame(df, index=selectedRows)
        else:
            for col in df.columns:
                if utils_recognize_type(df, col) != 'cat':
                    selectedCols.append(col)
            df = df[selectedCols]

        colors = ['#FF0000','#00FF00','#0000FF','#F00000','#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        mStyles = ["*", "+", "x", ".", ",", "o", "v", "^", "<", ">", "1", "2", "3", "4", "8", "s", "p", "P", "h", "H",
                   "X", "D", "d", "|", "_", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
                   ]
        if len(selectedCols) >= 2:
            for i in range(1, len(selectedCols)):
                #plt.scatter(df[selectedCols[0]], df[selectedCols[i]], c=colors[i], marker=mStyles[i], label=selectedCols[i])
                self.plotWindow.runPlotFunction(plt.scatter,df[selectedCols[0]], df[selectedCols[i]], c=colors[i], marker=mStyles[i], label=selectedCols[i])
        plt.legend(loc='upper left')

        #plt.show()
        self.plotWindow.show()
    @QtCore.pyqtSlot()
    def on_boxPlotPB_clicked(self):
        print("boxPlotPB clicked")
        df = pd.read_csv(self.filename)
        df = df.dropna()

        #print(df.head())
        # fig, ax = plt.subplots(nrows=1, ncols=1, sharex=False, sharey=False)
        #print(df.index)
        selected = self.table.selectedItems()
        selectedCols = []
        selectedRows = []
        if selected:
            for item in selected:
                print(item.column(),"X",item.row())
                if df.columns[item.column()] not in selectedCols:
                    selectedCols.append(df.columns[item.column()])
                if item.row() not in selectedRows:
                    selectedRows.append(item.row())
            df = df[selectedCols]
            df = pd.DataFrame(df, index=selectedRows)
        else:
            for col in df.columns:
                if utils_recognize_type(df, col) != 'cat':
                    selectedCols.append(col)
            df = df[selectedCols]

        df.boxplot(column=selectedCols)
        plt.show()
        self.table.clearSelection()

    @QtCore.pyqtSlot()
    def on_histogramPlotPB_clicked(self):
        #disc = {'x':['R1:R200'],'y':['C1:C200'],'groupby':''}
        #dialog = Dialog(disc, self)
        #dialog.show()
        df = pd.read_csv(self.filename)
        df = df.dropna()
        selected = self.table.selectedItems()
        selectedCols = []
        selectedRows = []
        if selected:
            for item in selected:
                print(item.column(),"X",item.row())
                if df.columns[item.column()] not in selectedCols:
                    selectedCols.append(df.columns[item.column()])
                if item.row() not in selectedRows:
                    selectedRows.append(item.row())
            df = df[selectedCols]
            df = pd.DataFrame(df, index=selectedRows)
        else:
            for col in df.columns:
                if utils_recognize_type(df, col) != 'cat':
                    selectedCols.append(col)
                    break
            df = df[selectedCols]
        # df.plot(y='PRX1')

        print(df)
        #df[selectedCols[0]].plot(kind='hist',bins=100,rwidth=.9)
        sns.distplot(df[selectedCols[0]], hist=True, kde=True, rug=False, bins=int(180/5),
                     color='darkblue',hist_kws={'edgecolor':'black'},
                     kde_kws={'linewidth': 3},
                     rug_kws={'color': 'black'})
        plt.show()
        self.table.clearSelection()

    @QtCore.pyqtSlot()
    def on_plotPB_clicked(self):
        print("Plot PB clicked")
        self.filename = self.addressLE.text()
        df = pd.read_csv(self.filename)
        df = df.dropna()
        '''
        a = df.iloc[0:1, :].to_numpy()
        dict = {}
        for i in df.columns:
            print(i)
            dict[i] = a[0][int(i)]
        df.rename(columns=dict, inplace=True)
        df = df.drop(columns="Time", axis=1)
        df = df.drop(labels=22, axis=0)
        df = pd.to_numeric(df,errors='coerce')
        '''
        #print(df.head())
        # fig, ax = plt.subplots(nrows=1, ncols=1, sharex=False, sharey=False)
        #print(df.index)
        #print(df.columns)
        selected = self.table.selectedItems()
        selectedCols = []
        selectedRows = []
        if selected:
            for item in selected:
                print(item.column(),"X",item.row())
                if df.columns[item.column()] not in selectedCols:
                    selectedCols.append(df.columns[item.column()])
                if item.row() not in selectedRows:
                    selectedRows.append(item.row())
            df = df[selectedCols]
            df = pd.DataFrame(df, index=selectedRows)
        else:
            for col in df.columns:
                if utils_recognize_type(df, col) != 'cat':
                    selectedCols.append(col)
            df = df[selectedCols]
        # df.plot(y='PRX1')

        print(df)
        df[selectedCols].plot()

        name, ext = os.path.splitext(self.filename)
        if not os.path.isdir(name):
            os.mkdir(name)
        plt.savefig(name + "\\fig1.png")
        self.addPicture(name + "\\fig1.png")
        self.table.clearSelection()
        plt.show()


    def findMaxColumns(self):
        maxColumns = 0
        with open(self.filename) as fp:
            for line in fp:
                line = line.strip()
                tempList = line.split(",")
                while '' in tempList:
                    tempList.remove('')

                if(maxColumns < len(tempList)):
                    maxColumns = len(tempList)
        return maxColumns

    def cellSelectionChanged(self):
        print("Cell selection changed")
        # add by Max
        selected = self.table.selectedItems()
        if not selected:
            return
        selectedColumns=[]
        if(self.inputCKB.isChecked()):
            selected = self.table.selectedItems()
            if selected:
                for item in selected:
                    if item.column() not in selectedColumns:
                        selectedColumns.append(item.column())
                        print(item.column(), "X", item.row())

                headers = []
                selectedHeaders = []
                with open(self.filename) as fp:
                    for line in fp:
                        line = line.strip()
                        headers = line.split(",")
                        break
                    for i in range(0,len(headers)):
                        if i in selectedColumns:
                            selectedHeaders.append(headers[i])

                    self.inputsLE.setText("")
                    for i in range(0, len(selectedHeaders)):
                        if i==0:
                            self.inputsLE.setText(selectedHeaders[i])
                        else:
                            self.inputsLE.setText(self.inputsLE.text() + "," + selectedHeaders[i])
        if(self.outputCKB.isChecked()):
            selected = self.table.selectedItems()
            if selected:
                for item in selected:
                    if item.column() not in selectedColumns:
                        selectedColumns.append(item.column())
                        print(item.column(), "X", item.row())

                headers = []
                selectedHeaders = []
                with open(self.filename) as fp:
                    for line in fp:
                        line = line.strip()
                        headers = line.split(",")
                        break
                    for i in range(0, len(headers)):
                        if i in selectedColumns:
                            selectedHeaders.append(headers[i])

                    self.outputLE.setText("")
                    for i in range(0, len(selectedHeaders)):
                        if i == 0:
                            self.outputLE.setText(selectedHeaders[i])
                        else:
                            self.outputLE.setText(self.outputLE.text() + "," + selectedHeaders[i])

        '''
        selected = self.table.selectedItems()
        if selected:
            for item in selected:
                print(item.column(),"X",item.row())
    
        dtf = pd.read_csv(name,skiprows=22)
        print(dtf.head())
        x = "PRX1"
        fig, ax = plt.subplots(nrows=1, ncols=1, sharex=False, sharey=False)
        #fig.suptitle(x, fontsize=20)
        dtf = dtf.drop(['PRX'], axis=1)
        tmp_dtf = pd.DataFrame(dtf[x])
        dtf.boxplot()
        plt.show()
        '''
    def handleDragNDrop(self,filepath):
        print("FilePath:",filepath)
        self.addressLE.setText(filepath)
        self.on_loadFilePB_clicked()

    def addTableOnTab(self,tab,filename):
        lineCount = 0
        wordCount = 0
        t = tab.findChild(QtWidgets.QWidget,str(self.openFilesTabWidget.currentIndex())+"_table")
        #if t != None:
        #    t.setParent(None)
        #vbox.deleteLater()
        vbox = tab.findChild(QtWidgets.QVBoxLayout, str(self.openFilesTabWidget.currentIndex()) + "_vbox")
        #if vbox != None:
        #    vbox.setParent(None)
        #tab.findChild(QtWidgets.QWidget,str(self.openFilesTabWidget.currentIndex())+"_table").setParent(None)
        #tab.findChild(QtWidgets.QWidget, str(self.openFilesTabWidget.currentIndex()) + "_table").deleteLater()
        if vbox == None and t == None:
            layout = QtWidgets.QVBoxLayout(tab)
            layout.setObjectName(str(self.openFilesTabWidget.currentIndex())+"_vbox")
            self.table = QtWidgets.QTableWidget()
            dnd = table_dragFile_injector(self.table)
            dnd.registerHandle(self.handleDragNDrop)
            self.table.setObjectName(str(self.openFilesTabWidget.currentIndex())+"_table")
            #self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            layout.addWidget(self.table)
        else:
            self.table = t
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
        if filename != '':
            with open(filename) as fp:
                for line in fp:
                    line = line.strip()
                    self.table.insertRow(self.table.rowCount())
                    tempList = line.split(",")
                    self.table.setColumnCount(len(tempList))
                    for i in range(0, len(tempList)):
                        self.table.setItem(self.table.rowCount() - 1, i, QtWidgets.QTableWidgetItem(str(tempList[i])))

        self.table.itemSelectionChanged.connect(self.cellSelectionChanged)

    def addPicture(self,path):
        vbox = QtWidgets.QVBoxLayout()
        cl = QtWidgets.QLabel()
        cl.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addWidget(cl,alignment=QtCore.Qt.AlignCenter)
        im = QtGui.QImage(path);
        #QPixmap::fromImage(*im).scaled(w,h, Qt::KeepAspectRatio)
        cl.setPixmap(QtGui.QPixmap.fromImage(im).scaled(350,350, QtCore.Qt.KeepAspectRatio))
        vbox.setContentsMargins(0, 0, 0, 10)
        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(QtCore.QSize(100, 200))
        self.listWidget.setViewMode(QtWidgets.QListView.ListMode)
        self.listWidget.addItem(item)
        self.listWidget.setItemWidget(item, cl)
        self.listWidget.setSizeAdjustPolicy(QListWidget.AdjustToContents)
        self.plotGB.setHidden(False)

    @QtCore.pyqtSlot()
    def on_fullScreenPB_clicked(self):
        date = datetime.now()
        filename = date.strftime('%Y-%m-%d_%H-%M-%S.jpg')
        #app = QtWidgets.QApplication(sys.argv)
        #widget.grab()
        QtGui.QScreen.grabWindow(app.primaryScreen(),QtWidgets.QApplication.desktop().winId()).save(filename, 'png')
        print("Full")

    @QtCore.pyqtSlot()
    def on_windowPB_clicked(self):
        date = datetime.now()
        filename = date.strftime('%Y-%m-%d_%H-%M-%S.jpg')
        #app = QtWidgets.QApplication(sys.argv)
        #widget.grab()
        #QtGui.QScreen.grabWindow(app.primaryScreen(),QtWidgets.QWidget().winId()).save(filename, 'png')
        QtGui.QScreen.grabWindow(app.primaryScreen(),  window.winId()).save(filename, 'png')
        print("Window")

    #new

    def select(self):
        self.pathtt.setText(select_path())

    def search(self):
        if self.pathtt.text() is "":
            root = Tk()
            root.withdraw()
            messagebox.showerror("Error", "Please select a path")
            return

        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(["FIle","Sheet","Path", "Open"])
        filePathList = []
        count = 0
        self.file_list.clear()
        for root, dirs, files in os.walk(self.pathtt.text()):
            file = (root, files)
            filePathList.append(file)
        for f in filePathList:
            for file_name in f[1]:
                try:
                    if (file_name.__contains__(".xl") or file_name.__contains__(".xlsx") or file_name.__contains__(".csv")):
                        path = f[0] + "/" + file_name
                        xls = pd.ExcelFile(path)
                        sheets_list=[]
                        if(self.sheetsLE.text()==""):
                            sheets_list=xls.sheet_names
                        else:
                            sheets = self.sheetsLE.text().split(',')
                            if(self.isStringCBK.isChecked()):
                                for sheet in sheets:
                                    sheets_list.append(sheet)
                            else:
                                names=xls.sheet_names
                                for sheetIndex in sheets:
                                    sheets_list.append(names[int(sheetIndex)])
                        for sheet_name in sheets_list:
                            if open_excel(path,sheet_name,self.keytt.text()):
                                rowPosition = self.tableWidget.rowCount()
                                #print(rowPosition)
                                self.tableWidget.insertRow(rowPosition)
                                self.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(file_name))
                                self.tableWidget.setItem(rowPosition, 1, QTableWidgetItem(sheet_name))
                                self.tableWidget.setItem(rowPosition, 2, QTableWidgetItem(path))
                                btn = QtWidgets.QPushButton("Open")
                                btn.index=[rowPosition,2]
                                pair=[path,sheet_name]
                                self.file_list.append(pair)
                                #btn.clicked.connect(lambda: open_file(path))
                                #lambda *args, row=row, column=column: cellClick(row, column))
                                btn.clicked.connect(lambda*args, row=rowPosition, column=2: self.open_file(row, column))
                                self.tableWidget.setCellWidget(rowPosition, 3, btn)
                                count=count+1
                except:
                    root = Tk()
                    root.withdraw()
                    messagebox.showerror("Error", "Please close the file-"+file_name)
        root = Tk()
        root.withdraw()
        messagebox.showinfo("Finished", "Found:"+str(count)+" Sheets")


    def filterListWidgetClicked(self):
        idx = self.filterListWidget.currentRow()
        print(idx)
        df = pd.DataFrame(self.dflist[1:]).T
        output = [[element for element in row] for row in df.values]
        # swap col row from list
        setoutput = set(output[idx])
        # unique value
        self.filterCheckBoxlistWidget = QListWidget()
        for i in setoutput:
            print(i)
            box = QCheckBox(str(i))
            item = QListWidgetItem()
            self.filterCheckBoxlistWidget.addItem(item)
            box.stateChanged.connect(self.filterCheckBoxChangeState)
            self.filterCheckBoxlistWidget.setItemWidget(item, box)
        # self.filterCheckBoxlistWidget.show()
        self.filterCheckBoxQVBoxLayout = QVBoxLayout()

        sortPB = QPushButton("sort")
        sortPB.clicked.connect(self.filterSort)
        self.filterCheckBoxQVBoxLayout.addWidget(sortPB)

        self.selectAllCheckBox = QCheckBox("select all")
        self.selectAllCheckBox.stateChanged.connect(self.selectAllCheckBoxStateChange)
        self.filterCheckBoxQVBoxLayout.addWidget(self.selectAllCheckBox)

        self.filterCheckBoxQVBoxLayout.addWidget(self.filterCheckBoxlistWidget)

        confirmPB = QPushButton("confirm")
        confirmPB.clicked.connect(self.getFilterChoose)
        self.filterCheckBoxQVBoxLayout.addWidget(confirmPB)

        self.filterCheckBoxQWidget = QWidget()
        self.filterCheckBoxQWidget.setWindowTitle(self.filterListWidget.item(idx).text())
        self.filterCheckBoxQWidget.setLayout(self.filterCheckBoxQVBoxLayout)

        df = pd.DataFrame(self.viewlist[self.openFilesTabWidget.currentIndex()][1:]).T
        self.filterCheckBoxQWidget.show()
        output = [[element for element in row] for row in df.values]
        # print(output)

        count = self.filterCheckBoxlistWidget.count()
        cb_list = [self.filterCheckBoxlistWidget.itemWidget(self.filterCheckBoxlistWidget.item(i))
                   for i in range(count)]
        for cb in cb_list:  # type:QCheckBox

            if str(cb.text()) in str(output[self.filterListWidget.currentRow()]):
                cb.setChecked(True)

    def filterCheckBoxChangeState(self):
        self.selectAllCheckBoxState = False

        count = self.filterCheckBoxlistWidget.count()
        cb_list = [self.filterCheckBoxlistWidget.itemWidget(self.filterCheckBoxlistWidget.item(i))
                   for i in range(count)]
        if any(cb.isChecked() == False for cb in cb_list):

            self.selectAllCheckBox.setChecked(False)

        else:
            self.selectAllCheckBox.setChecked(True)

    def selectAllCheckBoxStateChange(self):

        count = self.filterCheckBoxlistWidget.count()
        cb_list = [self.filterCheckBoxlistWidget.itemWidget(self.filterCheckBoxlistWidget.item(i))
                   for i in range(count)]
        # print(cb_list)
        if self.selectAllCheckBox.isChecked() == True:
            self.filterListWidget.item(self.filterListWidget.currentRow()).setBackground(QColor('white'))
            for cb in cb_list:  # type:QCheckBox
                cb.setChecked(True)
        else:
            if self.selectAllCheckBoxState:
                for cb in cb_list:  # type:QCheckBox
                    cb.setChecked(False)

        self.selectAllCheckBoxState = True

    def filterSort(self):
        self.viewlist[self.openFilesTabWidget.currentIndex()] = [self.dflist[0]] + sorted(
            self.viewlist[self.openFilesTabWidget.currentIndex()][1:],
            key=lambda s: s[self.filterListWidget.currentRow()])
        layout = QtWidgets.QVBoxLayout(self.openFilesTabWidget.widget(0))
        table = self.table
        # table.blockSignals(True)
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(0)
        layout.addWidget(table)
        for row in self.viewlist[self.openFilesTabWidget.currentIndex()]:

            tempList = row
            table.insertRow(table.rowCount())
            table.setColumnCount(len(tempList))
            for i in range(0, len(tempList)):
                table.setItem(table.rowCount() - 1, i, QtWidgets.QTableWidgetItem(str(tempList[i])))

        # table.blockSignals(False)

    def getFilterChoose(self):
        count = self.filterCheckBoxlistWidget.count()
        cb_list = [self.filterCheckBoxlistWidget.itemWidget(self.filterCheckBoxlistWidget.item(i))
                   for i in range(count)]
        # print(cb_list)
        chooses = []
        for cb in cb_list:  # type:QCheckBox
            if cb.isChecked():
                chooses.append(cb.text())
        self.filterChooses = chooses
        print(self.filterChooses)
        idx = self.filterListWidget.currentRow()
        df = pd.DataFrame(self.viewlist[self.openFilesTabWidget.currentIndex()][1:]).T
        # print(df)
        output = [[element for element in row] for row in df.values]
        # swap col row from list
        indices = [0]
        for choose in self.filterChooses:
            indices += [i + 1 for i, x in enumerate(output[idx]) if str(x) == choose]
        print(indices)
        # get indices of chooses
        layout = QtWidgets.QVBoxLayout(self.openFilesTabWidget.widget(0))
        table = self.table
        # table.blockSignals(True)
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(0)
        layout.addWidget(table)

        for indice in indices:
            tempList = self.viewlist[self.openFilesTabWidget.currentIndex()][indice]
            table.insertRow(table.rowCount())
            table.setColumnCount(len(tempList))
            for i in range(0, len(tempList)):
                table.setItem(table.rowCount() - 1, i, QtWidgets.QTableWidgetItem(str(tempList[i])))

        # table.blockSignals(False)

        self.viewlist[self.openFilesTabWidget.currentIndex()] = [self.viewlist[self.openFilesTabWidget.currentIndex()][i] for i in indices]
        # print(self.viewlist[self.openFilesTabWidget.currentIndex()])
        df = pd.DataFrame(self.dflist[1:]).T
        print(df)
        output1 = [[element for element in row] for row in df.values]
        df = pd.DataFrame(self.viewlist[self.openFilesTabWidget.currentIndex()][1:]).T
        print(df)
        output2 = [[element for element in row] for row in df.values]
        for i in range(len(output1)):
            if not set(output2[i]) == set(output1[i]):
                self.filterListWidget.item(i).setBackground(QColor('blue'))
                self.filterListWidget.item(i).setForeground(QColor('white'))

    @QtCore.pyqtSlot()
    def on_mergeFilesPB_clicked(self):
        print("on_mergeFilesPB_clicked")
        if len(self.tabIndexFileNameList) == 0:
            self.showError("No files open!!")
            return
        dialog = MergeFileDialog(self.tabIndexFileNameList, self)
        dialog.exec()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.setWindowFlags(QtCore.Qt.Window)
    window.show()  # é¡¯ç¤ºè¦– ?
    sys.exit(app.exec_())

