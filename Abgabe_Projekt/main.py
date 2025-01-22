import mbsModel 
import sys
from pathlib import Path

# Import von VTK-Modulen zur Visualisierung
from vtkmodules.vtkRenderingCore import (vtkRenderWindow, vtkRenderWindowInteractor, vtkRenderer)
from vtkmodules.all import vtkInteractorStyleTrackballCamera

# Import von PySide6-Modulen zur GUI-Erstellung
from PySide6.QtCore import Slot
from PySide6.QtGui import QAction, QKeySequence, QScreen
from PySide6.QtWidgets import QMainWindow, QApplication

from main_window import MainWindow  # Import des Hauptfensters

# Qt-Anwendung initialisieren
app = QApplication(sys.argv)

# Hauptfenster erstellen und anzeigen
window = MainWindow()
window.show()

# Ereignisverarbeitung starten und sicherstellen, dass die Anwendung korrekt beendet wird
sys.exit(app.exec())
