# Script Name: pds_utilities.py
# Description: Generic functions that can be used across the BLM Alaska MTP solution.
#
#
# Created By:  Premier Data Services, Gus Martinka
# Date:        May 2012
# ArcGIS Version: 10.x
# Python Version: 2.6

import sys
import os
import traceback
import arcpy
import string
import random

def listDataInGDB(gdb):
    ''' 
        Returns a list with the full path or all feature classes and tables in the gdb. 
        Paths will be all lower case. 
    '''
    originalWorkspace = arcpy.env.workspace
    arcpy.env.workspace = gdb
    outputList = []
    for fds in arcpy.ListDatasets('','feature') + ['']:
        for fc in arcpy.ListFeatureClasses('','',fds):
            outputList.append(os.path.join(arcpy.env.workspace, fds, fc).lower())
    for table in arcpy.ListTables():
        outputList.append(os.path.join(arcpy.env.workspace, table).lower())
    arcpy.env.workspace = originalWorkspace
    return outputList

def createList(strList,strDelim):
    """
    Create a python list.
    """
    import shlex
    try:
        theList = shlex.shlex(strList,posix=True)
        theList.whitespace += strDelim
        theList.whitespace_split = True
        return list(theList)
    except:
        return list()

def logToFile(logFile, logName):
    """
    Creates a logger that writes to a specified log file. Adding a logging handler allows the
    logger to be cleaned up when finished. If the log file already exists it will be appended to.
    """
    import logging
    # Does parent directory of logFile exist?
    if not os.path.exists(os.path.dirname(logFile)):
        addPrintMessage("Logfile parent directory does not exist: " + logFile, 2)
        sys.exit()

    logger = logging.getLogger(logName)
    logHandle = logging.FileHandler(logFile)
    formatter = logging.Formatter(fmt = '%(levelname)s: %(asctime)s %(message)s', datefmt = '%m/%d/%Y %I:%M:%S %p')
    logHandle.setFormatter(formatter)
    logger.addHandler(logHandle)
    logger.setLevel(logging.INFO)
    return logHandle

def closeLogger(logger, logHandle):
    """
    Cleans up the specified logging to free up resources and
    allow a new logger to be created if needed.
    """
    import logging
    logHandle.flush()
    logHandle.close()
    logging.getLogger(logger).removeHandler(logHandle)
    return

def customException():
    """
    Provides in depth exception reporting
    """
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    if pymsg != "PYTHON ERRORS:\nTraceback info:\n \nError Info:\n":
        addPrintMessage(pymsg, 2)

    if arcpy.GetMessages(2) != "":
        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
        addPrintMessage(msgs, 2)

def addPrintMessage(msg, severity = 0):
    """
    Adds a Message (in case this is run as a tool)
    and also prints the message to the screen (standard output)
    Split the message on \n first, so that if it's multiple lines,
    a GPMessage will be added for each line
    """
    try:
        print(msg)
    except:
        pass

    try:
        for string in msg.split('\n'):
            # Add appropriate geoprocessing message
            if severity == 0:
                    arcpy.AddMessage(string)
            elif severity == 1:
                    arcpy.AddWarning(string)
            elif severity == 2:
                    arcpy.AddError(string)
    except:
        pass

def checkDDP(currentMxd):
    """
    Get the current data driven page from the given map.
    """
    if hasattr(currentMxd,'dataDrivenPages'):
        currentDDP = currentMxd.dataDrivenPages
        pageNumber = currentMxd.dataDrivenPages.currentPageID
        addPrintMessage("The MXD has Data Driven Pages. The current page number is " + str(pageNumber) + ".", 0)
    else:
        addPrintMessage("Data driven pages not enabled.  Ensure you have the correct mxd.", 2)

def fieldTest(fc, fieldList):
    """
    Tests the input feature class to see if the all the given fields are present. 
    Returns true if all fields exist and false if any field is missing. 
    """
    try:
        fcFields = [f.name for f in arcpy.ListFields(fc)] 
        for field in fieldList:
            if field not in fcFields:
                return False
        return True
    except:
        return False


def decimal2dms(decimal_degrees):
    """
    Converts a floating point number of degrees to the equivalent number of degrees, minutes, and seconds, which are returned as a 3-element list.
    Example:
    >>> decimal2dms(-121.135)
    [-121, 8, 6.0000000000184173]
    """
    degrees = int(decimal_degrees)
    decimal_minutes = abs(decimal_degrees - degrees) * 60
    minutes = int(decimal_minutes)
    seconds = (decimal_minutes - minutes) * 60
    return [degrees, minutes, seconds]


def decimal2dm(decimal_degrees):
    """
    Converts a floating point number of degrees to the equivalent number of degrees and minutes, which are returned as a 2-element list.

    Example:
    >>> decimal2dm(-121.135)
    [-121, 8.100000000000307]
    """

    degrees = int(decimal_degrees)
    minutes = abs(decimal_degrees - degrees) * 60
    return [degrees, minutes]


def dms2decimal(degrees, minutes, seconds):
    """
    Converts degrees, minutes, and seconds to the equivalent number of decimal degrees.

    Example:
    >>> dms2decimal(-121, 8, 6)
    -121.13500000000001
    """

    decimal = 0.0
    if (degrees >= 0):
        decimal = degrees + float(minutes)/60 + float(seconds)/3600
    else:
        decimal = degrees - float(minutes)/60 - float(seconds)/3600

    return decimal

def addFieldsFromTemplate(targetFC, templateFC):
    """
    Adds fields to a feature class based on fields found in a template feature class.
    """
    try:
        # Lists fields currently found in the target feature class
        fieldnames = [f.name for f in arcpy.ListFields(targetFC)]
        # loops through fields found in the template feature class and adds a replica of the field to the target feature class
        for templateField in arcpy.ListFields(templateFC):
            if not templateField.name in fieldnames:
                # Verifies that the missing field has a valid type.
                if templateField.type != "OID":
                    arcpy.AddField_management(targetFC, templateField.name, templateField.type, templateField.precision, 
                                              templateField.scale, templateField.length, templateField.aliasName, 
                                              templateField.isNullable, "#", templateField.domain)
        return True

    except:
        customException()
        return False

def removeFieldsFromTemplate(targetFC, templateFC):
    """
    Removes fields from a feature class based on fields not found in a template feature class.
    """
    try:
        # Creates a list of fields found in the template feature class.
        templatefieldnames = [f.name for f in arcpy.ListFields(templateFC)]

        dropFields = []

        for fieldNames in arcpy.ListFields(targetFC):
            # Creates a list of field names that are not in the template feature class.
            if not fieldNames.name in templatefieldnames:
                dropFields.append(fieldNames.name)

        arcpy.DeleteField_management(targetFC, dropFields)

        addPrintMessage("Finished dropping fields not found in the template.", 0)
        return True

    except:
        customException()
        return False

def ifDelete(feature, message = False):
    """
    If a feature class exists, delete it.
    """
    if arcpy.Exists(feature):
        arcpy.Delete_management(feature)
        if message:
            addPrintMessage("Removed " + feature, 0)
    return

def validatePrjString(stringPRJ):
    """
     just perform a simple check that we have a real coordinate string
     created from exportToString()
    """
    if len(stringPRJ) > 10:
        if stringPRJ[0:6].upper() in 'GEOGCS,PROJCS':
            return True

def projectTransformAK(inFC, outFC, targetCoordSysString):
    """
     Project a featureclass, use the Alaska transformation when nessecary
     inFC must have a spatial reference
     outFC will be deleted before the projection
     if source and target Datum agree (have the same Datum), use no Transform method
     if the datums do not agree, use NAD_1927_To_NAD_1983_Alaska transform method

     when calling this function,
     targetCoordSysString can be created like this,
     arcpy.Describe(inFC).spatialReference.exportToString()
     the String representation seems more robust than sr.factoryCode = 3338 and sr.name = 'Alaska Albers Equal Area Conic'
     prj location for 3338:
     C:\Program Files (x86)\ArcGIS\Desktop10.0\Coordinate Systems\Projected Coordinate Systems\Continental\North America
     \Alaska Albers Equal Area Conic.prj
     epsg 3338
    """

    if arcpy.Exists(inFC):
        try:
            if arcpy.Exists(outFC):
                arcpy.Delete_management(outFC)

            if not validatePrjString(targetCoordSysString):
                util.addPrintMessage("Invalid Coordinate String.", 2)
                util.customException()
                sys.exit(2)

            inSR = arcpy.Describe(inFC).spatialReference
            inprjstring = inSR.exportToString()

            targetSR = arcpy.SpatialReference()
            targetSR.loadFromString(targetCoordSysString)

            ak_transform = 'NAD_1927_To_NAD_1983_Alaska'
            this_transform = ""

            if "1983" in inprjstring and "1983" in targetCoordSysString:
                this_transform = ""
            elif "1927" in inprjstring and "1927" in targetCoordSysString:
                this_transform = ""
            else:
                this_transform = ak_transform

            #  project
            message_str = "Projecting " + os.path.basename(inFC) + ' into ' + os.path.basename(outFC) + '.'
            addPrintMessage(message_str, 0)
            arcpy.Project_management(inFC, outFC, targetSR, this_transform)

            return True

        except:
            customException()
            return False

def sameDatum(FC1, FC2):
    """
    compare the Datums of two feature classes, return True or False
    """
    ret = ''
    sr1 = arcpy.Describe(FC1).spatialReference
    sr1string = sr1.exportToString()
    if sr1.type == '':
        return false


    sr2 = arcpy.Describe(FC2).spatialReference
    sr2string = sr2.exportToString()
    if sr2.type == '':
        return false

    # datumName is only available for Geographic CS
    if sr1.type.upper() == 'GEOGRAPHIC' and sr2.type.upper() == 'GEOGRAPHIC':
        if sr1.datumName == sr2.datumName:
            return True
        else:
            return False

    # datumName property is unavailable, so use less reliable 'in' operator
    if "1983" in sr1string and "1983" in sr2string:
        ret = True
    elif "1927" in sr1string and "1927" in sr2string:
        ret = True
    else:
        ret = False
    return ret

def matchFeatureClasseNames(geodatabase, featureClassList, featureDataSet='None'):
    """
     match the FC name to a Master Name, such a polyline3 to Polyline

     return a Dictionary, order may NOT be preserved

     annotation Annotation5
     polyline Polyline5
     polygon Polygon5
     point Point4
    """
    if arcpy.Exists(geodatabase):
        arcpy.env.workspace = geodatabase
        if featureDataSet:
            if arcpy.Exists(geodatabase  + os.sep + featureDataSet):
                scratch_fcs = arcpy.ListFeatureClasses("*","all",ds)
        else:
            scratch_fcs = arcpy.ListFeatureClasses("*","all")

        matched_fcs = dict()

        master_fc_names = []
        if ',' in featureClassList:
            master_fc_names = utils.createList(featureClassList,',')

        # add all Keys first
        # the Key should exist, if there is no match
        for m in master_fc_names:
            if not matched_fcs.has_key(m):
                matched_fcs[m] = None

        for cfg_fc in matched_fcs.keys():
            for s_fc in scratch_fcs:
                if cfg_fc.lower() in s_fc.lower():
                    matched_fcs[cfg_fc] = s_fc
        return matched_fcs

def GenRandomString(length=6, chars=string.ascii_letters + string.digits):
    """
    Generate a random String to help name a temporary FC or layer
    A featureclass Name cannot start with a number, so prefix with Letters
    arcpy.CreateScratchName
    """
    randCharList = [random.choice(chars) for i in range(length)]
    return 'ab' + ''.join( randCharList ).upper()

def insertTableRow(geodatabaseTable, dictFieldValues):
    """
    Insert a new Row in a table, populate the attributes
    no feature or geometry handling is included
    the dictionary key is the Field Name
    the dictionary value is the Field value

    """

    if not arcpy.Exists(geodatabaseTable):
        return False
        sys.exit()
    if len(dictFieldValues) == 0:
        return False
        sys.exit()

    # check that each Field in the dict is actually in the table
    tbl_fieldList = [f.name for f in arcpy.ListFields(geodatabaseTable)]

    dFV_keys = dictFieldValues.keys()
    missing = list()
    found = list()

    for k in dFV_keys:
        bFound = False
        for tfield in tbl_fieldList:
            if tfield.upper() == k.upper():
                bFound = True
        if bFound:
            found.append(k)
        else:
            missing.append(k)

    if len(missing) > 0:
        addPrintMessage("The following field(s) are missing from " + geodatabaseTable + ": " + str(missing) + '.' , 1)
        return False
        sys.exit()

    insert_values = list()

    for k,v in dictFieldValues.iteritems():
        insert_values.append(v)

    if len(found) > 0:
        c = arcpy.da.InsertCursor(geodatabaseTable, found)
        c.insertRow(insert_values)
        del c
        return True

def parseGdbFCPath(fullpath):
    """
    routine to split the Feature Class path into 3 components - geodatabase, dataset, feature class
    works with and without a feature Dataset
    can call specific token, parseGdbFCPath(gdb)['dataset'] instead of entire dict
    """
    gdb_dict = dict()
    if arcpy.Exists(fullpath) and '.GDB' in fullpath.upper():
        # can pass in a gdb or dataset or featureclass
        gdb_dict['rootgdb'] = None
        gdb_dict['dataset'] = None
        gdb_dict['name'] = None
        gdb_dict['fullpath'] = fullpath
        gdb_dict['datatype'] = None
        desc = arcpy.Describe(fullpath)
        gdb_dict['datatype'] = desc.dataType
        if desc.dataType.upper() == 'WORKSPACE':
            gdb_dict['rootgdb'] = fullpath
        elif desc.dataType.upper() == 'FEATUREDATASET':
            gdb_dict['rootgdb'] = os.path.dirname(fullpath)
            gdb_dict['dataset'] = os.path.basename(fullpath)
        elif desc.dataType.upper() == 'FEATURECLASS':
            gdb_dict['name'] = os.path.basename(fullpath)
            upone = os.path.dirname(fullpath)
            if arcpy.Describe(upone).dataType.upper() == 'FEATUREDATASET':
                gdb_dict['dataset'] = os.path.basename(desc.path)
                gdb_dict['rootgdb'] = os.path.dirname(desc.path)
            else:
                gdb_dict['rootgdb'] = upone

    return gdb_dict

def rows_as_update_dicts(cursor):
    """
    Return a arcpy.da.UpdateCursor() row as a dictionary.
    Allows accessing the rows attributes by field name. 
    
    Example:
    with arcpy.da.UpdateCursor(outLeaseDensity, cursorFields) as leaseCursor:
        for ur in pds.rows_as_update_dicts(leaseCursor):
            ur[leaseDensFieldName] = newValue
    """
    colnames = cursor.fields
    for row in cursor:
        row_object = dict(zip(colnames, row))
        yield row_object
        cursor.updateRow([row_object[colname] for colname in colnames])

def search_rows_as_dicts(cursor):
    """
    Return a arcpy.da.SearchCursor() row as a dictionary.
    Allows accessing the rows attributes by field name. 
    
    Example:
    with arcpy.da.SearchCursor(r'c:\data\world.gdb\world_cities', ('CITY_NAME', 'POPULATION', 'LATITUDE')) as sc:
        for row in rows_as_dicts(sc):
            print row['CITY_NAME']
    """
    colnames = cursor.fields
    for row in cursor:
        yield dict(zip(colnames, row))