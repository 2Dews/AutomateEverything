import os
import sys
import json

import arcpy

import pds_utilities as pds

def add_fields_from_fieldsObject(featureclass, fieldOjbectName, fieldsObject, fieldType):
    length = None
    if fieldType == "TEXT":
        if "length" in fieldsObject[fieldOjbectName]:
            length = fieldsObject[fieldOjbectName]["length"]
        else:
            pds.addPrintMessage("The {0} object {1} is missing the length element.".format(fieldOjbectName, fieldsObject[fieldOjbectName]), 2)

    if "fieldnames" in fieldsObject[fieldOjbectName]:        
        fieldAliasList = None
        if "fieldalias" in fieldsObject[fieldOjbectName]:
            fieldAliasList = fieldsObject[fieldOjbectName]["fieldalias"]
        for field in fieldsObject[fieldOjbectName]["fieldnames"]:
            alias = None
            if fieldAliasList:
                alias = fieldAliasList[fieldsObject[fieldOjbectName]["fieldnames"].index(field)]
            arcpy.AddField_management(featureclass, field, field_type = fieldType, field_length = length, field_alias = alias)
            pds.addPrintMessage("Added {0} to {1}".format(field, featureclass))
    else:
        pds.addPrintMessage("The {0} object {1} is missing the fieldnames element.".format(fieldOjbectName, fieldsObject[fieldOjbectName]), 2)

def add_fields_from_json(featureclass, jsonPath):
    """
    Supported json format: 
    {
    "stringfields": {
        "fields": [
            {
                "anyname": {
                    "length": 2,
                    "fieldnames": ["test1", "test2"],
                    "fieldalias": ["test 1", "test 2"]
                }
            }
        ]
    },
    "doublefields": { "fieldnames": [], "fieldalias": [] },
    "floatfields": { "fieldnames": [], "fieldalias": [] },
    "longfields": { "fieldnames": [], "fieldalias": [] },
    "datefields": { "fieldnames": [], "fieldalias": [] },
    "shortfields": { "fieldnames": [], "fieldalias": [] },
    "guidfields": { "fieldnames": [], "fieldalias": []
    }
}

    returns true if successful.
    """
    try:
        with open(jsonPath) as fieldsJson:
            fieldsObject = json.load(fieldsJson)

            if "stringfields" in fieldsObject:
                if "fields" in fieldsObject["stringfields"]:
                    for fieldOflength in fieldsObject["stringfields"]["fields"]:
                        fieldObjectName = None
                        for key in fieldOflength:
                            fieldObjectName = key
                        add_fields_from_fieldsObject(featureclass, fieldObjectName, fieldOflength, "TEXT")
                else:
                    pds.addPrintMessage("The stringfields object {0} is missing the fields element.".format(fieldOflength), 2)
            else:
                pds.addPrintMessage("No stringfields object found.")

            if "doublefields" in fieldsObject:
                add_fields_from_fieldsObject(featureclass, "doublefields", fieldsObject, "DOUBLE")
            else:
                pds.addPrintMessage("No doublefields object found.")

            if "floatfields" in fieldsObject:
                add_fields_from_fieldsObject(featureclass, "floatfields", fieldsObject, "FLOAT")
            else:
                pds.addPrintMessage("No floatfields object found.")

            if "longfields" in fieldsObject:
                add_fields_from_fieldsObject(featureclass, "longfields", fieldsObject, "LONG")
            else:
                pds.addPrintMessage("No longfields object found.")

            if "datefields" in fieldsObject:
                add_fields_from_fieldsObject(featureclass, "datefields", fieldsObject, "DATE")
            else:
                pds.addPrintMessage("No datefields object found.")

            if "shortfields" in fieldsObject:
                add_fields_from_fieldsObject(featureclass, "shortfields", fieldsObject, "SHORT")
            else:
                pds.addPrintMessage("No shortfields object found.")

            if "guidfields" in fieldsObject:
                add_fields_from_fieldsObject(featureclass, "guidfields", fieldsObject, "GUID")
            else:
                pds.addPrintMessage("No guidfields object found.")

        return True
    except:
        pds.customException()
        return False


