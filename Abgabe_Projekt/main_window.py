from __future__ import annotations

from PySide6.QtCore import Slot
from PySide6.QtGui import QAction, QKeySequence, QScreen , QColor
from PySide6.QtWidgets import QMainWindow, QFileDialog, QVBoxLayout, QWidget, QColorDialog
from main_widget import Widget
from mbsModel import mbsModel

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("FDD-File Reader")

        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        #Help Action
        self.help_menu = self.menu.addMenu("Help")
        help_action = QAction("Help", self)
        help_action.triggered.connect(self.helpfunc)
        self.help_menu.addAction(help_action)

        
        #Settings Action
        self.settings_menu = self.menu.addMenu("Settings")
        #Background
        self.background_action = QAction("Background",self)
        self.settings_menu.addAction(self.background_action)
        self.background_action.triggered.connect(lambda: self.backgroundfunc())


        #Load Action
        load_action = QAction("Load", self)              
        load_action.triggered.connect(self.loadfile)
        self.file_menu.addAction(load_action)

        #Save Action
        save_action = QAction("Save", self)              
        save_action.triggered.connect(self.savemodel)
        self.file_menu.addAction(save_action)

        #Import Action
        import_action = QAction("Import", self)          #Import
        import_action.triggered.connect(self.importfile)
        self.file_menu.addAction(import_action)

        # Exit QAction
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)


        # Status Bar
        self.status = self.statusBar()
        self.status.showMessage("Status wird geladen ...",10000)

        # Window dimensions
        geometry = self.screen().availableGeometry()
        self.setFixedSize(geometry.width() * 0.8, geometry.height() * 0.7)
        self.Widget = Widget(self)
        self.setCentralWidget(self.Widget)

    #Lade Funktion
    def loadfile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "load File", "", "pyFreeDyn-File (*.json)")
        self.mbsModel = mbsModel()
        self.mbsModel.loadDatabase(filePath)
        self.Widget.rendererMbsModel(self.mbsModel)
        self.status.showMessage("File loaded",2000)

    #Import Funktion
    def importfile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "import File", "", "pyFreeDyn-File (*.fdd)")
        self.mbsModel = mbsModel()
        self.mbsModel.importFddFile(filePath)
        self.Widget.rendererMbsModel(self.mbsModel)
        self.status.showMessage("File imported",2000)

    #Speicher Funktion
    def savemodel(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "save File", "", "pyFreeDyn-File (*.json)")
        self.mbsModel.saveDatabase(filePath)
        self.status.showMessage("File saved", 2000)

    #Help Funktion
    def helpfunc(self):
        self.status.showMessage("Hilfe ist Aussichtslos!")

    #Hintergrund Funktion
    def backgroundfunc(self):
        backgroundcolor = QColorDialog.getColor()
        if backgroundcolor.isValid():
            self.backgroundcolor_RGB = backgroundcolor.red(), backgroundcolor.green(), backgroundcolor.blue()
        self.mbsModel.backgroundcolor = self.backgroundcolor_RGB
        self.Widget.renderer.SetBackground([element/255 for element in self.mbsModel.backgroundcolor])