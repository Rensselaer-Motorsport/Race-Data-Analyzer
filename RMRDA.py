"""
RMRDA:
Rensselaer Motorsport Race Data Analyzer

Author: Mitchell Mellone (mellom3@rpi.edu)
Created: 4/17/2015
Last Modified: 4/17/2015
Version: 0.4.1

Copyright (C) 2015  Rensselaer Motorsports

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
import database as db

#---------------------------
#-----Main Window Class-----
#---------------------------
class GUI_window(QtGui.QMainWindow):
    #------------------------
    #GENERAL WINDOW FUNCTIONS
    #------------------------
    '''
    GUI_window is the main window for the UI and is created at start up.
    '''
    def __init__(self):
        super(GUI_window, self).__init__()
        self.initUI()
        self.prompt = None #for selecting things
        self.data = db.DataBase() #stores the data to be plotted

        #store list of current figures and such
        self.current_figures = {}
        self.plot_docks = []
        self.table_docks = []

        self.data.parse_file('test_buffer.txt') #parses data to be used this session

    '''
    Initializes the basic functions for the UI
    '''
    def initUI(self):
        #-----------------------------------------
        #CREATE ACTIONS THAT PERFORM GENERAL TASKS
        #-----------------------------------------
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
        createRMtable = QtGui.QAction(QtGui.QIcon('green+.png'), '&Add Graph', self)
        createRMtable.setShortcut('Ctrl+T')
        createRMtable.setStatusTip('Add a table of data from a sensor.')
        createRMtable.triggered.connect(self.RMtableSelect)

        #----------------------------
        #INITIALIZE MAIN GUI ELEMENTS
        #----------------------------
        #Status bar initialization
        self.statusBar().showMessage('Ready')

        #Tool bar initialization
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAction)
        self.toolbar.addAction(createRMplot)
        self.toolbar.addAction(createRMtable)

        #Menu bar initialization
        menubar = self.menuBar()
        self.file_menu = menubar.addMenu('&File')
        self.edit_menu = menubar.addMenu('&Edit')
        self.tools_menu = menubar.addMenu('&Tools')
        self.view_menu = menubar.addMenu('&View')
        self.help_menu = menubar.addMenu('&Help')

        #File Menu initialization
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

    def closeEvent(self, event):
        if self.prompt != None:
            self.prompt.close()

    #----------------
    #RMplot FUNCTIONS
    #----------------
    '''
    Creates a SensorSelctPopup to prompt user for sensor
    '''
    def RMplotSelect(self):
        self.prompt = MultSensorSelectPopup(self.data.get_list_of_sensors())
        self.connect(self.prompt.getButton(), SIGNAL("clicked()"), self.RMplotHandleButtonPress)
        self.prompt.show()

    def RMplotHandleButtonPress(self):
        self.createRMplot(self.prompt.getState())
        self.prompt.close()
        self.prompt = None

    '''
    Creates a RMplot and adds it to the GUI
    '''
    def createRMplot(self, sensorNames):
        newRMplot = RMplot(sensorNames)
        newRMplot.makePlot(self.data, sensorNames)
        self.addDockWidget(Qt.TopDockWidgetArea, newRMplot)

    #---------------------------
    #-----RMtable Functions-----
    #---------------------------
    '''
    Creates a SensorSelctPopup to prompt user for sensor
    '''
    def RMtableSelect(self):
        self.prompt = SensorSelectPopup(self.data.get_list_of_sensors())
        self.connect(self.prompt.getButton(), SIGNAL("clicked()"), self.RMtableHandleButtonPress)
        self.prompt.show()

    def RMtableHandleButtonPress(self):
        self.createRMtable(self.prompt.getState())
        self.prompt.close()
        self.prompt = None

    def createRMtable(self, sensorName):
        newRMtable = RMtable(sensorName)
        newRMtable.makeTable(self.data, sensorName)
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
        self.names = senNames
        super(RMplot, self).__init__(title)
        self.layout = pg.GraphicsLayoutWidget()
        self.timeLabel = pg.LabelItem(justify='right')
        self.layout.addItem(self.timeLabel)
        self.plot = self.layout.addPlot(row=1, col=0)
        self.data = None
        self.colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w']
        self.labelCols = ['red', 'green', 'blue', 'cyan', 'magenta', 'yellow', 'kahki', 'white']
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
    def makePlot(self, data, sensorNames):
        # Get times and values
        self.names = sensorNames #made a member variable b/c it is used in mouseMoved()
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
        # # Get times and values
        # self.name = sensorName #made a member variable b/c it is used in mouseMoved()
        # self.data = data
        # times = self.data.get_elapsed_times()
        # values = self.data.get_sensor_values(str(self.name))
        #
        # #Find limits for the view range of the plot
        # ymin = self.data.get_min_sensor_value(str(self.name))
        # if ymin > 0:
        #     ymin = 0
        # ymax = self.data.get_max_sensor_value(str(self.name))
        # if ymax < 0:
        #     ymax = 0
        # #determine initial padding
        # xpadding = times[len(times)-1] * 0.1
        # ypadding = abs(ymax-ymin) * 0.1
        # tmax = self.data.get_max_sensor_value('time') #find the maximum time
        #
        # self.plot.plot(times, values, pen=(255, 0, 0))
        #
        # self.plot.setLimits(xMin=0-xpadding, xMax=times[len(times)-1]+xpadding, yMin=ymin-ypadding, yMax=ymax+ypadding)
        # self.plot.setRange(xRange=(0, tmax), yRange=(ymin, ymax), padding=0.0) #sets the initial range of the plot
        # self.plot.showGrid(x=True, y=True, alpha=0.5)
        # self.plot.setLabel('bottom', text='Time Elapsed', units="s")
        # self.plot.setLabel('left', text=self.name, units=" unit")
        #
        # self.plot.setTitle(title=self.name)
        #
        # #for crosshair
        # self.plot.addItem(self.vLine, ignoreBounds=True)
        # self.plot.addItem(self.hLine, ignoreBounds=True)
        #
        # self.setWidget(self.layout)

    '''
    Used to add a crosshair to the plot
    '''
    def mouseMoved(self, evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if self.plot.sceneBoundingRect().contains(pos):
            mousePoint = self.plot.vb.mapSceneToView(pos)
            index = int(mousePoint.x())
            index = self.data.normalize_time(mousePoint.x())

            currX = self.data.get_elapsed_times()[index]
            self.vLine.setPos(currX)
            label = "<span style='font-size: 12pt'>Time=%0.4f seconds,   " % currX

            currYs = []
            for i, name in enumerate(self.names):
                currY = self.data.get_sensor_values(str(name))[index]
                self.hLines[i].setPos(currY)
                # label = label + "<span style='color: %s red'>%s=%0.4f" % (self.labelCols[i%len(self.labelCols)], str(name), currY)
                label = label + "<span style='color: %s'>%s=%0.4f units,  " % (self.labelCols[i%len(self.labelCols)], str(name), currY)

            self.timeLabel.setText(label)
            # self.timeLabel.setText("<span style='font-size: 12pt'>Time=%0.4f seconds,   <span style='color: red'>Value=%0.4f units</span>" % (currX, currY))

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
    def __init__(self, title):
        super(RMtable, self).__init__(title)
        self.table = None

    def makeTable(self, data, sensorName):
        times = data.get_elapsed_times()
        values = data.get_sensor_values(str(sensorName))
        self.table = QtGui.QTableWidget(len(values), 2)
        #add values to the sensor
        for i, (t, v) in enumerate(zip(times, values)):
            self.table.setItem(i, 0, QTableWidgetItem("%0.8f" % (t)))
            self.table.setItem(i, 1, QTableWidgetItem("%0.8f" % (v)))
        #name the table columns
        headers = ['Time', sensorName]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setMaximumWidth(241)
        self.table.setMinimumWidth(241)

        self.setWidget(self.table)

#------------------------------------------
#-----Single Sensor-Select Popup Class-----
#------------------------------------------
class SensorSelectPopup(QWidget):
    '''
    SensorSelectPopup is a popup window that allows the user to select a
    specific sensor
    '''
    def __init__(self, sensor_list):
        QWidget.__init__(self)
        # self.setGeometry(QRect(200, 200, 200, 100))

        options = sensor_list
        self.dropdown_box = QtGui.QComboBox(parent=self)
        self.dropdown_box.addItems(options)
        self.dropdown_box.setMinimumWidth(150)
        self.dropdown_box.move(25, 10)
        # self.dropdown_box.show()

        self.btn = QtGui.QPushButton("Select", parent=self)
        self.btn.setGeometry(QRect(12, 50, 175, 40))

    '''
    Returns the sensor that is currently selected
    '''
    def getState(self):
        return self.dropdown_box.currentText()

    '''
    Returns the QPushButton object
    '''
    def getButton(self):
        return self.btn

#--------------------------------------------
#-----Multiple Sensor-Select Popup Class-----
#--------------------------------------------
class MultSensorSelectPopup(QWidget):
    '''
    MultSensorSelectPopup is a popup window that gives the user the list of
    possible sensors and asks them to select multiple sensors
    '''
    def __init__(self, sensor_list):
        QWidget.__init__(self)
        self.setGeometry(QRect(200, 200, 400, 200))
        self.setWindowTitle("Select Sensor")
        self.layout = QtGui.QGridLayout(self)
        #place all of the radio buttons
        self.options = sensor_list
        self.senList = QtGui.QListWidget()
        for i, sen in enumerate(sensor_list):
            self.senList.addItem(sen)
            # self.radioButtons(i).move()
        # self.senList.setGeometry(10, 10, 185, 125)

        self.selectedList = QtGui.QListWidget()
        # self.selected.setGeometry(205, 10, 185, 125)
        self.layout.addWidget(self.senList, 0, 0)
        self.layout.addWidget(self.selectedList, 0, 1)

        # place the select button
        self.btn = QtGui.QPushButton("Select Sensor(s)")
        self.btn.setMaximumWidth(175)
        # self.btn.setGeometry(QRect(, 150, 175, 40))
        self.layout.addWidget(self.btn, 1, 0, 1, 2, Qt.AlignCenter)

        self.senList.sortItems()
        self.selectedList.sortItems()

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

#------------------------
#-----Main Functions-----
#------------------------
def main():
    app = QtGui.QApplication(sys.argv)
    mw = GUI_window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
