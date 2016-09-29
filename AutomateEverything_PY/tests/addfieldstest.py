import unittest
import os

import arcpy

class Test_addfieldstest(unittest.TestCase):
    def test_add_fields_to_featureclass(self):
        
        import scripts
        
        testFCPath = r"in_memory\testfc"
        scripts.pds.ifDelete(testFCPath)
        arcpy.CreateFeatureclass_management(os.path.dirname(testFCPath), os.path.basename(testFCPath), "POLYGON")
        initFieldNameList = [f.name for f in arcpy.ListFields(testFCPath)]

        fieldsJsonPath = r"D:\GusDocuments\Projects\GISServices\AutomateEverything\AutomateEverything_PY\examples\exampleFields.json"
        self.assertTrue(scripts.addfields.add_fields_from_json(testFCPath, fieldsJsonPath))

        testFieldNameList = [f.name for f in arcpy.ListFields(testFCPath)]

        self.assertNotEqual(len(initFieldNameList), len(testFieldNameList))
        

if __name__ == '__main__':
    unittest.main()
