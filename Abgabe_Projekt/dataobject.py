from mbsObject import mbsObject

# Definiert eine Klasse "dataobject", die von "mbsObject" erbt
class dataobject(mbsObject):
    def __init__(self, subtype, **kwargs):
        # Ruft den Konstruktor der Basisklasse "mbsObject" auf
        # Übergibt dabei den Typ "DataObject" und den Subtyp, sowie zusätzliche Argumente
        mbsObject.__init__(self, "DataObject", subtype, **kwargs)

# Definiert eine Klasse "parameter", die von "dataobject" erbt
class parameter(dataobject):
    def __init__(self, **kwargs):
        # Überprüft, ob im Dictionary "kwargs" ein Schlüssel "text" vorhanden ist
        if "text" in kwargs:
            # Definiert ein Dictionary "parameter" mit Standardwerten für das Parameterobjekt
            parameter = {
                "name": {"type": "string", "value": ""},
                "InitialValue": {"type": "float", "value": 0.}
            }
            # Ruft den Konstruktor der Basisklasse "dataobject" auf
            # Setzt den Subtyp "Parameter", den Text aus "kwargs" und übergibt das Parameter-Dictionary
            dataobject.__init__(self, "Parameter", text=kwargs["text"], parameter=parameter)
        else:
            # Ruft den Konstruktor der Basisklasse "dataobject" auf,
            # falls kein "text"-Schlüssel übergeben wurde
            dataobject.__init__(self, "Parameter", **kwargs)
