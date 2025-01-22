from __future__ import annotations

import os
import vtk
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QAction, QKeySequence, QScreen, QColor
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QColorDialog, QDialog, QPushButton, QGroupBox, QLabel,
    QSlider, QLineEdit, QStatusBar
)

from main_widget import Widget
from mbsModel import mbsModel

# Erweiterte MainWindow-Klasse mit Screenshot-Funktion
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FDD-File Reader")

        # Menüleiste anlegen
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")
        self.settings_menu = self.menu.addMenu("Settings")
        self.help_menu = self.menu.addMenu("Help")

        # Actions für das Datei-Menü
        load_action = QAction("Load", self)
        load_action.triggered.connect(self.loadfile)
        self.file_menu.addAction(load_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.savemodel)
        self.file_menu.addAction(save_action)

        import_action = QAction("Import", self)
        import_action.triggered.connect(self.importfile)
        self.file_menu.addAction(import_action)

        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)

        # Actions für das Settings-Menü
        self.background_action = QAction("Background", self)
        self.background_action.triggered.connect(self.backgroundfunc)
        self.settings_menu.addAction(self.background_action)

        self.body_action = QAction("Body", self)
        self.body_action.triggered.connect(self.bodyfunc)
        self.settings_menu.addAction(self.body_action)

        # NEU: Screenshot-Action hinzufügen
        screenshot_action = QAction("Screenshot", self)
        screenshot_action.setShortcut("Ctrl+Shift+S")
        screenshot_action.triggered.connect(self.save_screenshot)
        self.settings_menu.addAction(screenshot_action)

        # Actions für das Hilfe-Menü
        help_action = QAction("Help", self)
        help_action.triggered.connect(self.helpfunc)
        self.help_menu.addAction(help_action)

        # Status-Bar
        self.status = self.statusBar()
        self.status.showMessage("Status wird geladen ...", 5000)

        # Größe des Hauptfensters
        geometry = self.screen().availableGeometry()
        self.setFixedSize(int(geometry.width() * 0.8), int(geometry.height() * 0.7))

        # Zentrales Widget (VTK-Ansicht)
        self.Widget = Widget(self)
        self.setCentralWidget(self.Widget)

        # Modellplaceholder
        self.mbsModel = None

    # -- Slot-Methoden für die Menü-Aktionen ----------------------------------

    def loadfile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "load File", "", "pyFreeDyn-File (*.json)")
        if filePath:
            self.mbsModel = mbsModel()
            self.mbsModel.loadDatabase(filePath)
            self.Widget.rendererMbsModel(self.mbsModel)
            self.status.showMessage(f"File loaded: {filePath}", 2000)

    def importfile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "import File", "", "pyFreeDyn-File (*.fdd)")
        if filePath:
            self.mbsModel = mbsModel()
            self.mbsModel.importFddFile(filePath)
            self.Widget.rendererMbsModel(self.mbsModel)
            self.status.showMessage(f"File imported: {filePath}", 2000)

    def savemodel(self):
        if self.mbsModel is None:
            self.status.showMessage("No model to save!", 2000)
            return

        filePath, _ = QFileDialog.getSaveFileName(self, "save File", "", "pyFreeDyn-File (*.json)")
        if filePath:
            self.mbsModel.saveDatabase(filePath)
            self.status.showMessage(f"File saved: {filePath}", 2000)

    def helpfunc(self):
        self.status.showMessage("Hilfe ist Aussichtslos!", 8000)

    def backgroundfunc(self):
        if self.mbsModel is None:
            self.status.showMessage("No model loaded!", 2000)
            return

        backgroundcolor = QColorDialog.getColor()
        if backgroundcolor.isValid():
            self.mbsModel.backgroundcolor = [
                backgroundcolor.red(),
                backgroundcolor.green(),
                backgroundcolor.blue()
            ]
            if hasattr(self.Widget, "renderer"):
                self.Widget.renderer.SetBackground(
                    [c / 255 for c in self.mbsModel.backgroundcolor]
                )
                self.Widget.renderer.GetRenderWindow().Render()

    def bodyfunc(self):
        if self.mbsModel is None:
            self.status.showMessage("No model loaded!", 2000)
            return

        # Beispiel: Body-Dialog aufrufen
        bodywindow = QDialog(self)
        bodywindow.setWindowTitle("Eigenschaften der Körper")
        main_layout = QVBoxLayout(bodywindow)

        self.listofBodys = []
        for obj in self.mbsModel.getlistofmbsObject():
            if obj.getType() == "Body":
                self.listofBodys.append(obj)

        self.Anzeigefarbe = []
        for body in self.listofBodys:
            group_box = QGroupBox(f"Eigenschaften von {body.parameter['name']['value']}")
            layout = QVBoxLayout(group_box)
            main_layout.addWidget(group_box)

            label_color = QLabel("Farbe:")
            layout.addWidget(label_color)

            color_edit = QLineEdit()
            color_edit.setReadOnly(True)

            color_show = QColor(
                body.parameter["color"]["value"][0],
                body.parameter["color"]["value"][1],
                body.parameter["color"]["value"][2]
            )
            color_edit.setStyleSheet(f"background-color: {color_show.name()};")
            layout.addWidget(color_edit)

            self.Anzeigefarbe.append(color_edit)

            color_button = QPushButton("Farbe wählen")
            color_button.clicked.connect(
                lambda _, b=body, idx=len(self.Anzeigefarbe)-1: self.bodycolor(b, idx)
            )
            layout.addWidget(color_button)

            label_transparency = QLabel("Transparenz:")
            layout.addWidget(label_transparency)

            slider_layout = QHBoxLayout()
            slider_layout.addWidget(QLabel("0%"))
            trans_slider = QSlider(Qt.Horizontal)
            trans_slider.setMinimum(0)
            trans_slider.setMaximum(100)
            current_t = body.parameter["transparency"]["value"]
            trans_slider.setValue(int(current_t / 255 * 100))
            trans_slider.valueChanged.connect(
                lambda val, b=body: self.transparency_update(val, b)
            )
            slider_layout.addWidget(trans_slider)
            slider_layout.addWidget(QLabel("100%"))
            layout.addLayout(slider_layout)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(lambda: self.push_OK(bodywindow))
        main_layout.addWidget(ok_button)

        bodywindow.exec()

    def bodycolor(self, body, index):
        bodycolor = QColorDialog.getColor()
        if bodycolor.isValid():
            body.parameter["color"]["value"] = (
                bodycolor.red(),
                bodycolor.green(),
                bodycolor.blue()
            )
            # Farb-Update im zugehörigen QLineEdit
            self.Anzeigefarbe[index].setStyleSheet(f"background-color: {bodycolor.name()};")

    def transparency_update(self, value, body):
        body.parameter["transparency"]["value"] = value * 255 / 100

    def push_OK(self, dialog):
        if hasattr(self, "listofBodys"):
            for b in self.listofBodys:
                b.hide(self.Widget.renderer)  # Entfernt bisherigen Actor
                b.updateActor()               # Erstellt neuen Actor
                b.show(self.Widget.renderer)  # Fügt neuen Actor hinzu
        dialog.accept()

    # ------------------- NEU: Screenshot-Funktion -------------------
    def save_screenshot(self):
        """
        Erstellt einen Screenshot des aktuellen VTK-Renderfensters
        und speichert ihn als PNG oder JPEG-Datei.
        """
        if not hasattr(self.Widget, "QVTKWidget"):
            self.status.showMessage("Keine QVTK-Ansicht gefunden!", 2000)
            return

        filePath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Screenshot",
            "",
            "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*)"
        )
        if not filePath:
            return  # Abbrechen

        # Erzeugt ein Fenster->Bild-Filter für die VTK-Ansicht
        render_window = self.Widget.QVTKWidget.GetRenderWindow()
        w2i = vtk.vtkWindowToImageFilter()
        w2i.SetInput(render_window)
        # Wähle z.B. RGB statt RGBA oder setze AA-Optionen, falls gewünscht
        w2i.SetInputBufferTypeToRGB()
        w2i.ReadFrontBufferOff()
        w2i.Update()

        # Dateiendung prüfen, um passenden Writer auszuwählen (PNGWriter oder JPEGWriter)
        _, ext = os.path.splitext(filePath)
        ext = ext.lower()
        if ext in [".jpg", ".jpeg"]:
            writer = vtk.vtkJPEGWriter()
        else:
            writer = vtk.vtkPNGWriter()

        writer.SetFileName(filePath)
        writer.SetInputConnection(w2i.GetOutputPort())
        writer.Write()

        self.status.showMessage(f"Screenshot saved to {filePath}", 2000)
