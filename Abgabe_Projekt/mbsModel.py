import inputfilereader
import body
import constraint
import force
import measure
import dataobject
import json
import os

# Definition der Klasse "mbsModel", die ein Mehrkörpersystem (MBS) repräsentiert
class mbsModel:
    def __init__(self):
        # Liste zum Speichern aller MBS-Objekte
        self.__mbsObjectList = []
        # Hintergrundfarbe (Standard: Schwarz [0, 0, 0])
        self.backgroundcolor = [0, 0, 0]
    
    def importFddFile(self, filepath):
        # Extrahieren von Dateiname und Dateierweiterung
        file_name, file_extension = os.path.splitext(filepath)

        # Überprüfen, ob die geladene Datei die erwartete FDD-Endung hat
        if (file_extension == ".fdd"):
            # Lesen des Dateiinhalts und Erzeugen der entsprechenden MBS-Objekte
            self.__mbsObjectList = inputfilereader.readInput(filepath)
        else:
            # Falscher Dateityp
            print("Wrong file type: " + file_extension)
            return False
        
        # Setzen des Kontexts (Referenz auf das Modell selbst) in jedem MBS-Objekt
        for object in self.__mbsObjectList:
            object.setModelContext(self)

        return True
        
    def exportFdsFile(self, filepath):
        # Öffnen bzw. Anlegen einer FDS-Datei zum Schreiben
        f = open(filepath, "w")
        # Schreiben der Solver-Eingaben aller Objekte in die Datei
        for object in self.__mbsObjectList:
            object.writeSolverInput(f)
        f.close()
        
    def loadDatabase(self, database2Load):
        # Öffnen der JSON-Datei, aus der die MBS-Objekte geladen werden
        f = open(database2Load)
        data = json.load(f)
        f.close()

        # Durchlaufen aller gespeicherten Modelldaten
        for modelObject in data["modelObjects"]:
            # Abhängig von Typ/Subtyp wird das passende Klassenobjekt erstellt
            if (modelObject["type"] == "Body" and modelObject["subtype"] == "Rigid_EulerParameter_PAI"):
                self.__mbsObjectList.append(body.rigidBody(parameter=modelObject["parameter"]))
            elif (modelObject["type"] == "Constraint" and modelObject["subtype"] == "Generic"):
                self.__mbsObjectList.append(constraint.genericConstraint(parameter=modelObject["parameter"]))
            elif (modelObject["type"] == "Force"):
                if (modelObject["subtype"] == "GenericForce"):
                    self.__mbsObjectList.append(force.genericForce(parameter=modelObject["parameter"]))
                elif (modelObject["subtype"] == "GenericTorque"):
                    self.__mbsObjectList.append(force.genericTorque(parameter=modelObject["parameter"]))
            elif (modelObject["type"] == "Measure"):
                self.__mbsObjectList.append(measure.measure(parameter=modelObject["parameter"]))
            elif (modelObject["type"] == "DataObject" and modelObject["subtype"] == "Parameter"):
                self.__mbsObjectList.append(dataobject.parameter(parameter=modelObject["parameter"]))
        
        # Laden der Hintergrundfarbe aus der JSON-Datei
        self.backgroundcolor = data["Backgroundcolor"]
        return True

    def saveDatabase(self, dataBasePath):
        # Erstellen einer Liste (modelObjects), die alle MBS-Objekte repräsentiert
        modelObjects = []
        for object in self.__mbsObjectList:
            # Für jedes Objekt werden Typ, Subtyp und Parameter gespeichert
            modelObject = {
                "type": object.getType(),
                "subtype": object.getSubType(),
                "parameter": object.parameter
            }
            modelObjects.append(modelObject)
        
        # Erzeugen eines Dictionary mit Objekten und Hintergrundfarbe
        jDataBase = json.dumps({
            "modelObjects": modelObjects,            # Modellobjekte
            "Backgroundcolor": self.backgroundcolor  # Hintergrundfarbe
        })

        # Schreiben in die angegebene Datei (JSON-Format)
        with open(dataBasePath, "w") as outfile:
            outfile.write(jDataBase)
    
    def showModel(self, renderer):
        # Anzeigen aller MBS-Objekte in dem übergebenen Renderer (VTK)
        for object in self.__mbsObjectList:
            object.show(renderer)

    def getlistofmbsObject(self):
        # Gibt die Liste aller MBS-Objekte zurück
        return self.__mbsObjectList
