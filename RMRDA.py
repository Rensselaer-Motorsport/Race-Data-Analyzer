"""
RMRDA:
Rensselaer Motorsport Race Data Analyzer

Author: Mitchell Mellone (mellom3@rpi.edu)
Created: 4/17/2015
Last Modified: 4/17/2015
Version: 0.5.0

Copyright (C) 2015 Rensselaer Motorsports

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

ENJOY!
"""

import os, sys
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
# from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.console
from pyqtgraph.dockarea import *
import numpy as np
from PyQt4.Qt import *
import xlwt
import database as db

#---------------------------
#-----Main Window Class-----
#---------------------------
class GUI_window(QtGui.QMainWindow):
    #----------------------------------
    #-----GENERAL WINDOW FUNCTIONS-----
    #----------------------------------
    '''
    GUI_window is the main window for the UI and is created at start up.
    '''
    def __init__(self):
        super(GUI_window, self).__init__()
        self.prompt = None #for selecting things
        self.data = db.DataBase() #stores the data to be plotted
        self.version = 0x050 #Should be equal to version in header comment (without periods)
        self.objectCounter = 0
        self.initUI()

        self.data.parse_file('test_buffer.txt') #parses data to be used this session

    '''
    Initializes the basic functions for the UI
    '''
    def initUI(self):
        #---------------------------------------------------
        #-----CREATE ACTIONS THAT PERFORM GENERAL TASKS-----
        #---------------------------------------------------
        #Exit action initialization
        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application.')
        exitAction.triggered.connect(QtGui.qApp.quit)

        #Create Plot action initialization
        createRMplot = QtGui.QAction(QtGui.QIcon('green+.png'), '&Add Graph', self)
        createRMplot.setShortcut('Ctrl+P')
        createRMplot.setStatusTip('Add a plot of data from a sensor.')
        createRMplot.triggered.connect(self.RMplotSelect)

        #Create Table action initialization
        createRMtable = QtGui.QAction(QtGui.QIcon('green+.png'), '&Add Table', self)
        createRMtable.setShortcut('Ctrl+T')
        createRMtable.setStatusTip('Add a table of data from a sensor.')
        createRMtable.triggered.connect(self.RMtableSelect)

        #SaveAs action initialization
        saveAction = QtGui.QAction('&SaveAs', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Saves the current window state.')
        saveAction.triggered.connect(self.saveAs)

        #Load action initialization
        openAction = QtGui.QAction('&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Opens a previous window state.')
        openAction.triggered.connect(self.load)

        #Export_to_Excel action initialization
        exportExlAction = QtGui.QAction('Export to Excel', self)
        exportExlAction.setShortcut('Ctrl+E')
        exportExlAction.setStatusTip('Exports all of the data to excel.')
        exportExlAction.triggered.connect(self.exportExcelFile)

        #--------------------------------------
        #-----INITIALIZE MAIN GUI ELEMENTS-----
        #--------------------------------------
        #Status bar initialization
        self.statusBar().showMessage('Ready')

        #Tool bar initialization
        self.toolbar = QToolBar(parent=self)
        self.addToolBar(self.toolbar)
        self.toolbar.setObjectName(str(self.objectCounter))
        self.objectCounter += 1
        self.toolbar.addAction(exitAction)
        self.toolbar.addAction(createRMplot)
        self.toolbar.addAction(createRMtable)

        #Menu bar initialization
        menubar = self.menuBar()
        self.file_menu = menubar.addMenu('&File')
        self.view_menu = menubar.addMenu('&View')
        self.help_menu = menubar.addMenu('&Help')

        #File Menu initialization
        self.file_menu.addAction(saveAction)
        self.file_menu.addAction(openAction)
        self.file_menu.addAction(exportExlAction)
        self.file_menu.addAction(createRMplot)
        self.file_menu.addAction(createRMtable)
        self.file_menu.addAction(exitAction)

        #Set main window properties
        self.setGeometry(300, 300, 750, 500)
        self.setWindowTitle('RM Race Data Analysis')
        self.setWindowIcon(QtGui.QIcon('rmlogo.png'))

        #Add a background image
        # self.background = QtGui.QLabel()
        # logoBackground = QtGui.QPixmap('rmlogo2.png')
        # self.background.setPixmap(logoBackground)
        # self.setCentralWidget(self.background)

        #Show the window
        self.show()

    #---------------------------
    #-----UTILITY FUNCTIONS-----
    #---------------------------
    #Called if main window is closed
    def closeEvent(self, event):
        if self.prompt != None:
            self.prompt.close()

    #only saves the state, not the actual stuff
    def saveAs(self):
        fileName = QtGui.QFileDialog.getSaveFileName(parent=self, caption='Save As', filter='RM files (*.rmrda)')
        f = open(str(fileName), 'wb')
        f.write(self.saveState())
        f.close

    #only loads a state, not any actual material
    def load(self):
        fileName = QtGui.QFileDialog.getOpenFileName(parent=self, caption='Open')

        byteArrayIn = None
        with open(fileName, 'rb') as fin:
            byteArrayIn = fin.read()
        self.restoreState(byteArrayIn)

    def exportExcelFile(self):
        self.prompt = ExcelExportSelectPopup(self.data.get_list_of_sensors())
        self.prompt.show()
        #generate the excel file 'book'
        book = xlwt.Workbook()
        sh = book.add_sheet('all data')
        sh.write(0, 0, label='Time') #write time label
        for r, t in enumerate(self.data.get_elapsed_times()):
            #write in the times in the left-most column
            sh.write(r+1, 0, label=t)
        for c, sens in enumerate(self.data.get_list_of_sensors()):
            #write in the sensor labels on the first row
            sh.write(0, c+1, label=str(sens))
            for r, v in enumerate(self.data.get_sensor_values(str(sens))):
                #write in the values under their respective sensor label
                sh.write(r+1, c+1, label=v)

        fileName = QtGui.QFileDialog.getSaveFileName(parent=self, caption='Save As', filter='Excel Files (*.xlsx)')
        print fileName
        if fileName[len(fileName)-5:] != '.xlsx':
            fileName += '.xlsx'
        book.save(fileName)

    #--------------------------
    #-----RMplot FUNCTIONS-----
    #--------------------------
    # Creates a SensorSelctPopup to prompt user for sensor
    def RMplotSelect(self):
        self.prompt = SensorSelectPopup(self.data.get_list_of_sensors())
        self.connect(self.prompt.getButton(), SIGNAL("clicked()"), self.RMplotHandleButtonPress)
        self.prompt.show()

    def RMplotHandleButtonPress(self):
        self.createRMplot(self.prompt.getState())
        self.prompt.close()
        self.prompt = None

    # Creates a RMplot and adds it to the GUI
    def createRMplot(self, sensorNames):
        newRMplot = RMplot(sensorNames)
        newRMplot.setObjectName(str(self.objectCounter))
        self.objectCounter += 1
        newRMplot.makePlot(self.data)
        self.addDockWidget(Qt.TopDockWidgetArea, newRMplot)

    #---------------------------
    #-----RMtable Functions-----
    #---------------------------
    # Creates a SensorSelctPopup to prompt user for sensor
    def RMtableSelect(self):
        self.prompt = SensorSelectPopup(self.data.get_list_of_sensors())
        self.connect(self.prompt.getButton(), SIGNAL("clicked()"), self.RMtableHandleButtonPress)
        self.prompt.show()

    def RMtableHandleButtonPress(self):
        self.createRMtable(self.prompt.getState())
        self.prompt.close()
        self.prompt = None

    # Creates an RMTable and adds it to the GUI
    def createRMtable(self, sensorName):
        newRMtable = RMtable(sensorName)
        newRMtable.setObjectName(str(self.objectCounter))
        self.objectCounter += 1
        newRMtable.makeTable(self.data)
        self.addDockWidget(Qt.TopDockWidgetArea, newRMtable)

#----------------------
#-----RMplot Class-----
#----------------------
class RMplot(QtGui.QDockWidget):
    '''
    RMplot is a custom plot widget that extends QDockWidget, which allows
    it to be moved around the MainWindow, dragged outside the main window,
    and tabbed, and uses a pyqtgraph plotWidget to actually do the
    graphing.
    Params:
    title = title for the plot
    '''
    def __init__(self, senNames):
        title = senNames[0]
        for name in senNames[1:]:
            title = title + ', ' + name
        title = title + ' Plot'
        self.names = senNames
        super(RMplot, self).__init__(title)
        self.layout = pg.GraphicsLayoutWidget()
        self.timeLabel = pg.LabelItem(justify='right')
        self.layout.addItem(self.timeLabel)
        self.plot = self.layout.addPlot(row=1, col=0)
        self.data = None
        self.colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w']
        self.labelCols = ['red', 'green', 'blue', 'cyan', 'magenta', 'yellow', 'khaki', 'white']
        self.hLines = []
        for l in range(0, len(senNames)):
            self.hLines.append(pg.InfiniteLine(angle=0, movable=False, pen=self.colors[l%(len(self.colors))]))
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.proxy = pg.SignalProxy(self.plot.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.setAllowedAreas(Qt.DockWidgetArea_Mask)

    '''
    Makes the pyqtgraph plot widget and adds it to this RMplot object
    Params:
    data = dataBase of sensor values and time
    sensorName = name of the sensor to plot
    '''
    def makePlot(self, data):
        # Get times and values
        self.data = data
        times = self.data.get_elapsed_times()

        #Find limits for the view range of the plot
        ymin = 0
        ymax = 0
        for name in self.names:
            ymin_temp = self.data.get_min_sensor_value(str(name))
            if ymin_temp < ymin:
                ymin = ymin_temp
            ymax_temp = self.data.get_max_sensor_value(str(name))
            if ymax_temp > ymax:
                ymax = ymax_temp
        #determine initial padding
        xpadding = times[len(times)-1] * 0.1
        ypadding = abs(ymax-ymin) * 0.1
        tmax = self.data.get_max_sensor_value('time') #find the maximum time

        for i, name in enumerate(self.names):
            values = self.data.get_sensor_values(str(name))
            self.plot.plot(times, values, pen=self.colors[i%len(self.colors)])

        self.plot.setLimits(xMin=0-xpadding, xMax=times[len(times)-1]+xpadding, yMin=ymin-ypadding, yMax=ymax+ypadding)
        self.plot.setRange(xRange=(0, tmax), yRange=(ymin, ymax), padding=0.0) #sets the initial range of the plot
        self.plot.showGrid(x=True, y=True, alpha=0.5)
        self.plot.setLabel('bottom', text='Time Elapsed', units="s")
        self.plot.setLabel('left', text='Sensor Value', units=" unit")

        #for crosshair
        self.plot.addItem(self.vLine, ignoreBounds=True)
        for i in range(0, len(self.hLines)):
            self.plot.addItem(self.hLines[i], ignoreBounds=True)

        self.setWidget(self.layout)

    '''
    Update Crosshair when mouse is moved on plot
    '''
    def mouseMoved(self, evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if self.plot.sceneBoundingRect().contains(pos):
            mousePoint = self.plot.vb.mapSceneToView(pos)
            index = int(mousePoint.x())
            index = self.data.normalize_time(mousePoint.x())

            currX = self.data.get_elapsed_times()[index]
            self.vLine.setPos(currX)
            label = "<span style='font-size: 12pt'>Time=%0.3f seconds,   " % currX

            currYs = []
            for i, name in enumerate(self.names):
                currY = self.data.get_sensor_values(str(name))[index]
                self.hLines[i].setPos(currY)
                label = label + "<span style='color: %s'>%s=%0.3f units" % (self.labelCols[i%len(self.labelCols)], str(name), currY)
                if i != len(self.names)-1:
                    label = label + ",  "

            self.timeLabel.setText(label)

#-----------------------
#-----RMtable Class-----
#-----------------------
class RMtable(QtGui.QDockWidget):
    '''
    RMtable functions similar to RMplot, except it produces a table instead of a
    plot (shocking, right?)
    Params:
    title = title for the plot
    '''
    def __init__(self, senNames):
        title = senNames[0]
        for name in senNames[1:]:
            title = title + ', ' + name
        title = title + ' Table'
        self.names = senNames
        super(RMtable, self).__init__(title)
        self.table = None

    def makeTable(self, data):
        #initialize list of times and the table
        times = data.get_elapsed_times()
        self.table = QtGui.QTableWidget(len(times), len(self.names)+1)
        headers = ['Time']

        #add times to the table
        for r, t in enumerate(times):
            self.table.setItem(r, 0, QTableWidgetItem("%0.8f" % (t)))

        #add the sensor values to the table
        for c, sen in enumerate(self.names):
            values = data.get_sensor_values(str(sen))
            for r, v in enumerate(values):
                self.table.setItem(r, c+1, QTableWidgetItem("%0.8f" % (v)))
            headers.append(str(sen))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        # self.table.setMaximumWidth(121*(len(self.names)+1))
        # self.table.setMinimumWidth(121*(len(self.names)+1))

        self.setWidget(self.table)

#-----------------------------------
#-----Sensor-Select Popup Class-----
#-----------------------------------
class SensorSelectPopup(QWidget):
    '''
    MultSensorSelectPopup is a popup window that gives the user the list of
    possible sensors and asks them to select multiple sensors
    '''
    def __init__(self, sensor_list):
        QWidget.__init__(self)
        self.setGeometry(QRect(200, 200, 400, 200))
        self.setWindowTitle("Select Sensor")
        self.layout = QtGui.QGridLayout(self)

        self.senList = QtGui.QListWidget()
        for i, sen in enumerate(sensor_list):
            self.senList.addItem(sen)
        self.senList.sortItems()

        self.selectedList = QtGui.QListWidget()
        self.selectedList.sortItems()
        self.layout.addWidget(self.senList, 0, 0)
        self.layout.addWidget(self.selectedList, 0, 1)

        # place the select button
        self.btn = QtGui.QPushButton("Select Sensor(s)")
        self.btn.setMaximumWidth(175)
        self.layout.addWidget(self.btn, 1, 0, 1, 2, Qt.AlignCenter)

        # connect methods for selecting/deselecting a sensor when it's clicked
        self.senList.itemClicked.connect(self.selectSen)
        self.selectedList.itemClicked.connect(self.deselectSen)

    '''
    Returns a list of the sensors that are selected
    '''
    def getState(self):
        selectedSens = []
        for i in range(0, self.selectedList.count()):
            selectedSens.append(self.selectedList.item(i).text())
        return selectedSens

    '''
    Returns the QPushButton object
    '''
    def getButton(self):
        return self.btn

    def selectSen(self, item):
        self.selectedList.addItem(item.text())
        self.senList.takeItem(self.senList.row(item))

    def deselectSen(self, item):
        self.senList.addItem(item.text())
        self.selectedList.takeItem(self.selectedList.row(item))

#----------------------------------
#-----Excel-Export Popup Class-----
#----------------------------------
class ExcelExportSelectPopup(QWidget):
    '''
    MultSensorSelectPopup is a popup window that gives the user the list of
    possible sensors and asks them to select multiple sensors
    '''
    def __init__(self, sensor_list):
        QWidget.__init__(self)
        self.setGeometry(QRect(200, 200, 400, 250))
        self.setWindowTitle("Excel Options")
        self.layout = QtGui.QGridLayout(self)
        self.sheets = {'sheet 1': []} #holds all of the sheets; key=name value=sensors
        self.sheetNames = {'sheet 1': 'sheet1'} #holds the name for each sheet (key corresponds to self.sheets)

        #Combo box selects which sheet you are on
        self.sheetSelectBox = QtGui.QComboBox(self)
        self.sheetSelectBox.setMaximumWidth(175)
        self.sheetSelectBox.addItem('sheet 1')
        # self.sheetSelectBox.currentIndexChanged.connect(selectSheet)
        self.layout.addWidget(self.sheetSelectBox, 0, 0, 1, 2, Qt.AlignCenter)

        #setNameLabel will change the name of the sheet
        self.setNameLabel = QtGui.QLabel('Sheet Name: ')
        self.setNameLabel.setMaximumWidth(100)
        self.layout.addWidget(self.setNameLabel, 1, 0, 1, 1, Qt.AlignRight)

        # set name for the sheet
        self.sheetNameBox = QtGui.QLineEdit('sheet1')
        self.sheetNameBox.setMaximumWidth(150)
        self.layout.addWidget(self.sheetNameBox, 1, 1, 1, 1, Qt.AlignLeft)
        # self.sheetNameBox.textEdited.connect(changeName)

        # list of all possible sensors
        self.senList = QtGui.QListWidget()
        for i, sen in enumerate(sensor_list):
            self.senList.addItem(sen)
        self.senList.sortItems()
        self.layout.addWidget(self.senList, 2, 0)

        #lists of all the selected sensors
        selectList = QtGui.QListWidget()
        selectList.itemClicked.connect(self.deselectSen)
        self.selectedLists = [] #list of all selected sensors
        self.selectedLists.append(selectList)
        self.layout.addWidget(self.selectedLists[0], 2, 1)


        # place the select button
        self.okBtn = QtGui.QPushButton("Ok")
        self.okBtn.setMaximumWidth(100)
        # params for addWidget:(button, row, column, rowspan, columnspan, aligns it center)
        self.layout.addWidget(self.okBtn, 3, 0, 1, 1, Qt.AlignCenter)

        # place the new sheet button
        self.newSheetBtn = QtGui.QPushButton("New Sheet")
        self.newSheetBtn.setMaximumWidth(100)
        self.layout.addWidget(self.newSheetBtn, 3, 1, 1, 1, Qt.AlignCenter)

        # connect methods for selecting/deselecting a sensor when it's clicked
        self.senList.itemClicked.connect(self.selectSen)
        # connect method
        self.newSheetBtn.clicked.connect(self.makeNewSheet)

    '''
    Returns a list of the sensors that are selected
    '''
    def getState(self):
        selectedSens = []
        for i in range(0, self.selectedList.count()):
            selectedSens.append(self.selectedList.item(i).text())
        return selectedSens

    def getOkButton(self):
        return self.okBtn

    def getNewSheetButton(self):
        return self.newSheetBtn

    def selectSen(self, item):
        l = self.selectedLists[self.sheetSelectBox.currentIndex()]
        l.addItem(item.text())
        self.sheets[]

    def deselectSen(self, item):
        l = self.selectedLists[self.sheetSelectBox.currentIndex()]
        l.takeItem(l.row(item))

    # Creates a new sheet, i.e. a new option in the combo box, and a new selectedList
    def makeNewSheet(self):
        newSheetID = 'sheet ' + str(len(self.sheets)+1)
        print newSheetID
        self.sheets[newSheetID] = [] #add to sheets data
        self.sheetNames[newSheetID] = newSheetID #add to name data
        self.sheetSelectBox.addItem(newSheetID) #add to combo box
        self.sheetSelectBox.setCurrentIndex(self.sheetSelectBox.count()-1)
        self.sheetNameBox.setText(newSheetID)

        #hide all current selectLists
        for li in self.selectedLists:
            li.hide()

        selectList = QtGui.QListWidget()
        selectList.itemClicked.connect(self.deselectSen)
        self.selectedLists.append(selectList)
        self.layout.addWidget(self.selectedLists[len(self.selectedLists)-1], 2, 1)


    # def changeName(self):
    #
    # def selectSheet(self, index):

#-----------------------
#-----Main Function-----
#-----------------------
def main():
    app = QtGui.QApplication(sys.argv)
    mw = GUI_window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
