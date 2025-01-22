from __future__ import annotations

#from PySide6.QtCore import QDateTime, Qt
#from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (QWidget, QHeaderView, QHBoxLayout, QTableView, QSizePolicy)
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis

# Importiere das QVTKRenderWindowInteractor-Modul von QVTK
import QVTKRenderWindowInteractor as QVTK
# Importiere den Renderer aus der VTK-Bibliothek
from vtkmodules.vtkRenderingCore import vtkRenderer
from vtkmodules.vtkCommonDataModel import vtkBoundingBox
import vtk
from vtkmodules.vtkRenderingCore import (vtkRenderWindow, vtkRenderWindowInteractor, vtkRenderer)
from vtkmodules.all import vtkInteractorStyleTrackballCamera

#class mainwidget(QVTK.QVTKRenderWindowInteractor):
class Widget(QWidget):
    def __init__(self, parent=None):
        # Aufruf des Konstruktors der Elternklasse "QWidget"
        QWidget.__init__(self)

        # Erstellen eines horizontalen Layouts für das Widget
        self.layout = QHBoxLayout()

    def rendererMbsModel(self, mbsModel):
        # Erzeugen eines QVTKRenderWindowInteractor-Widgets zur Anzeige von VTK-Inhalten
        self.QVTKWidget = QVTK.QVTKRenderWindowInteractor(self)
        # Hinzufügen des QVTK-Widgets zum Layout
        self.layout.addWidget(self.QVTKWidget)
        # Setzen des Layouts für dieses Widget
        self.setLayout(self.layout)

        # Erstellen eines VTK-Renderers (zuständig für das Rendering von 3D-Szenen)
        self.renderer = vtkRenderer()
        # Zugriff auf das RenderWindow (dient zur Darstellung der gerenderten Szene)
        self.renderWindow = self.QVTKWidget.GetRenderWindow()
        # Hinzufügen des Renderers zum RenderWindow
        self.renderWindow.AddRenderer(self.renderer)
        # Hintergrundfarbe des Renderers einstellen (Werte werden von 0 bis 1 normalisiert)
        self.renderer.SetBackground([element / 255 for element in mbsModel.backgroundcolor])

        # Initialisieren des Interactors (ermöglicht Interaktionen mit der Szene, z.B. Mausbewegungen)
        interactor = self.QVTKWidget.GetRenderWindow().GetInteractor()
        interactor.SetRenderWindow(self.renderWindow)

        # Festlegen des Interaktionsstils (Trackball-Kamera zur freien 3D-Navigation)
        style = vtkInteractorStyleTrackballCamera()
        interactor.SetInteractorStyle(style)

        # Aufrufen der Methode "showModel" des übergebenen mbsModel-Objekts,
        # um die 3D-Objekte in den Renderer zu laden
        mbsModel.showModel(self.renderer)

        # Ausführen des ersten Renderings
        self.renderWindow.Render()
        # Starten der Interaktionsschleife, damit der Nutzer die Szene mit Maus/Tastatur manipulieren kann
        interactor.Start()
