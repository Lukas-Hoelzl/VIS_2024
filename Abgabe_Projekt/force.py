from mbsObject import mbsObject

# Importieren der benötigten VTK-Module
from vtkmodules.vtkFiltersSources import (
    vtkLineSource,
    vtkArcSource,
    vtkConeSource
)
from vtkmodules.vtkFiltersCore import (
    vtkTubeFilter
)
from vtkmodules.vtkRenderingCore import (
    vtkPolyDataMapper
)
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkRenderingCore import vtkActor
from vtkmodules.vtkCommonMath import vtkMatrix4x4
import numpy as np

# Basisklasse "force" (Zugehörigkeit zu einem Mehrkörpersystem-Objekt)
class force(mbsObject):
    def __init__(self, subtype, **kwargs):
        # Ruft den Konstruktor der Basisklasse "mbsObject" auf und setzt den Typ "Force"
        mbsObject.__init__(self, "Force", subtype, **kwargs)

# Definition einer generischen Kraft (Ableitung von "force")
class genericForce(force):
    def __init__(self, **kwargs):
        # Prüfen, ob im Dictionary "kwargs" ein Schlüssel "text" vorhanden ist
        if "text" in kwargs:
            # Standardparameter für eine generische Kraft definieren
            parameter = {
                "body1": {"type": "string", "value": "no"},
                "body2": {"type": "string", "value": "no"},
                "PointOfApplication_Body1": {"type": "vector", "value": [0., 0., 0.]},
                "PointOfApplication_Body2": {"type": "vector", "value": [0., 0., 0.]},
                "mode": {"type": "string", "value": ""},
                "direction": {"type": "vector", "value": [0., 0., 0.]},
                "ForceExpression": {"type": "string", "value": ""}
            }
            # Ruft den Konstruktor der Basisklasse "force" auf und übergibt die Parameter
            force.__init__(self, "GenericForce", text=kwargs["text"], parameter=parameter)
        else:
            # Andernfalls wird direkt der Konstruktor der Basisklasse mit den übergebenen Argumenten aufgerufen
            force.__init__(self, "GenericForce", **kwargs)

        # Farbdefinitionen für die Achsen
        colors = {
            "X": (1, 0, 0),
            "Y": (0, 1, 0),
            "Z": (0, 0, 1),
        }

        # Erzeugung von drei zylindrischen Linien (eine pro Achse X, Y, Z) als Symbolik
        for i, axis in enumerate(["X", "Y", "Z"]):
            # Start- und Endpunkte der Linie bestimmen
            start = [0, 0, 0]
            end = [0, 0, 0]
            end[i] = self._symbolsScale  # Skalierung entlang der Achse

            # Erstellen einer Linienquelle (VTK-Objekt)
            line = vtkLineSource()
            line.SetPoint1(*start)
            line.SetPoint2(*end)

            # Hinzufügen eines Tube-Filters für die zylindrische Form
            tube = vtkTubeFilter()
            tube.SetInputConnection(line.GetOutputPort())
            tube.SetRadius(0.05 * self._symbolsScale)
            tube.SetNumberOfSides(50)
            tube.CappingOn()

            # Erstellen eines Mappers für die Tube-Geometrie
            tube_mapper = vtkPolyDataMapper()
            tube_mapper.SetInputConnection(tube.GetOutputPort())

            # Anlegen eines Actors, der diese Geometrie darstellt
            tube_actor = vtkActor()
            self.actors.append(tube_actor)
            tube_actor.SetMapper(tube_mapper)
            # Festlegen der Achsenfarbe
            tube_actor.GetProperty().SetColor(colors[axis])

        # Anlegen einer Transformation, um die Tube-Objekte zu verschieben
        transform = vtkTransform()
        # Positionierung erfolgt hier an der Ankopplungsstelle (Kraftangriffspunkt) für Body1
        transform.Translate(self.parameter["PointOfApplication_Body1"]["value"])

        # Anwenden der Transformation auf alle Actor-Objekte
        for actor in self.actors:
            actor.SetUserTransform(transform)

        # Erstellung einer zusätzlichen Linie zwischen den beiden Körpern (Body1 und Body2)
        start = self.parameter["PointOfApplication_Body1"]["value"]
        end = self.parameter["PointOfApplication_Body2"]["value"]
        line = vtkLineSource()
        line.SetPoint1(*start)
        line.SetPoint2(*end)

        # Analog wie zuvor, diese Linie ebenfalls zu einem Zylinder (Tube) machen
        tube = vtkTubeFilter()
        tube.SetInputConnection(line.GetOutputPort())
        tube.SetRadius(0.025 * self._symbolsScale)
        tube.SetNumberOfSides(50)
        tube.CappingOn()

        tube_mapper = vtkPolyDataMapper()
        tube_mapper.SetInputConnection(tube.GetOutputPort())

        tube_actor = vtkActor()
        self.actors.append(tube_actor)
        tube_actor.SetMapper(tube_mapper)
        # Farbe (rot) für die Verbindung zwischen den beiden Körpern
        tube_actor.GetProperty().SetColor((1, 0, 0))

# Definition eines generischen Moments bzw. Drehmoments (Ableitung von "force")
class genericTorque(force):
    def __init__(self, **kwargs):
        # Prüfen, ob "text" in den Parametern übergeben wurde
        if "text" in kwargs:
            # Standardparameter für ein generisches Moment festlegen
            parameter = {
                "body1": {"type": "string", "value": "no"},
                "body2": {"type": "string", "value": "no"},
                "mode": {"type": "string", "value": ""},
                "direction": {"type": "vector", "value": [0., 0., 0.]},
                "TorqueExpression": {"type": "string", "value": ""}
            }
            # Konstruktoraufruf der Basisklasse "force"
            force.__init__(self, "GenericTorque", text=kwargs["text"], parameter=parameter)
        else:
            # Alternativ direkt Konstruktoraufruf ohne Defaultparameter
            force.__init__(self, "GenericTorque", **kwargs)

        # Auslesen des Richtungsvektors und Normalisieren
        vec1 = np.array(self.parameter["direction"]["value"])
        vec1 = vec1 / np.linalg.norm(vec1)

        # Auswählen des Koordinaten-Einheitsvektors mit der kleinsten absoluten Komponente in vec1
        smallest_idx = np.argmin(np.abs(vec1))
        unit_vector = np.zeros(3)
        unit_vector[smallest_idx] = 1.0

        # Erzeugen eines Vektors, der senkrecht zu vec1 steht
        vec2 = np.cross(vec1, unit_vector)
        vec2 /= np.linalg.norm(vec2)

        # Ein weiterer senkrechter Vektor, um ein orthonormales Koordinatensystem zu bilden
        vec3 = np.cross(vec1, vec2)

        # Erstellen einer zylindrischen Achse, welche den Drehmoment-Vektor darstellt
        center = np.zeros(3)
        start = center - 0.5 * vec1 * self._symbolsScale
        end = center + 0.5 * vec1 * self._symbolsScale
        axis = vtkLineSource()
        axis.SetPoint1(*start)
        axis.SetPoint2(*end)

        axisTube = vtkTubeFilter()
        axisTube.SetInputConnection(axis.GetOutputPort())
        axisTube.SetRadius(0.05 * self._symbolsScale)
        axisTube.SetNumberOfSides(50)
        axisTube.CappingOn()

        axisTube_mapper = vtkPolyDataMapper()
        axisTube_mapper.SetInputConnection(axisTube.GetOutputPort())

        axisTube_actor = vtkActor()
        self.actors.append(axisTube_actor)
        axisTube_actor.SetMapper(axisTube_mapper)
        axisTube_actor.GetProperty().SetColor((1, 0, 0))

        # Erstellen eines Bogens (Arc), um eine umlaufende Rotation anzudeuten
        arc = vtkArcSource()
        arc.SetCenter(center)

        arc.SetPoint1(vec2 * self._symbolsScale)
        arc.SetPoint2(vec3 * self._symbolsScale)
        arc.SetResolution(10)

        tube = vtkTubeFilter()
        tube.SetInputConnection(arc.GetOutputPort())
        tube.SetRadius(0.05 * self._symbolsScale)
        tube.SetNumberOfSides(50)
        tube.CappingOn()

        tube_mapper = vtkPolyDataMapper()
        tube_mapper.SetInputConnection(tube.GetOutputPort())

        tube_actor = vtkActor()
        self.actors.append(tube_actor)
        tube_actor.SetMapper(tube_mapper)
        tube_actor.GetProperty().SetColor((1, 0, 0))

        # Erzeugen eines Kegels (Cone), um das Drehmomentsymbol zu vollenden (Pfeilspitze)
        arrow = vtkConeSource()
        arrow.SetRadius(0.2 * self._symbolsScale)
        arrow.SetHeight(0.5 * self._symbolsScale)
        arrow.SetResolution(50)

        arrow_mapper = vtkPolyDataMapper()
        arrow_mapper.SetInputConnection(arrow.GetOutputPort())

        # Aufbau einer 4x4-Transformationsmatrix, um den Kegel passend auszurichten
        transform_matrix = np.eye(4)
        transform_matrix[:3, 0] = -vec2    # Pfeil soll entgegengesetzt zu vec2 zeigen (Kegel-Ausrichtung in x)
        transform_matrix[:3, 1] = vec3
        transform_matrix[:3, 2] = -vec1
        transform_matrix[:3, 3] = vec3 * self._symbolsScale  # Positionierung entlang vec3

        vtk_matrix = vtkMatrix4x4()
        vtk_matrix.DeepCopy(transform_matrix.ravel())

        arrow_transform = vtkTransform()
        arrow_transform.SetMatrix(vtk_matrix)

        arrow_actor = vtkActor()
        self.actors.append(arrow_actor)
        arrow_actor.SetMapper(arrow_mapper)
        arrow_actor.SetUserTransform(arrow_transform)
        arrow_actor.GetProperty().SetColor((1, 0, 0))
