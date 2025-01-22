from mbsObject import mbsObject

# Importieren der VTK-Quellen, die einfache geometrische Objekte erstellen können
from vtkmodules.vtkFiltersSources import (
    vtkLineSource,
    vtkSphereSource,
    vtkRegularPolygonSource
)
# Importieren der Mapper-Klasse aus dem VTK-Rendering-Core
from vtkmodules.vtkRenderingCore import (
    vtkPolyDataMapper
)
# Importieren der Actor-Klasse aus dem VTK-Rendering-Core
from vtkmodules.vtkRenderingCore import vtkActor
# Importieren zusätzlicher VTK-Komponenten zur Transformation
from vtkmodules.all import vtkMatrix4x4, vtkTransform
import numpy as np

# Basisklasse "constraint", die von "mbsObject" erbt und einen Zwang im Mehrkörpersystem beschreibt
class constraint(mbsObject):
    def __init__(self, subtype, **kwargs):
        # Aufruf des Konstruktors der Basisklasse "mbsObject" mit dem Typ "Constraint"
        mbsObject.__init__(self, "Constraint", subtype, **kwargs)

# "genericConstraint" als abgeleitete Klasse von "constraint" für generische Zwänge
class genericConstraint(constraint):
    def __init__(self, **kwargs):
        # Überprüfung, ob "text" im Dictionary "kwargs" vorhanden ist
        if "text" in kwargs:
            # Standardparameter für einen generischen Zwang definieren
            parameter = {
                "body1": {"type": "string", "value": "no"},
                "body2": {"type": "string", "value": "no"},
                "position": {"type": "vector", "value": [0., 0., 0.]},
                "x_axis": {"type": "vector", "value": [0., 0., 0.]},
                "y_axis": {"type": "vector", "value": [0., 0., 0.]},
                "z_axis": {"type": "vector", "value": [0., 0., 0.]},
                "dx": {"type": "bool", "value": False},
                "dy": {"type": "bool", "value": False},
                "dz": {"type": "bool", "value": False},
                "ax": {"type": "bool", "value": False},
                "ay": {"type": "bool", "value": False},
                "az": {"type": "bool", "value": False}
            }
            # Aufruf des Konstruktors der Basisklasse "constraint" mit Default-Parametern
            constraint.__init__(self, "Generic", text=kwargs["text"], parameter=parameter)
        else:
            # Aufruf des Konstruktors der Basisklasse ohne zusätzliche Default-Parameter
            constraint.__init__(self, "Generic", **kwargs)

        # Zusammenfassen der Freiheitsgrade, die gesperrt (True) oder frei (False) sind
        self.__locks = {
            "translation": [
                self.parameter["dx"]["value"],
                self.parameter["dy"]["value"],
                self.parameter["dz"]["value"]
            ],
            "rotation": [
                self.parameter["ax"]["value"],
                self.parameter["ay"]["value"],
                self.parameter["az"]["value"]
            ]
        }

        # Farbdefinitionen für X-, Y- und Z-Achsen
        colors = {
            "X": (1, 0, 0),
            "Y": (0, 1, 0),
            "Z": (0, 0, 1),
        }

        # Schleife über die drei Hauptachsen X, Y, Z
        for i, axis in enumerate(["X", "Y", "Z"]):
            # Erstellen einer Linie (vtkLineSource) für die jeweilige Achse
            line = vtkLineSource()
            start = [0, 0, 0]
            end = [0, 0, 0]
            end[i] = self._symbolsScale  # Skalierung der Liniendarstellung

            # Festlegen der Start- und Endpunkte der Linie
            line.SetPoint1(*start)
            line.SetPoint2(*end)

            # Erstellen eines Mappers für die erzeugte Linie
            line_mapper = vtkPolyDataMapper()
            line_mapper.SetInputConnection(line.GetOutputPort())

            # Erzeugen eines Actors für die Linie
            line_actor = vtkActor()
            self.actors.append(line_actor)
            line_actor.SetMapper(line_mapper)
            # Farbe des Actors entsprechend der aktuellen Achse (X, Y oder Z) setzen
            line_actor.GetProperty().SetColor(colors[axis])

            # Prüfen, ob die Translation um diese Achse gesperrt (True) ist
            if self.__locks["translation"][i]:
                # Erzeugen einer Kugel (vtkSphereSource) am Ende der Achse
                sphere = vtkSphereSource()
                sphere.SetCenter(*end)
                sphere.SetRadius(0.05 * self._symbolsScale)

                # Erstellen eines Mappers für die Kugel
                sphere_mapper = vtkPolyDataMapper()
                sphere_mapper.SetInputConnection(sphere.GetOutputPort())

                # Erzeugen eines Actors für die Kugel und Festlegen der Farbe
                sphere_actor = vtkActor()
                self.actors.append(sphere_actor)
                sphere_actor.SetMapper(sphere_mapper)
                sphere_actor.GetProperty().SetColor(colors[axis])

            # Prüfen, ob die Rotation um diese Achse gesperrt (True) ist
            if self.__locks["rotation"][i]:
                # Erzeugen eines Rings (vtkRegularPolygonSource), der um einen Teil der Achse verschoben wird
                ring = vtkRegularPolygonSource()
                ring.SetCenter([0.7 * v for v in end])  # Ring-Zentrum etwas entlang der Achse platzieren
                ring.SetRadius(0.2 * self._symbolsScale)  # Radius des Rings
                ring.SetNumberOfSides(50)                 # Feinheit des Rings

                # Ausrichtung des Rings entsprechend der Achse
                if axis == "X":
                    ring.SetNormal(1, 0, 0)
                elif axis == "Y":
                    ring.SetNormal(0, 1, 0)
                elif axis == "Z":
                    ring.SetNormal(0, 0, 1)

                # Erstellen eines Mappers für den Ring
                ring_mapper = vtkPolyDataMapper()
                ring_mapper.SetInputConnection(ring.GetOutputPort())

                # Erzeugen eines Actors für den Ring und Festlegen der Farbe
                ring_actor = vtkActor()
                self.actors.append(ring_actor)
                ring_actor.SetMapper(ring_mapper)
                ring_actor.GetProperty().SetColor(colors[axis])

        # Erstellen einer Transformationsmatrix (4x4) als NumPy-Array und Initialisierung auf Einheitsmatrix
        transform_matrix = np.eye(4)
        # Befüllen der Transformationsmatrix mit Achsen- und Positionsinformationen aus den Parametern
        transform_matrix[:3, 0] = np.array(self.parameter["x_axis"]["value"])
        transform_matrix[:3, 1] = np.array(self.parameter["y_axis"]["value"])
        transform_matrix[:3, 2] = np.array(self.parameter["z_axis"]["value"])
        transform_matrix[:3, 3] = np.array(self.parameter["position"]["value"])

        # Erstellen eines vtkMatrix4x4-Objekts und Befüllen mit den Daten aus der NumPy-Matrix
        vtk_matrix = vtkMatrix4x4()
        vtk_matrix.DeepCopy(transform_matrix.ravel())

        # Anlegen eines vtkTransform-Objekts und Setzen der erstellten Matrix
        transform = vtkTransform()
        transform.SetMatrix(vtk_matrix)

        # Anwendung der Transformation auf alle zuvor erzeugten Actors
        for actor in self.actors:
            actor.SetUserTransform(transform)
