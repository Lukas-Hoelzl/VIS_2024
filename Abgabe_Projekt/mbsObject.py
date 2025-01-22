import os
import sys

# Basisklasse "mbsObject" für Mehrkörpersystem-Objekte
class mbsObject:
    def __init__(self, type, subtype, **kwargs):
        # Speichern des Typs und Subtyps
        self.__type = type
        self._subtype = subtype

        # Skalierungsfaktor für grafische Darstellungen (z.B. Symbolgrößen)
        self._symbolsScale = 10.

        # Überprüfen, ob Parameter übergeben wurden; ansonsten Abbruch
        if "parameter" in kwargs:
            self.parameter = kwargs["parameter"]
        else:
            sys.exit("parameter not provided, cannot create mbsObject!")    

        # Liste für VTK-Actors, die das Objekt in 3D visualisieren
        self.actors = []

        # Falls zusätzlich ein "text"-Argument übergeben wird, wird versucht,
        # aus den Zeilen Werte in die Parameter zu übernehmen
        if "text" in kwargs:
            for line in kwargs["text"]:
                splitted = line.split(":")
                for key in self.parameter.keys():
                    keyString = splitted[0].strip()
                    valueString = line[len(key) + 1:].strip()

                    # Zuordnung basierend auf Parametertyp
                    if(keyString == key):
                        if(self.parameter[key]["type"] == "float"):
                            self.parameter[key]["value"] = self.str2float(valueString)
                        elif(self.parameter[key]["type"] == "vector"):
                            self.parameter[key]["value"] = self.str2vector(valueString)
                        elif(self.parameter[key]["type"] == "colorvector"):
                            self.parameter[key]["value"] = self.str2colorvector(valueString)
                        elif(self.parameter[key]["type"] == "string"):
                            self.parameter[key]["value"] = valueString
                        elif(self.parameter[key]["type"] == "filepath"):
                            self.parameter[key]["value"] = os.path.normpath(valueString)
                        elif(self.parameter[key]["type"] == "bool"):
                            self.parameter[key]["value"] = self.str2bool(valueString)

    # Gibt den Typ (z.B. "Body", "Force" usw.) des Objekts zurück
    def getType(self):
        return self.__type
    
    # Gibt den Subtyp (z.B. "Rigid_EulerParameter_PAI" oder "GenericForce") des Objekts zurück
    def getSubType(self):
        return self._subtype
    
    # Setzt den Modellkontext (das zugehörige mbsModel), wird aktuell nicht weiter verwendet
    def setModelContext(self, modelContext):
        return
    
    # Schreibt Eingabedaten für einen Solver in eine Datei
    def writeSolverInput(self, file):
        text = []
        # Kopfzeile: Typ und Subtyp
        text.append(self.__type + " " + self._subtype + "\n")

        # Parameter Zeile für Zeile ausgeben
        for key in self.parameter.keys():
            value = self.parameter[key]["value"]
            # Die Ausgabe hängt vom Parametertyp ab
            if(self.parameter[key]["type"] == "float"):
                text.append("\t" + key + " = " + self.float2str(value) + "\n")
            elif(self.parameter[key]["type"] == "vector"):
                text.append("\t" + key + " = " + self.vector2str(value) + "\n")
            elif(self.parameter[key]["type"] == "string"):
                text.append("\t" + key + " = " + value + "\n")
            elif(self.parameter[key]["type"] == "filepath"):
                text.append("\t" + key + " = " + value + "\n")
            elif(self.parameter[key]["type"] == "bool"):
                text.append("\t" + key + " = " + self.bool2str(value) + "\n")

        # Abschluss für den jeweiligen Objektblock
        text.append("End" + self.__type + "\n%\n")

        # Schreiben in das übergebene Dateihandling-Objekt
        file.writelines(text)

    # Umwandlung von String zu Float
    @staticmethod
    def str2float(inString):
        return float(inString)

    # Umwandlung von Float zu String
    @staticmethod
    def float2str(inFloat):
        return str(inFloat)
    
    # Umwandlung eines Strings in einen Vektor mit 3 Elementen
    @staticmethod
    def str2vector(inString):
        return [
            float(inString.split(",")[0]),
            float(inString.split(",")[1]),
            float(inString.split(",")[2])
        ]

    # Umwandlung eines Vektors (Liste von 3 Elementen) in einen String
    @staticmethod
    def vector2str(inVector):
        return str(inVector[0]) + "," + str(inVector[1]) + "," + str(inVector[2])
    
    # Umwandlung eines Strings in einen Farbvektor (RGBA),
    # hier werden laut Code immer die ersten drei Werte plus der zweite Wert (!) ausgewertet
    @staticmethod
    def str2colorvector(inString):
        splitted = inString.split(" ")
        return [
            int(splitted[0]),
            int(splitted[1]),
            int(splitted[2]),
            int(splitted[1])  # Hinweis: Hier wird noch einmal splitted[1] verwendet
        ]
    
    # Umwandlung eines Strings in einen Bool-Wert
    # (1 -> True, alles andere -> False)
    @staticmethod
    def str2bool(inString):
        return bool(int(inString))

    # Umwandlung eines Bool-Werts in einen String ("yes"/"no")
    @staticmethod
    def bool2str(inBool):
        if inBool:
            return "yes"
        else:
            return "no"
    
    # Zeigt die zugehörigen Actors (3D-Darstellungen) in einem VTK-Renderer
    def show(self, renderer):
        for actor in self.actors:
            renderer.AddActor(actor)

    # Entfernt die zugehörigen Actors aus dem VTK-Renderer (Verstecken/Löschen der Darstellung)
    def hide(self, renderer):
        for actor in self.actors:
            renderer.RemoveActor(actor)
