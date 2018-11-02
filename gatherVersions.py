from __future__ import print_function
import arcpy
import getpass
import re
import StringIO
import smtplib
import datetime

def main():
    try:
        arcpy.env.overwriteOutput = True
        arcpy.env.workspace,user_name = set_workspace()
        db_exclude = ['SDE@WebAppDev_CLUSTER.sde']
        version_exclude = ['"CITYHALL\\CDGLASS".cglass', #  This should be pkled in a file and checked for new versions
                           '"CITYHALL\\MORIO".addr_101618',
                           '"CITYHALL\\MORIO".BLDG_101618',
                           '"CITYHALL\\MORIO".DAZ',
                           '"CITYHALL\\TGRAHAM".GRAHAM_SANITARY',
                           '"CITYHALL\\TGRAHAM".TGRAHAM_TELECOM',
                           '"CITYHALL\\TGRAHAM".T_GRAHAM_STORM',
                           '"CITYHALL\\TGRAHAM".TGRAHAM_WATER'
                           '"CITYHALL\\ACASTILLO".OandFlorida',
                           '"CITYHALL\\SEDGE".Edge_Sanitary',
                           '"CITYHALL\\SEDGE".Edge_Stormwater',
                           '"CITYHALL\\SEDGE".Edge_Fiber',
                           '"CITYHALL\\SEDGE".Edge_Water',
                           'CEICHENMULLER.Ceichenmuller',
                           'SDE.Editor_WoodlawnCemetery_App']
        conn_files = [file for file in arcpy.ListFiles("SDE@*") if file not in db_exclude]
        print (conn_files)

        for file in conn_files:
            # arcpy.AcceptConnections(file, False)
            # arcpy.DisconnectUser(file,"ALL")

            db_string = r"Database Connections\{}".format(file)
            reconcile_errors = False
            versions_children = [version.name.encode('ascii') for version in arcpy.da.ListVersions(db_string)
                                 if version.parentVersionName not in ['sde.DEFAULT',None]
                                 and version.name not in version_exclude]
            version_QA = [version.name.encode('ascii') for version in arcpy.da.ListVersions(db_string)
                          if version.parentVersionName == 'sde.DEFAULT'
                          and version.name[-3:]=='_QA']
            version_default = ['sde.DEFAULT']

            print (file)
            print (version_QA)
            print (versions_children)

            print ('\n\n')
    except Exception as E:
        print (E)
    finally:
        for file in conn_files:
            arcpy.AcceptConnections(file, True)

def set_workspace():
    user_name = getpass.getuser()
    folder_path = r"C:\Users\{}\AppData\Roaming\ESRI\Desktop10.4\ArcCatalog\\".format(user_name)
    return folder_path,user_name




main()