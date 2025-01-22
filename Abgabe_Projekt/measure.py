from mbsObject import mbsObject

# Importieren der notwendigen VTK-Klassen
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
import numpy as np

# Definition einer Klasse "measure", die Messpunkte bzw. Messgrößen im Modell repräsentiert
class measure(mbsObject):
    def __init__(self, **kwargs):
        # Überprüfung, ob im Dictionary "kwargs" ein Schlüssel "text" vorhanden ist
        if "text" in kwargs:
            # Standardparameter für ein Measure-Objekt
            parameter = {
                "body1": {"type": "string", "value": "no"},
                "body2": {"type": "string", "value": "no"},
                "type": {"type": "string", "value": ""},
                "component": {"type": "int", "value": "0"},
                "location_body1": {"type": "vector", "value": [0., 0., 0.]},
                "location_body2": {"type": "vector", "value": [0., 0., 0.]},
                "vector_body1": {"type": "vector", "value": [0., 0., 0.]},
                "vector1_body2": {"type": "vector", "value": [0., 0., 0.]},
                "vector2_body2": {"type": "vector", "value": [0., 0., 0.]},
                "use_initial_value": {"type": "bool", "value": False}
            }
            # Konstruktoraufruf der Basisklasse mbsObject: Typ = "Measure", Subtyp = ""
            mbsObject.__init__(self, "Measure", "", text=kwargs["text"], parameter=parameter)
        else:
            # Konstruktoraufruf ohne Default-Parameter, falls kein "text" übergeben wurde
            mbsObject.__init__(self, "Measure", "", **kwargs)

        # Abhängig vom Wert des Parameters "type" wird der Subtyp des Measure-Objekts festgelegt
        if self.parameter["type"]["value"] == "displacement":
            self._subtype = "Translational"
        if self.parameter["type"]["value"] == "velocity":
            self._subtype = "Translational"
        if self.parameter["type"]["value"] == "angle":
            self._subtype = "Rotational"
        if self.parameter["type"]["value"] == "angular velocity":
            self._subtype = "Rotational"

        # Farbdefinitionen für mögliche Achsen (X, Y, Z)
        colors = {
            "X": (1, 0, 0),
            "Y": (0, 1, 0),
            "Z": (0, 0, 1),
        }

        # Falls die Messgröße translationaler Natur ist (Positions-/Geschwindigkeitsmessung)
        if self._subtype == "Translational":
            # Erzeugen von drei Achsen (X, Y, Z) als zylindrische Linien
            for i, axis in enumerate(["X", "Y", "Z"]):
                # Start- und Endpunkt der Achse
                start = [0, 0, 0]
                end = [0, 0, 0]
                end[i] = self._symbolsScale  # Skalierung entlang der entsprechenden Achse

                # Erzeugen einer Linie mittels vtkLineSource
                line = vtkLineSource()
                line.SetPoint1(*start)
                line.SetPoint2(*end)

                # Hinzufügen eines TubeFilters zur Linienquelle für eine 3D-repräsentative Röhre
                tube = vtkTubeFilter()
                tube.SetInputConnection(line.GetOutputPort())
                tube.SetRadius(0.05 * self._symbolsScale)
                tube.SetNumberOfSides(50)
                tube.CappingOn()

                # Erstellen eines Mappers und Zuweisung der gefilterten Geometrie
                tube_mapper = vtkPolyDataMapper()
                tube_mapper.SetInputConnection(tube.GetOutputPort())

                # Erzeugen eines Actors, der den Mapper rendert
                tube_actor = vtkActor()
                self.actors.append(tube_actor)
                tube_actor.SetMapper(tube_mapper)
                # Farbe festlegen (abhängig von Achse)
                tube_actor.GetProperty().SetColor(colors[axis])

            # Anlegen einer Transform, um alle Achsen-Actors an die Position von body1 zu verschieben
            transform = vtkTransform()
            transform.Translate(self.parameter["location_body1"]["value"])

            # Anwenden der Transformation auf alle erzeugten Actors
            for actor in self.actors:
                actor.SetUserTransform(transform)

            # Zusätzlich eine Linie zwischen body1 und body2 erzeugen, um z.B. eine Distanz zu visualisieren
            start = self.parameter["location_body1"]["value"]
            end = self.parameter["location_body2"]["value"]
            line = vtkLineSource()
            line.SetPoint1(*start)
            line.SetPoint2(*end)

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

        # Falls die Messgröße Rotationen oder Winkel betrifft (Rotational)
        elif self._subtype == "Rotational":
            # Aus den Parametern gelesene Vektoren (vector1_body2 und vector2_body2)
            # werden verwendet, um die Ebene des Rotationsmesskreises zu bestimmen
            vec2 = np.array(self.parameter["vector1_body2"]["value"])
            vec3 = np.array(self.parameter["vector2_body2"]["value"])

            # Normalenvektor aufgespannt durch Kreuzprodukt (vec2 x vec3)
            normal = np.cross(vec2, vec3)
            normal = normal / np.linalg.norm(normal)

            # Definition eines Mittelpunktes für die Rotationsdarstellung (z.B. Ursprung)
            center = [0, 0, 0]

            # Erzeugen einer zylindrischen Achse entlang des Normalenvektors
            start = center - 0.5 * normal * self._symbolsScale
            end = center + 0.5 * normal * self._symbolsScale
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

            # Erzeugen eines Bogens (Arc), der die Rotationsebene veranschaulicht
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

            # Erzeugen eines Kegels (vtkConeSource) als Pfeilspitze zur Verdeutlichung der Drehrichtung
            arrow = vtkConeSource()
            arrow.SetRadius(0.2 * self._symbolsScale)
            arrow.SetHeight(0.5 * self._symbolsScale)
            arrow.SetResolution(50)

            arrow_mapper = vtkPolyDataMapper()
            arrow_mapper.SetInputConnection(arrow.GetOutputPort())

            # Anlegen einer Transformation für den Kegel: Positionierung, Ausrichtung, etc.
            arrow_transform = vtkTransform()
            arrow_transform.Translate(vec3 * self._symbolsScale)
            angle = np.arccos(np.dot(vec3, vec2)) * 180 / np.pi
            # Hier ein Beispiel für eine mögliche Rotation um Z plus den errechneten Winkel
            arrow_transform.RotateZ(90 + angle)

            arrow_actor = vtkActor()
            self.actors.append(arrow_actor)
            arrow_actor.SetMapper(arrow_mapper)
            arrow_actor.SetUserTransform(arrow_transform)
