from __future__ import annotations

from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QAction, QKeySequence, QScreen , QColor
from PySide6.QtWidgets import QMainWindow, QFileDialog, QVBoxLayout, QHBoxLayout, QWidget, QColorDialog, QDialog, QPushButton, QGroupBox, QLabel, QSlider, QLineEdit
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
        #Body Color
        self.body_action = QAction("Body",self)
        self.settings_menu.addAction(self.body_action)
        self.body_action.triggered.connect(lambda: self.bodyfunc())


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
        self.status.showMessage("Hilfe ist Aussichtslos!", 100000)

    #Hintergrund Funktion
    def backgroundfunc(self):
        backgroundcolor = QColorDialog.getColor()
        if backgroundcolor.isValid():
            self.backgroundcolor_RGB = backgroundcolor.red(), backgroundcolor.green(), backgroundcolor.blue()
        self.mbsModel.backgroundcolor = self.backgroundcolor_RGB
        self.Widget.renderer.SetBackground([element/255 for element in self.mbsModel.backgroundcolor])

    #Körper Funktion
    def bodyfunc(self):
        bodywindow = QDialog()
        bodywindow.setWindowTitle("Eigenschaften der Körper")
        main_layout = QVBoxLayout(bodywindow)
        self.listofBodys = []
        for obj in self.mbsModel.getlistofmbsObject():
            if obj.getType() == "Body":
                self.listofBodys.append(obj)
        self.Anzeigefarbe = []
        for body in self.listofBodys:
            unterwindow = QGroupBox(f"Eigenschaften von {body.parameter["name"]["value"]}") #f interpretiert geschwunge Klammer nicht als string
            layout = QVBoxLayout(unterwindow)
            main_layout.addWidget(unterwindow)

            label_color = QLabel("Farbe")
            layout.addWidget(label_color)
            self.Anzeigefarbe.append(QLineEdit())
            self.Anzeigefarbe[self.listofBodys.index(body)].setReadOnly(True)
            print(body.parameter["color"]["value"][0])
            color_show = QColor(body.parameter["color"]["value"][0],body.parameter["color"]["value"][1],body.parameter["color"]["value"][2])
            self.Anzeigefarbe[self.listofBodys.index(body)].setStyleSheet(f"background-color: {color_show.name()};")
       
            layout.addWidget(self.Anzeigefarbe[self.listofBodys.index(body)])

            Color_button = QPushButton("Farbe wählen")
            Color_button.clicked.connect(lambda checked, bodycolor=body, index=self.listofBodys.index(body): self.bodycolor(bodycolor,index))
            layout.addWidget(Color_button)

            label_transparency = QLabel("Transparenz")
            layout.addWidget(label_transparency)
            layout_slider = QHBoxLayout()
            label_left = QLabel("0%")
            layout_slider.addWidget(label_left)
            transparency_slider = QSlider(Qt.Horizontal)
            transparency_slider.setMinimum(0)
            transparency_slider.setMaximum(100)
            transparency_slider.setValue(body.parameter["transparency"]["value"]/255*100)
            transparency_slider.valueChanged.connect(lambda value, bodyslider=body: self.transparency_update(value,bodyslider))
            layout_slider.addWidget(transparency_slider)
            label_right = QLabel("100%")
            layout_slider.addWidget(label_right)
            layout.addLayout(layout_slider)


        


        OK_button = QPushButton("Bernhard")
        OK_button.clicked.connect(lambda: self.push_OK(bodywindow))
        main_layout.addWidget(OK_button)
        bodywindow.exec()
        
    def bodycolor(self, body, indexbody):
        bodycolor = QColorDialog.getColor()
        if bodycolor.isValid():
            body.parameter["color"]["value"] = bodycolor.red(), bodycolor.green(), bodycolor.blue()
            self.Anzeigefarbe[indexbody].setStyleSheet(f"background-color: {bodycolor.name()};")
        #self.mbsModel.bodycolor = self.bodycolor_RGB
        #self.Widget.renderer.SetBackground([element/255 for element in self.mbsModel.bodycolor])

    def transparency_update(self,value,body):
        body.parameter["transparency"]["value"] = value*255/100
    

    def push_OK(self,window):
        for body in self.listofBodys:
            body.hide(self.Widget.renderer)
            body.updateActor()
            body.show(self.Widget.renderer)
        window.accept()