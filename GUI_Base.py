# Rensselaer Motorsports 2014

# Author : Mitchell Mellone
# Version : 0.4.0.8
# Most Recent Edits : 2-21-15
# Description : Base class for a GUI using the pyQt library that will display
# information from the sensors on the car in a clear and readable way

import os, sys
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.console
from pyqtgraph.dockarea import *
import numpy as np
from PyQt4.Qt import *
import database as db

class GUI_window(QtGui.QMainWindow):
    def __init__(self):
        super(GUI_window, self).__init__()
        self.initUI()
        # self.area = DockArea()



        #self.setCentralWidget(self.area)
        self.popup_win = None
        self.data = db.DataBase()

        '''
        NOTE: current_plots and figures are basically the same, but it works and
        would require substantial effort to eliminate this redundancy so for the
        time being I will leave as is.
        However, from this moment on, figures should be the variable that is used.
        '''
        self.figures = {}
        self.current_plots = []

        self.data.parse_file('test_buffer.txt')
        self.plot_docks = []
        self.table_docks = []

    def initUI(self):
        #Exit action initialization
        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application.')
        exitAction.triggered.connect(QtGui.qApp.quit)

        addSensorData = QtGui.QAction(QtGui.QIcon('green+.png'), '&Add Graph', self)
        addSensorData.setShortcut('Ctrl+A')
        addSensorData.setStatusTip('Add a plot and table of data from a sensor.')
        addSensorData.triggered.connect(self.selectDataPopup)

        RMlogo = QtGui.QAction(QtGui.QIcon('rmlogo.png'), '&Exit', self)

        #Status bar initialization
        self.statusBar().showMessage('Ready')

        #Tool bar initialization
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAction)
        self.toolbar.addAction(addSensorData)
        self.toolbar.addAction(RMlogo)

        #Menu bar initialization
        menubar = self.menuBar()
        self.file_menu = menubar.addMenu('&File')
        self.file_menu.addAction(addSensorData)
        self.file_menu.addAction(exitAction)

        self.edit_menu = menubar.addMenu('&Edit')
        self.tools_menu = menubar.addMenu('&Tools')
        self.view_menu = menubar.addMenu('&View')
        self.help_menu = menubar.addMenu('&Help')

        self.setGeometry(300, 300, 500, 300)
        self.setWindowTitle('RM Data Analysis')
        self.setWindowIcon(QtGui.QIcon('rmlogo.png'))

        self.palette = QPalette()
        self.palette.setBrush(QPalette.Background,QBrush(QPixmap("rmlogo2.png")))
        self.setPalette(palette)

        self.show()


#----------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------ADD PLOTS AND TABLES-------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------
    '''
    selectDataPopup creates a pop up that prompts the user on what data to display
    it creates a button on that popup that selects the sensor in the dropdown window
    selectDataButton handles that button click
    '''
    def selectDataPopup(self):
        self.popup_win = DataSelect(self.data.get_list_of_sensors()) #create the popup window
        self.popup_win.setGeometry(QRect(200, 200, 200, 100)) #set window position (first 2 params) and size (last 2 params)
        btn = QPushButton('Select Data To Display', self.popup_win) #initialize button
        btn.setGeometry(QRect(12, 50, 175, 40)) #set button position (first 2 params) and size (last 2 params)
        self.connect(btn, SIGNAL("clicked()"), self.selectDataButton) #links button click to selectDataButton
        self.popup_win.show()

    def selectDataButton(self):
        if len(self.current_plots) == 0:
            self.initPlotTools() #add all of the relevant plot tools the first time a plot is added
        self.plot(self.popup_win.getState()) #generate the plot and table for the sensor
        self.popup_win.close()

    '''
    Plot creates a dock with a plot and corresponding table of values from the sensor
    it then adds it to the dock area
    '''
    def plot(self, sensorName):

        #CREATE THE DOCK
        self.resize(850,500) #resize the window to prepare for the new dock
        #creates the dock, for now they can't be closed, it's a little tricky getting that to work
        # dock
        # dock = Dock(sensorName, size=(600, 500), closable=False)

        #CREATE THE PLOT
        #get data from sensors
        times = self.data.get_elapsed_times()
        values = self.data.get_sensor_values(str(sensorName))

        #construct plot and place data on it
        # plot
        plot = pg.PlotWidget(title=sensorName)
        plot.plot(times, values, pen=(255, 0, 0))


        #find and set the view range limits and initial view
        #make sure x axis is in view
        ymin = self.data.get_min_sensor_value(str(sensorName))
        if ymin > 0:
            ymin = 0
        ymax = self.data.get_max_sensor_value(str(sensorName))
        if ymax < 0:
            ymax = 0
        #determine initial padding
        xpadding = times[len(times)-1] * 0.1
        ypadding = abs(ymax-ymin) * 0.1
        tmax = self.data.get_max_sensor_value('time') #find the maximum time
        #set the view limits, so the user can't scroll or zoom too far away from data
        plot.setLimits(xMin=0-xpadding, xMax=times[len(times)-1]+xpadding, yMin=ymin-ypadding, yMax=ymax+ypadding)
        plot.setRange(xRange=(0, tmax), yRange=(ymin, ymax), padding=0.0) #sets the original range of the plot
        plot.showGrid(x=True, y=True, alpha = 0.5) #shows the grid

        #add a cross hair
        vLine = pg.InfiniteLine(angle=90, movable=False)
        hLine = pg.InfiniteLine(angle=0, movable=False)
        plot.addItem(vLine, ignoreBounds=True)
        plot.addItem(hLine, ignoreBounds=True)

        self.current_plots.append((str(sensorName), plot)) #append the name and plot widget to current_plots
        self.figures[sensorName + "plot"] = plot #add the plot widget to the list of current figures
        self.addWidget(plot)
        # dock.addWidget(plot) #add the plot to the new dock

        #CREATE THE TABLE
        #initialize the table and set it to a width where each column can be seen
        table = QtGui.QTableWidget(len(times), 2)
        table.setMaximumWidth(250)
        table.setMinimumWidth(250)
        #add values to the table
        for i, (t, v) in enumerate(zip(times, values)):
            newTimeItem = QTableWidgetItem(str(t))
            newValueItem = QTableWidgetItem(str(v))
            table.setItem(i, 0, newTimeItem)
            table.setItem(i, 1, newValueItem)
        #name the table columns
        headers = ['Time', sensorName]
        table.setHorizontalHeaderLabels(headers)
        self.figures[sensorName + "table"] = table


        #ADD THE DOCK TO THE AREA
        #self.area.addDock(dock, 'above')



#----------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------VIEW FUNCTIONS-------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------
    '''
    initPlotTools will create 5 actions to adust the view range of a graph and set them in the view_menu
    The 5 actions are:
        Set View Range:  Allows the user to select the min and max x and y values on the plot window (no padding)
        Fit Data:        Automatically sets the view range to the min and max x and y points in the data (with padding)
        Fit Data Height: Automatically sets the min and max y values to the min and max y points in the data (with padding)
        Fit Data Width:  Automatically sets the min and max x values to the min and max x points in the data (with padding)
        Default View:    Sets view to see all of the data points as well as the x and y axis'
    '''
    def initPlotTools(self):
        #creates and adds setViewRange
        setViewRangeAction = QtGui.QAction('&Set View Range', self) #initializes action
        setViewRangeAction.setStatusTip('Set the x and y view range on desired plot.') #sets tip to show in status bar and when hovering
        setViewRangeAction.triggered.connect(self.setViewRangePopup) #calls function that creates popup when action is selected
        self.view_menu.addAction(setViewRangeAction) #adds action to the view menu

        #creates and adds fitData
        fitDataAction = QtGui.QAction('&Fit Data', self)
        fitDataAction.setStatusTip('Zooms to show all the data.')
        fitDataAction.triggered.connect(self.fitDataPopup)
        self.view_menu.addAction(fitDataAction)

        #creates and adds fitDataHeight
        fitDataHeightAction = QtGui.QAction('&Fit Data Height', self)
        fitDataHeightAction.setStatusTip('Zooms the y-axis to fit the data.')
        fitDataHeightAction.triggered.connect(self.fitDataHeightPopup)
        self.view_menu.addAction(fitDataHeightAction)

        #creates and adds fitDataWidth
        fitDataWidthAction = QtGui.QAction('&Fit Data Width', self)
        fitDataWidthAction.setStatusTip('Zooms the x-axis to fit the data.')
        fitDataWidthAction.triggered.connect(self.fitDataWidthPopup)
        self.view_menu.addAction(fitDataWidthAction)

        #creates and adds defaultView
        defaultViewAction = QtGui.QAction('&Default View', self)
        defaultViewAction.setStatusTip('Returns to the default view, shows all data and x- and y-axis.')
        defaultViewAction.triggered.connect(self.defaultViewPopup)
        self.view_menu.addAction(defaultViewAction)

    '''
    setViewRangePopup initializes the popup window that allows the user to set the view range
    It uses the RangeSelect class (declared and initialized below)
    The button added takes the data written in the pop-up's text boxes resizes the plot view range accordingly
    '''
    def setViewRangePopup(self):
        self.popup_win = RangeSelect(self, self.current_plots) #initialize the popup window
        self.popup_win.setGeometry(QRect(200, 200, 350, 200)) #set the popup's position (first 2 parameters), and width/height (second 2 parameters)
        btn = QPushButton('Select Range', self.popup_win) #declare and initialize the select button
        btn.setGeometry(QRect(87, 150, 175, 40)) #set the button's position and width/height
        self.connect(btn, SIGNAL("clicked()"), self.setViewRangeButton) #call setViewRangeButton function when the button is pressed
        self.popup_win.show() #show the popup window on screen

    #setViewRangeButton is run when button is pressed
    def setViewRangeButton(self):
        plotName = self.popup_win.getPlotName() #get the plot we are changing
        newXRange = (self.popup_win.getXMin(), self.popup_win.getXMax()) #get new x range
        newYRange = (self.popup_win.getYMin(), self.popup_win.getYMax()) #get new y range
        self.figures[plotName + "plot"].setRange(xRange=newXRange, yRange=newYRange, padding=0.0) #change the view range in the appropriate plot
        self.popup_win.close() #close the popup window after changes are made

    '''
    The following functions perform the other automatic range select features described above
    They all behave in similar ways to the setViewRange functions
    '''
    #controls fit data
    def fitDataPopup(self):
        self.popup_win = SelectPlot(self, self.current_plots)
        self.popup_win.setGeometry(QRect(200, 200, 200, 100))
        btn = QPushButton('Fit Data', self.popup_win)
        btn.setGeometry(QRect(25, 40, 150, 40))
        self.connect(btn, SIGNAL("clicked()"), self.fitDataButton)
        self.popup_win.show()
    def fitDataButton(self):
        plotName = self.popup_win.getPlotName()
        ymin = self.data.get_min_sensor_value(str(plotName))
        ymax = self.data.get_max_sensor_value(str(plotName))
        tmax = self.data.get_max_sensor_value('time')
        self.figures[plotName + "plot"].setRange(xRange=(0, tmax), yRange=(ymin, ymax))
        self.popup_win.close()

    #controls fit data height
    def fitDataHeightPopup(self):
        self.popup_win = SelectPlot(self, self.current_plots)
        self.popup_win.setGeometry(QRect(200, 200, 200, 100))
        btn = QPushButton('Fit Data Height', self.popup_win)
        btn.setGeometry(QRect(25, 40, 150, 40))
        self.connect(btn, SIGNAL("clicked()"), self.fitDataHeightButton)
        self.popup_win.show()
    def fitDataHeightButton(self):
        plotName = self.popup_win.getPlotName()
        ymin = self.data.get_min_sensor_value(str(plotName))
        ymax = self.data.get_max_sensor_value(str(plotName))
        self.figures[plotName + "plot"].setYRange(min=ymin, max=ymax)
        self.popup_win.close()

    #controls fit data width
    def fitDataWidthPopup(self):
        self.popup_win = SelectPlot(self, self.current_plots)
        self.popup_win.setGeometry(QRect(200, 200, 200, 100))
        btn = QPushButton('Fit Data Width', self.popup_win)
        btn.setGeometry(QRect(25, 40, 150, 40))
        self.connect(btn, SIGNAL("clicked()"), self.fitDataWidthButton)
        self.popup_win.show()
    def fitDataWidthButton(self):
        plotName = self.popup_win.getPlotName()
        tmax = self.data.get_max_sensor_value('time')
        self.figures[plotName + "plot"].setXRange(min=0, max=tmax)
        self.popup_win.close()

    #controls default view
    def defaultViewPopup(self):
        self.popup_win = SelectPlot(self, self.current_plots)
        self.popup_win.setGeometry(QRect(200, 200, 200, 100))
        btn = QPushButton('Set to Default View', self.popup_win)
        btn.setGeometry(QRect(25, 40, 150, 40))
        self.connect(btn, SIGNAL("clicked()"), self.defaultViewButton)
        self.popup_win.show()
    def defaultViewButton(self):
        plotName = self.popup_win.getPlotName()
        ymin = self.data.get_min_sensor_value(str(plotName))
        if ymin > 0:
            ymin = 0
        ymax = self.data.get_max_sensor_value(str(plotName))
        if ymax < 0:
            ymax = 0
        tmax = self.data.get_max_sensor_value('time')
        self.figures[plotName + "plot"].setRange(xRange=(0, tmax), yRange=(ymin, ymax))
        self.popup_win.close()

    #mouse move event for controlling crosshairs
    def mouseMoved(evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        for key in figures:
            keyType = key[len(key)-4:]
            if keyType == 'plot' and figures[key].sceneBvboundingRect().contains(pos):
                mousePoint = vb.mapSceneToView(pos)
                index = int(mousePoint.x())
                if index > 0 and index < len(data1):
                    label.setText("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (mousePoint.x(), data1[index], data2[index]))
                vLine.setPos(mousePoint.x())
                hLine.setPos(mousePoint.y())

    # proxy = pg.SignalProxy(p1.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)

#----------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------Classes for Popup Windows--------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------
class DataSelect(QWidget):
    def __init__(self, sensor_list):
        QWidget.__init__(self)
        # options = ['temperature', 'oil_pressure', 'accelerometer']
        options = sensor_list
        self.dropdown_box = QtGui.QComboBox(self)
        self.dropdown_box.addItems(options)
        self.dropdown_box.setMinimumWidth(150)
        self.dropdown_box.move(25, 10)
        self.dropdown_box.show()

    def getState(self):
        return self.dropdown_box.currentText()

class RangeSelect(QWidget):
    #win is the main window, current_plots are the plots currently displayed in the main window
    def __init__(self, win, current_plots):
        QWidget.__init__(self) #calls parent class constructor
        self.options = [] #list of choices for dropdown box
        self.plot_items = [] #holds the actual plot_items currently displayed
        for plots in current_plots:
            self.options.append(plots[0])
            self.plot_items.append(plots[1])

        #initialize the dropdown box (QComboBox), add names of current plots (options), set size/position
        self.dropdown_box = QtGui.QComboBox(self)
        self.dropdown_box.addItems(self.options)
        self.dropdown_box.setMinimumWidth(150)
        self.dropdown_box.move(100, 10)
        self.dropdown_box.show()

        self.xminLabel = QtGui.QLabel("min x", self)
        self.xminLabel.move(25, 50)
        self.xmin = QtGui.QLineEdit(self)
        self.xmin.move(75, 50)

        self.xmaxLabel = QtGui.QLabel("max x", self)
        self.xmaxLabel.move(200, 50)
        self.xmax = QtGui.QLineEdit(self)
        self.xmax.move(250, 50)

        self.yminLabel = QtGui.QLabel("min y", self)
        self.yminLabel.move(25, 100)
        self.ymin = QtGui.QLineEdit(self)
        self.ymin.move(75, 100)

        self.ymaxLabel = QtGui.QLabel("max y", self)
        self.ymaxLabel.move(200, 100)
        self.ymax = QtGui.QLineEdit(self)
        self.ymax.move(250, 100)

        self.xmin.setMaxLength(8)
        self.xmin.setMaximumWidth(60)
        self.xmax.setMaxLength(8)
        self.xmax.setMaximumWidth(60)
        self.ymin.setMaxLength(8)
        self.ymin.setMaximumWidth(60)
        self.ymax.setMaxLength(8)
        self.ymax.setMaximumWidth(60)

        self.dropdown_box.connect(self.dropdown_box, SIGNAL("currentIndexChanged(int)"), self.updateLineEdits)
        self.updateLineEdits()

        self.xmin.show()
        self.xmax.show()
        self.ymin.show()
        self.ymax.show()
        self.xminLabel.show()
        self.xmaxLabel.show()
        self.yminLabel.show()
        self.ymaxLabel.show()

    def updateLineEdits(self):
        i = self.options.index(self.dropdown_box.currentText())
        currRange = self.plot_items[i].viewRange() #returns current views visible range in format [[xmin, xmax], [ymin, ymax]]
        self.xmin.setText(str(currRange[0][0]))
        self.xmax.setText(str(currRange[0][1]))
        self.ymin.setText(str(currRange[1][0]))
        self.ymax.setText(str(currRange[1][1]))

    #return what is currently in the dropdown_box
    def getPlotName(self):
        return self.dropdown_box.currentText()

    def getXMin(self):
        return float(self.xmin.text())

    def getXMax(self):
        return float(self.xmax.text())

    def getYMin(self):
        return float(self.ymin.text())

    def getYMax(self):
        return float(self.ymax.text())

#Uses a dropdown box to prompt user to select a plot that is currently displayed
class SelectPlot(QWidget):
    #win is the main window, current_plots are the plots currently displayed in the main window
    def __init__(self, win, current_plots):
        QWidget.__init__(self) #calls parent class constructor
        self.options = [] #list of choices for dropdown box
        self.plot_items = [] #holds the actual plot_items currently displayed
        for plots in current_plots:
            self.options.append(plots[0])
            self.plot_items.append(plots[1])

        #initialize the dropdown box (QComboBox), add names of current plots (options), set size/position
        self.dropdown_box = QtGui.QComboBox(self)
        self.dropdown_box.addItems(self.options)
        self.dropdown_box.setMinimumWidth(150)
        self.dropdown_box.move(25, 10)
        self.dropdown_box.show()

    #return what is currently in the dropdown_box
    def getPlotName(self):
        return self.dropdown_box.currentText()

#----------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------Main Functions-------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------
def main():
    app = QtGui.QApplication(sys.argv)
    mw = GUI_window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
