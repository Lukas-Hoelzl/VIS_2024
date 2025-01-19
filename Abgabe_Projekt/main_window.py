from __future__ import annotations

from PySide6.QtCore import Slot
from PySide6.QtGui import QAction, QKeySequence, QScreen
from PySide6.QtWidgets import QMainWindow, QFileDialog, QVBoxLayout, QWidget
from main_widget import Widget
from mbsModel import mbsModel

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("FDD-File Reader")

        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        self.help_menu = self.menu.addMenu("Help")
        help_action = QAction("Help", self)
        help_action.triggered.connect(self.helpfunc)
        self.help_menu.addAction(help_action)

        load_action = QAction("Load", self)              #Load
        load_action.triggered.connect(self.loadfile)
        self.file_menu.addAction(load_action)

        save_action = QAction("Save", self)              #Save
        save_action.triggered.connect(self.savemodel)
        self.file_menu.addAction(save_action)

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

    def loadfile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "load File", "", "pyFreeDyn-File (*.json)")
        self.mbsModel = mbsModel()
        self.mbsModel.loadDatabase(filePath)
        self.Widget.rendererMbsModel(self.mbsModel)
        self.status.showMessage("File loaded",2000)

    def importfile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "import File", "", "pyFreeDyn-File (*.fdd)")
        self.mbsModel = mbsModel()
        self.mbsModel.importFddFile(filePath)
        self.Widget.rendererMbsModel(self.mbsModel)
        self.status.showMessage("File imported",2000)

    def savemodel(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "save File", "", "pyFreeDyn-File (*.json)")
        self.mbsModel.saveDatabase(filePath)
        self.status.showMessage("File saved", 2000)

    def helpfunc(self):
        self.status.showMessage("Hilfe ist Aussichtslos!")
    