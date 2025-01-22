from __future__ import annotations

# Importieren der benötigten Klassen und Funktionen aus PySide6
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QAction, QKeySequence, QScreen, QColor
from PySide6.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QColorDialog,
    QDialog,
    QPushButton,
    QGroupBox,
    QLabel,
    QSlider,
    QLineEdit
)

# Importieren eigener Klassen
from main_widget import Widget
from mbsModel import mbsModel

# Definition der Hauptklasse "MainWindow", abgeleitet von "QMainWindow"
class MainWindow(QMainWindow):
    def __init__(self):
        # Aufruf des Konstruktors der Basisklasse QMainWindow
        QMainWindow.__init__(self)
        self.setWindowTitle("FDD-File Reader")

        # Erstellen der Menüleiste und Hinzufügen von Menüpunkten
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        # Hilfe-Menü (Help)
        self.help_menu = self.menu.addMenu("Help")
        help_action = QAction("Help", self)
        help_action.triggered.connect(self.helpfunc)
        self.help_menu.addAction(help_action)

        # Einstellungen-Menü (Settings)
        self.settings_menu = self.menu.addMenu("Settings")

        # Hintergrund-Einstellung (Background)
        self.background_action = QAction("Background", self)
        self.settings_menu.addAction(self.background_action)
        self.background_action.triggered.connect(lambda: self.backgroundfunc())

        # Einstellung für Körper-Farbe (Body Color)
        self.body_action = QAction("Body", self)
        self.settings_menu.addAction(self.body_action)
        self.body_action.triggered.connect(lambda: self.bodyfunc())

        # Menüeintrag zum Laden einer Datei
        load_action = QAction("Load", self)
        load_action.triggered.connect(self.loadfile)
        self.file_menu.addAction(load_action)

        # Menüeintrag zum Speichern einer Datei
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.savemodel)
        self.file_menu.addAction(save_action)

        # Menüeintrag zum Importieren einer Datei
        import_action = QAction("Import", self)
        import_action.triggered.connect(self.importfile)
        self.file_menu.addAction(import_action)

        # Menüeintrag zum Beenden der Anwendung (Exit)
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)

        # Erstellen einer Statusleiste und Setzen einer Statusmeldung
        self.status = self.statusBar()
        self.status.showMessage("Status wird geladen ...", 10000)

        # Einstellen der Fenstergröße (hier 80% der Bildschirmbreite und 70% der Höhe)
        geometry = self.screen().availableGeometry()
        self.setFixedSize(geometry.width() * 0.8, geometry.height() * 0.7)

        # Erstellen des Haupt-Widgets (Widget) und Setzen als zentrales Widget
        self.Widget = Widget(self)
        self.setCentralWidget(self.Widget)

    # Methode zum Laden einer Datei
    def loadfile(self):
        # Öffnet ein Dateidialog-Fenster, um eine Datei auszuwählen (Filter auf *.json)
        filePath, _ = QFileDialog.getOpenFileName(self, "load File", "", "pyFreeDyn-File (*.json)")
        # Erzeugt ein neues mbsModel-Objekt und lädt die Datenbank aus der ausgewählten Datei
        self.mbsModel = mbsModel()
        self.mbsModel.loadDatabase(filePath)
        # Rendert das geladene Modell in unserem Hauptwidget
        self.Widget.rendererMbsModel(self.mbsModel)
        # Setzt eine kurze Statusmeldung
        self.status.showMessage("File loaded", 2000)

    # Methode zum Importieren einer Datei (hier *.fdd)
    def importfile(self):
        # Öffnet ein Dateidialog-Fenster, um eine Datei auszuwählen (Filter auf *.fdd)
        filePath, _ = QFileDialog.getOpenFileName(self, "import File", "", "pyFreeDyn-File (*.fdd)")
        # Erzeugt ein neues mbsModel-Objekt und importiert das FDD-File
        self.mbsModel = mbsModel()
        self.mbsModel.importFddFile(filePath)
        # Rendert das importierte Modell
        self.Widget.rendererMbsModel(self.mbsModel)
        # Setzt eine kurze Statusmeldung
        self.status.showMessage("File imported", 2000)

    # Methode zum Speichern des Modells
    def savemodel(self):
        # Öffnet ein Dateidialog-Fenster, um einen Speicherort auszuwählen (Filter auf *.json)
        filePath, _ = QFileDialog.getSaveFileName(self, "save File", "", "pyFreeDyn-File (*.json)")
        # Speichert das aktuelle mbsModel in der angegebenen Datei
        self.mbsModel.saveDatabase(filePath)
        # Setzt eine kurze Statusmeldung
        self.status.showMessage("File saved", 2000)

    # Methode für die Hilfe-Funktion
    def helpfunc(self):
        # Zeigt eine Statusmeldung an
        self.status.showMessage("Hilfe ist Aussichtslos!", 100000)

    # Methode zum Ändern der Hintergrundfarbe
    def backgroundfunc(self):
        # Öffnet ein Farbwahl-Dialogfenster
        backgroundcolor = QColorDialog.getColor()
        # Wenn eine gültige Farbe ausgewählt wurde, extrahieren wir RGB-Werte
        if backgroundcolor.isValid():
            self.backgroundcolor_RGB = backgroundcolor.red(), backgroundcolor.green(), backgroundcolor.blue()
        # Setzen der Hintergrundfarbe im mbsModel und Aktualisieren des Renderers
        self.mbsModel.backgroundcolor = self.backgroundcolor_RGB
        self.Widget.renderer.SetBackground([element / 255 for element in self.mbsModel.backgroundcolor])

    # Methode zum Bearbeiten der Körpereigenschaften
    def bodyfunc(self):
        # Erstellen eines Dialogfensters zur Konfiguration der Körper
        bodywindow = QDialog()
        bodywindow.setWindowTitle("Eigenschaften der Körper")
        main_layout = QVBoxLayout(bodywindow)

        # Liste aller Körper im Modell
        self.listofBodys = []
        for obj in self.mbsModel.getlistofmbsObject():
            if obj.getType() == "Body":
                self.listofBodys.append(obj)

        # Für jede gefundene Instanz eines Körpers erstellen wir ein eigenes Unterfenster
        self.Anzeigefarbe = []
        for body in self.listofBodys:
            # Erzeugt eine Gruppierung (QGroupBox) mit dem Namen des Körpers
            # Achtung: f-Strings interpretieren Anführungszeichen in den Parametern
            unterwindow = QGroupBox(f"Eigenschaften von {body.parameter['name']['value']}")
            layout = QVBoxLayout(unterwindow)
            main_layout.addWidget(unterwindow)

            # Label und QLineEdit zur Anzeige der aktuellen Körperfarbe
            label_color = QLabel("Farbe")
            layout.addWidget(label_color)
            self.Anzeigefarbe.append(QLineEdit())
            self.Anzeigefarbe[self.listofBodys.index(body)].setReadOnly(True)
            # Erstellen eines QColor-Objekts aus den RGB-Werten des Körpers
            color_show = QColor(body.parameter["color"]["value"][0],
                                body.parameter["color"]["value"][1],
                                body.parameter["color"]["value"][2])
            # Hintergrundfarbe des QLineEdit-Feldes entsprechend der Körperfarbe setzen
            self.Anzeigefarbe[self.listofBodys.index(body)].setStyleSheet(f"background-color: {color_show.name()};")
            layout.addWidget(self.Anzeigefarbe[self.listofBodys.index(body)])

            # Erstellen eines Buttons zum Öffnen des Farbdialogs für diesen Körper
            Color_button = QPushButton("Farbe wählen")
            Color_button.clicked.connect(
                lambda checked, bodycolor=body, index=self.listofBodys.index(body): self.bodycolor(bodycolor, index)
            )
            layout.addWidget(Color_button)

            # Erstellen eines Labels und Sliders für die Transparenz-Einstellung
            label_transparency = QLabel("Transparenz")
            layout.addWidget(label_transparency)
            layout_slider = QHBoxLayout()
            label_left = QLabel("0%")
            layout_slider.addWidget(label_left)

            # Slider wird von 0 bis 100% gesetzt
            transparency_slider = QSlider(Qt.Horizontal)
            transparency_slider.setMinimum(0)
            transparency_slider.setMaximum(100)
            # Der initiale Wert wird aus dem Modell geholt und umgerechnet in Prozent
            transparency_slider.setValue(body.parameter["transparency"]["value"] / 255 * 100)
            # Verbinden der Value-Änderung mit einer Methode, die den Wert im Modell aktualisiert
            transparency_slider.valueChanged.connect(
                lambda value, bodyslider=body: self.transparency_update(value, bodyslider)
            )
            layout_slider.addWidget(transparency_slider)

            label_right = QLabel("100%")
            layout_slider.addWidget(label_right)
            layout.addLayout(layout_slider)

        # OK-Button zum Speichern/Aktualisieren der Änderungen
        OK_button = QPushButton("Bernhard")  # Humorvoller Button-Text
        OK_button.clicked.connect(lambda: self.push_OK(bodywindow))
        main_layout.addWidget(OK_button)

        # Öffnen des Dialogfensters im modalen Modus
        bodywindow.exec()

    # Methode zum Öffnen des Farbwahl-Dialogs für einen bestimmten Körper
    def bodycolor(self, body, indexbody):
        bodycolor = QColorDialog.getColor()
        # Falls eine gültige Farbe ausgewählt wurde, werden die RGB-Werte im Modell aktualisiert
        if bodycolor.isValid():
            body.parameter["color"]["value"] = (bodycolor.red(), bodycolor.green(), bodycolor.blue())
            # Aktualisieren des Hintergrunds in QLineEdit entsprechend der gewählten Farbe
            self.Anzeigefarbe[indexbody].setStyleSheet(f"background-color: {bodycolor.name()};")

    # Methode zum Aktualisieren der Transparenz im Modell
    def transparency_update(self, value, body):
        # Umrechnung des Slidervalues (0–100%) in einen Transparenzwert (0–255)
        body.parameter["transparency"]["value"] = value * 255 / 100

    # Methode, die aufgerufen wird, wenn der Benutzer den OK-Button klickt
    def push_OK(self, window):
        # Für jeden Körper wird die Darstellung im Renderer erneuert
        for body in self.listofBodys:
            # Zuerst den alten Actor verstecken
            body.hide(self.Widget.renderer)
            # Actor mit neuen Eigenschaften (Farbe, Transparenz) aktualisieren
            body.updateActor()
            # Danach den Actor wieder im Renderer anzeigen
            body.show(self.Widget.renderer)
        # Schließen des Dialogfensters
        window.accept()
