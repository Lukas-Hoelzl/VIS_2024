from mbsObject import mbsObject

# Importieren der notwendigen VTK-Module
from vtkmodules.vtkIOGeometry import vtkOBJReader
from vtkmodules.vtkRenderingCore import (
    vtkPolyDataMapper,
    vtkActor
)
from vtkmodules.all import vtkMatrix4x4, vtkTransform
import numpy as np

# Definition der Basisklasse "body" für Mehrkörpersystem-Objekte
class body(mbsObject):
    def __init__(self, subtype, **kwargs):
        # Initialisierung des Body-Objekts mit Typ "Body" und übergebenem Subtyp
        mbsObject.__init__(self, "Body", subtype, **kwargs)

# Definition der Klasse "rigidBody", abgeleitet von "body"
class rigidBody(body):
    def __init__(self, **kwargs):
        # Überprüfung, ob im Dictionary "kwargs" ein Schlüssel "text" vorhanden ist
        if "text" in kwargs:
            # Erstellen eines Dictionaries mit Standardparametern für einen starren Körper
            parameter = {
                "name": {"type": "string", "value": "UNKNOWN"},
                "mass": {"type": "float", "value": 1.},
                "COG": {"type": "vector", "value": [0., 0., 0.]},
                "geometry": {"type": "filepath", "value": ""},
                "position": {"type": "vector", "value": [0., 0., 0.]},
                "x_axis": {"type": "vector", "value": [1., 0., 0.]},
                "y_axis": {"type": "vector", "value": [0., 1., 0.]},
                "z_axis": {"type": "vector", "value": [0., 0., 1.]},
                "color": {"type": "colorvector", "value": [0, 0, 0, 0]},
                "transparency": {"type": "int", "value": 0}
            }

            # Aufruf des Konstruktors der Basisklasse "body" mit Standardparametern
            body.__init__(self, "Rigid_EulerParameter_PAI", text=kwargs["text"], parameter=parameter)
        else:
            # Aufruf des Konstruktors der Basisklasse "body" mit übergebenen Parametern
            body.__init__(self, "Rigid_EulerParameter_PAI", **kwargs)

        # Aktualisieren des Darstellungsobjekts (Actors) für die grafische Repräsentation
        self.updateActor()

    def updateActor(self):
        # Farbe aus den Parametern auslesen und von 0–255 in Werte von 0–1 umrechnen
        color = [rgb / 255 for rgb in self.parameter["color"]["value"]]
        
        # Liste für alle VTK-Actors dieses Körpers initialisieren (z.B. mehrere Teile möglich)
        self.actors = []

        # Einlesen der zugehörigen Geometriedatei im OBJ-Format
        reader = vtkOBJReader()
        reader.SetFileName(self.parameter["geometry"]["value"])
        reader.Update()  # Liest die Datei ein und bereitet die Daten auf

        # Erstellen eines Mappers für die gelesene Geometrie
        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        # Erzeugen eines VTK-Actors, der das 3D-Modell repräsentiert
        bodyActor = vtkActor()
        self.actors.append(bodyActor)  # Speichern des Actors in der Liste
        bodyActor.SetMapper(mapper)    # Zuweisung des Mappers (Geometriedaten) zum Actor

        # Setzen verschiedener Oberflächeneigenschaften
        bodyActor.GetProperty().SetDiffuse(0.8)        # Diffuse Reflexion
        bodyActor.GetProperty().SetSpecular(0.3)       # Spekulare Reflexion
        bodyActor.GetProperty().SetSpecularPower(60.0) # Glanzlicht-Eigenschaft
        bodyActor.GetProperty().SetColor(color[0:3])   # Farbe (RGB) aus den Parametern
        # Berechnung der Deckkraft basierend auf dem Transparenzwert (0 = durchsichtig, 255 = vollständig deckend)
        bodyActor.GetProperty().SetOpacity((255 - self.parameter["transparency"]["value"]) / 255)

        # Erstellen einer 4x4-Transformationsmatrix mithilfe von NumPy
        transform_matrix = np.eye(4)  # Identitätsmatrix als Ausgangspunkt
        # Aus den Parametern gelesene Achsenvektoren und Position übernehmen
        transform_matrix[:3, 0] = np.array(self.parameter["x_axis"]["value"])
        transform_matrix[:3, 1] = np.array(self.parameter["y_axis"]["value"])
        transform_matrix[:3, 2] = np.array(self.parameter["z_axis"]["value"])
        transform_matrix[:3, 3] = np.array(self.parameter["position"]["value"])

        # Erstellen einer VTK-Matrix und Befüllen mit den Werten der NumPy-Matrix
        vtk_matrix = vtkMatrix4x4()
        vtk_matrix.DeepCopy(transform_matrix.ravel())

        # Anlegen eines VTK-Transformationsobjekts zur Anwendung der Matrix
        transform = vtkTransform()
        transform.SetMatrix(vtk_matrix)

        # Zuweisen der Transformationsmatrix zum Actor (verschiebt/dreht das 3D-Modell)
        bodyActor.SetUserTransform(transform)
