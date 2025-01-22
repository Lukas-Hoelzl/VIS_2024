import body
import constraint
import force
import measure
import dataobject

import json

# Funktion zum Einlesen einer Eingabedatei, die MBS-Objekte (Mehrkörpersystem-Objekte) beschreibt
def readInput(path2File):
    # Öffnen der Datei im Lesemodus
    f = open(path2File, "r")

    # Einlesen des kompletten Inhalts der Datei und Aufsplitten in einzelne Zeilen
    fileContent = f.read().splitlines()
    f.close()

    # Initialisierung von Variablen zur Erkennung und Verarbeitung von Textblöcken
    currentBlockType = ""
    currentTextBlock = []
    listOfMbsObjects = []

    # Liste der möglichen Objekttypen, nach denen gesucht werden soll
    search4Objects = ["RIGID_BODY", "CONSTRAINT", "FORCE_GenericForce", "FORCE_GenericTorque", "MEASURE", "DATAOBJECT_PARAMETER"]

    # Durchlaufen aller Zeilen des eingelesenen Inhalts
    for line in fileContent:
        # Prüfung, ob ein Dollarzeichen ('$') in der Zeile vorhanden ist (Kennzeichen für neuen Block)
        if (line.find("$") >= 0):
            # Falls bereits ein aktueller Blocktyp gesetzt ist, wird ein Objekt erzeugt und zur Liste hinzugefügt
            if (currentBlockType != ""):
                if (currentBlockType == "RIGID_BODY"):
                    listOfMbsObjects.append(body.rigidBody(text=currentTextBlock))
                elif (currentBlockType == "CONSTRAINT"):
                    listOfMbsObjects.append(constraint.genericConstraint(text=currentTextBlock))
                elif (currentBlockType == "FORCE_GenericForce"):
                    listOfMbsObjects.append(force.genericForce(text=currentTextBlock))
                elif (currentBlockType == "FORCE_GenericTorque"):
                    listOfMbsObjects.append(force.genericTorque(text=currentTextBlock))
                elif (currentBlockType == "MEASURE"):
                    listOfMbsObjects.append(measure.measure(text=currentTextBlock))
                elif (currentBlockType == "DATAOBJECT_PARAMETER"):
                    listOfMbsObjects.append(dataobject.parameter(text=currentTextBlock))

                # Zurücksetzen des Blocktyps nach Verarbeitung
                currentBlockType = ""

        # Suche nach einem der definierten Typen innerhalb der Zeile
        for type_i in search4Objects:
            # Überprüfung, ob der Suchbegriff "type_i" an der richtigen Stelle im String gefunden wird
            if(line.find(type_i, 1, len(type_i)+1) >= 0):
                currentBlockType = type_i
                # Leeren des Zwischenspeichers für den aktuellen Textblock
                currentTextBlock.clear()
                break

        # Aktuelle Zeile zum aktuellen Textblock hinzufügen
        currentTextBlock.append(line)

    # Rückgabe einer Liste aller erstellten MBS-Objekte
    return listOfMbsObjects
