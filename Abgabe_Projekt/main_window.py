from __future__ import annotations

import os
import vtk
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QAction, QKeySequence, QScreen, QColor
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QColorDialog, QDialog, QPushButton, QGroupBox, QLabel,
    QSlider, QLineEdit
)

from main_widget import Widget
from mbsModel import mbsModel

class MainWindow(QMainWindow):
    def __init__(self):
        """
        Konstruktor des Hauptfensters (MainWindow).
        Hier werden verschiedene Menüeinträge erzeugt, 
        Widgets aufgebaut und das Fenster konfiguriert.
        """
        super().__init__()
        self.setWindowTitle("FDD- und Json-File Reader")

        # Menüleiste erstellen und den drei Hauptkategorien "File", "Settings" und "Help" zuordnen
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")
        self.settings_menu = self.menu.addMenu("Settings")
        self.help_menu = self.menu.addMenu("Help")

        # Actions (Menüpunkte) für das Datei-Menü:
        # ------------------------------------------------
        # 1. Load (Laden einer existierenden Datei)
        load_action = QAction("Load", self)
        load_action.triggered.connect(self.loadfile)
        self.file_menu.addAction(load_action)

        # 2. Save (Speichern in eine neue oder bestehende Datei)
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.savemodel)
        self.file_menu.addAction(save_action)

        # 3. Import (Einlesen eines FDD-Files)
        import_action = QAction("Import", self)
        import_action.triggered.connect(self.importfile)
        self.file_menu.addAction(import_action)

        # 4. Exit (Beenden der Anwendung)
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)

        # Actions (Menüpunkte) für das Einstellungs-Menü (Settings):
        # ------------------------------------------------
        # Hintergrundfarbe einstellen
        self.background_action = QAction("Background", self)
        self.background_action.triggered.connect(self.backgroundfunc)
        self.settings_menu.addAction(self.background_action)

        # Körpereigenschaften (Farbe, Transparenz) einstellen
        self.body_action = QAction("Body", self)
        self.body_action.triggered.connect(self.bodyfunc)
        self.settings_menu.addAction(self.body_action)

        # Screenshot-Funktion
        # Action zum Erstellen eines Bildschirmfotos (Screenshot) des VTK-Fensters
        screenshot_action = QAction("Screenshot", self)
        screenshot_action.setShortcut("Ctrl+Shift+S")  # Beispiel für ein Tastenkürzel
        screenshot_action.triggered.connect(self.save_screenshot)
        self.settings_menu.addAction(screenshot_action)

        # Actions (Menüpunkte) für das Hilfe-Menü (Help):
        # ------------------------------------------------
        # Hilfetext (aktuelles Beispiel nur eine Statusmeldung)
        help_action = QAction("Help", self)
        help_action.triggered.connect(self.helpfunc)
        self.help_menu.addAction(help_action)

        # Statusleiste am unteren Rand des Fensters
        self.status = self.statusBar()
        # Kurze Info-Meldung beim Start
        self.status.showMessage("Status wird geladen ...", 5000)

        # Festlegen der Fenstergröße (hier 80% der Bildschirmbreite, 70% der Höhe)
        geometry = self.screen().availableGeometry()
        self.setFixedSize(int(geometry.width() * 0.8), int(geometry.height() * 0.7))

        # Zentrales Widget (enthält das QVTKRenderWindowInteractor)
        self.Widget = Widget(self)
        self.setCentralWidget(self.Widget)

        # Placeholder für das Mehrkörpersystem-Modell (mbsModel), wird später geladen oder importiert
        self.mbsModel = None

    # Methoden, die aufgerufen werden, wenn die entsprechenden Menüpunkte geklickt werden

    def loadfile(self):
        """
        Öffnet einen Dateidialog zum Laden einer JSON-Datei (pyFreeDyn-File).
        Erstellt ein neues mbsModel-Objekt, lädt die Daten und rendert diese.
        """
        filePath, _ = QFileDialog.getOpenFileName(self, "load File", "", "pyFreeDyn-File (*.json)")
        if filePath:
            self.mbsModel = mbsModel()
            self.mbsModel.loadDatabase(filePath)
            self.Widget.rendererMbsModel(self.mbsModel)
            self.status.showMessage(f"File geladen: {filePath}", 2000)

    def importfile(self):
        """
        Öffnet einen Dateidialog zum Importieren einer FDD-Datei.
        Erstellt ein neues mbsModel-Objekt, importiert die FDD-Daten und rendert diese.
        """
        filePath, _ = QFileDialog.getOpenFileName(self, "import File", "", "pyFreeDyn-File (*.fdd)")
        if filePath:
            self.mbsModel = mbsModel()
            self.mbsModel.importFddFile(filePath)
            self.Widget.rendererMbsModel(self.mbsModel)
            self.status.showMessage(f"File importiert: {filePath}", 2000)

    def savemodel(self):
        """
        Öffnet einen Dateidialog zum Speichern der aktuellen Modell-Daten in einer JSON-Datei.
        """
        if self.mbsModel is None:
            self.status.showMessage("Kein Modell zum Speichern!", 2000)
            return

        filePath, _ = QFileDialog.getSaveFileName(self, "save File", "", "pyFreeDyn-File (*.json)")
        if filePath:
            self.mbsModel.saveDatabase(filePath)
            self.status.showMessage(f"File gespeichert in: {filePath}", 2000)

    def helpfunc(self):
        """
        Zeigt eine längere Statusmeldung im Statusbalken an. 
        (Beispielhaft als "Hilfe ist Aussichtslos!")
        """
        self.status.showMessage("Hilfe ist Aussichtslos!", 8000)

    def backgroundfunc(self):
        """
        Öffnet einen Farbwahldialog, um die Hintergrundfarbe anzupassen.
        Aktualisiert anschließend den Renderer, sofern ein Modell geladen wurde.
        """
        if self.mbsModel is None:
            self.status.showMessage("Kein Modell geladen!", 2000)
            return

        backgroundcolor = QColorDialog.getColor()
        if backgroundcolor.isValid():
            # Übernahme der ausgewählten Farbwerte in das Modell
            self.mbsModel.backgroundcolor = [
                backgroundcolor.red(),
                backgroundcolor.green(),
                backgroundcolor.blue()
            ]
            # Aktualisierung im Renderer
            if hasattr(self.Widget, "renderer"):
                self.Widget.renderer.SetBackground(
                    [c / 255 for c in self.mbsModel.backgroundcolor]
                )
                self.Widget.renderer.GetRenderWindow().Render()
            self.status.showMessage("Hintergrundfarbe geändert" , 2000)

    def bodyfunc(self):
        """
        Öffnet einen Dialog zum Bearbeiten der Körpereigenschaften (Farbe, Transparenz).
        Dabei werden alle Körper (type="Body") aus dem Modell abgefragt und einzeln angezeigt.
        """
        if self.mbsModel is None:
            self.status.showMessage("Kein Modell geladen!", 2000)
            return

        # Neuer Dialog
        bodywindow = QDialog(self)
        bodywindow.setWindowTitle("Eigenschaften der Körper")
        main_layout = QVBoxLayout(bodywindow)

        # Alle Körperobjekte im Modell ausfindig machen
        self.listofBodys = []
        for obj in self.mbsModel.getlistofmbsObject():
            if obj.getType() == "Body":
                self.listofBodys.append(obj)

        # QLineEdits zur Anzeige der aktuellen Farbe im Dialog
        self.Anzeigefarbe = []

        for body in self.listofBodys:
            # Neue Gruppe (QGroupBox) für jeden Body
            group_box = QGroupBox(f"Eigenschaften von {body.parameter['name']['value']}")
            layout = QVBoxLayout(group_box)
            main_layout.addWidget(group_box)

            # Farbe
            label_color = QLabel("Farbe:")
            layout.addWidget(label_color)

            color_edit = QLineEdit()
            color_edit.setReadOnly(True)

            # Die aktuelle Farbe wird aus dem Parameter-Dict gelesen
            color_show = QColor(
                body.parameter["color"]["value"][0],
                body.parameter["color"]["value"][1],
                body.parameter["color"]["value"][2]
            )
            # Hintergrund des QLineEdits wird auf die Körperfarbe gesetzt
            color_edit.setStyleSheet(f"background-color: {color_show.name()};")
            layout.addWidget(color_edit)

            self.Anzeigefarbe.append(color_edit)

            # Button zum Ändern der Farbe
            color_button = QPushButton("Farbe wählen")
            color_button.clicked.connect(
                lambda _, b=body, idx=len(self.Anzeigefarbe)-1: self.bodycolor(b, idx)
            )
            layout.addWidget(color_button)

            # Transparenz-Einstellung per Slider
            label_transparency = QLabel("Transparenz:")
            layout.addWidget(label_transparency)

            slider_layout = QHBoxLayout()
            slider_layout.addWidget(QLabel("0%"))

            trans_slider = QSlider(Qt.Horizontal)
            trans_slider.setMinimum(0)
            trans_slider.setMaximum(100)
            current_t = body.parameter["transparency"]["value"]
            # Aktualisierung des Schiebers in Prozent
            trans_slider.setValue(int(current_t / 255 * 100))
            trans_slider.valueChanged.connect(
                lambda val, b=body: self.transparency_update(val, b)
            )

            slider_layout.addWidget(trans_slider)
            slider_layout.addWidget(QLabel("100%"))
            layout.addLayout(slider_layout)

        # OK-Button zum Bestätigen/Schließen
        ok_button = QPushButton("Bernhard")
        ok_button.clicked.connect(lambda: self.push_OK(bodywindow))
        main_layout.addWidget(ok_button)

        # Dialog im modalen Modus starten
        bodywindow.exec()

    def bodycolor(self, body, index):
        """
        Öffnet einen Farbwahldialog und weist die ausgewählte Farbe dem Body zu.
        Die QLineEdit-Hintergrundfarbe (self.Anzeigefarbe[index]) wird entsprechend aktualisiert.
        """
        bodycolor = QColorDialog.getColor()
        if bodycolor.isValid():
            body.parameter["color"]["value"] = (
                bodycolor.red(),
                bodycolor.green(),
                bodycolor.blue()
            )
            self.Anzeigefarbe[index].setStyleSheet(f"background-color: {bodycolor.name()};")
            self.status.showMessage("Farbe des Körpers geändert" , 2000)

    def transparency_update(self, value, body):
        """
        Aktualisiert den Transparenzwert (0...255) im Body-Parameter, 
        basierend auf dem Sliderwert (0...100%).
        """
        body.parameter["transparency"]["value"] = value * 255 / 100
        self.status.showMessage("Transparenz geändert" , 2000)

    def push_OK(self, dialog):
        """
        Schließt den Körper-Eigenschaften-Dialog und rendert alle Körper neu, 
        damit Farb- und Transparenzänderungen wirksam werden.
        """
        if hasattr(self, "listofBodys"):
            for b in self.listofBodys:
                # Entfernt bisherige Actor-Darstellung aus dem Renderer
                b.hide(self.Widget.renderer)
                # Aktualisiert die Actor-Parameter (z. B. Farbe, Transparenz)
                b.updateActor()
                # Fügt die neue Actor-Darstellung dem Renderer hinzu
                b.show(self.Widget.renderer)
        dialog.accept()

    # Screenshot-Funktion 
    def save_screenshot(self):
        """
        Erstellt einen Screenshot des aktuellen VTK-Renderfensters
        und speichert ihn als PNG- oder JPEG-Datei ab.
        """
        # Überprüfen, ob ein QVTKRenderWindowInteractor existiert
        if not hasattr(self.Widget, "QVTKWidget"):
            self.status.showMessage("Keine QVTK-Ansicht gefunden!", 2000)
            return

        # Dateidialog für Screenshot-Speicherort
        filePath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Screenshot",
            "",
            "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*)"
        )
        if not filePath:
            return  # Abbrechen, wenn kein Pfad gewählt wurde

        # Zugriff auf das RenderWindow (zur Gewinnung der Pixeldaten)
        render_window = self.Widget.QVTKWidget.GetRenderWindow()

        # Ein vtkWindowToImageFilter wandelt den Inhalt des Render-Fensters in ein Bild um
        w2i = vtk.vtkWindowToImageFilter()
        w2i.SetInput(render_window)
        # Festlegen, dass RGB (ohne Alphakanal) verwendet wird
        w2i.SetInputBufferTypeToRGB()
        # Front Buffer ist normal ausgeschaltet - hier examplehaft Off
        w2i.ReadFrontBufferOff()
        w2i.Update()

        # Dateiendung prüfen, um den passenden Writer zu wählen
        _, ext = os.path.splitext(filePath)
        ext = ext.lower()
        if ext in [".jpg", ".jpeg"]:
            writer = vtk.vtkJPEGWriter()
        else:
            # Standard: PNG
            writer = vtk.vtkPNGWriter()

        # Writer konfigurieren und Bild schreiben
        writer.SetFileName(filePath)
        writer.SetInputConnection(w2i.GetOutputPort())
        writer.Write()

        # Feedback in der Statusleiste, dass der Screenshot erstellt wurde
        self.status.showMessage(f"Screenshot gespeichert in {filePath}", 2000)
