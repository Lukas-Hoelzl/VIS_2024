import mbsModel 
import sys
from pathlib import Path

from vtkmodules.vtkRenderingCore import (vtkRenderWindow, vtkRenderWindowInteractor, vtkRenderer)
from vtkmodules.all import vtkInteractorStyleTrackballCamera

from PySide6.QtCore import Slot
from PySide6.QtGui import QAction, QKeySequence, QScreen
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QApplication

from main_window import MainWindow

# Qt Application
app = QApplication(sys.argv)

window = MainWindow()

window.show()
sys.exit(app.exec())