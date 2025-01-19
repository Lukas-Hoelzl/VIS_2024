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
        QWidget.__init__(self)            

        self.layout = QHBoxLayout()                
    
    def rendererMbsModel(self,mbsModel):
        self.QVTKWidget = QVTK.QVTKRenderWindowInteractor(self)
        self.layout.addWidget(self.QVTKWidget)
        self.setLayout(self.layout)

        self.renderer = vtkRenderer()                       # Erstelle einen VTK-Renderer
        self.renderWindow = self.QVTKWidget.GetRenderWindow()  # Füge den Renderer hinzu
        self.renderWindow.AddRenderer(self.renderer)

        # Interactor
        interactor = self.QVTKWidget.GetRenderWindow().GetInteractor()
        interactor.SetRenderWindow(self.renderWindow)

        style = vtkInteractorStyleTrackballCamera()
        interactor.SetInteractorStyle(style)

        mbsModel.showModel(self.renderer)

        # Render Interaktionloop
        self.renderWindow.Render()
        interactor.Start()