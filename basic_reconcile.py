from __future__ import print_function
import arcpy
import getpass
import re


text_match = '\[(\d+/\d+/\d+.+)]\s(Warning: Conflicts found reconciling version)\s([SDE]+\.\w+)\.'


def main():
    try:
        arcpy.env.overwriteOutput = True
        arcpy.env.workspace,user_name = set_workspace()
        db_exclude_list = ['SDE@WebAppDev_CLUSTER.sde']
        conn_files = [file for file in arcpy.ListFiles("SDE@*") if file in db_exclude_list]
        print (conn_files)

        for file in conn_files:

            db_string = r"Database Connections\{}".format(file)
            reconcile_errors = False
            versions_children = [version.name.encode('ascii') for version in arcpy.da.ListVersions(db_string) if version.parentVersionName not in ['sde.DEFAULT',None]]
            version_QA = [version.name.encode('ascii') for version in arcpy.da.ListVersions(db_string) if version.parentVersionName == 'sde.DEFAULT' and version.name[-3:]=='_QA']
            version_default = ['sde.DEFAULT']
            arcpy.ReconcileVersions_management(file,
                                               "ALL_VERSIONS",
                                               version_QA[0],
                                               versions_children,
                                               "LOCK_ACQUIRED",
                                               "ABORT_CONFLICTS",
                                               "BY_ATTRIBUTE",
                                               "FAVOR_TARGET_VERSION",
                                               "POST",
                                               "KEEP_VERSION",
                                               r"C:\Users\{}\Desktop\reconcile_folder\{}_{}.txt".format(user_name,file,version_QA[0]))

            with open(r"C:\Users\{}\Desktop\reconcile_folder\{}_{}.txt".format(user_name,file,version_QA[0]),'r') as in_file,\
                    open(r"C:\Users\{}\Desktop\finalfolder\finalfolderlog.txt".format(user_name), "a") as outfile:
                line = in_file.readline()
                while line:
                    match = re.search(text_match,line)
                    if match:
                        reconcile_errors = True
                        outfile.write(file + "\n")
                        outfile.write("\t" + line + "\n")
                    line = in_file.readline()

            if reconcile_errors == False:
                arcpy.ReconcileVersions_management(file,
                                                   "ALL_VERSIONS",
                                                   version_default[0],
                                                   version_QA[0],
                                                   "LOCK_ACQUIRED",
                                                   "ABORT_CONFLICTS",
                                                   "BY_ATTRIBUTE",
                                                   "FAVOR_TARGET_VERSION",
                                                   "POST",
                                                   "KEEP_VERSION",
                                                   r"C:\Users\{}\Desktop\reconcile_folder\{}_{}.txt".format(user_name,file,version_default[0]))

                with open(r"C:\Users\{}\Desktop\reconcile_folder\{}_{}.txt".format(user_name,file,version_default[0]),
                          'r') as in_file, \
                        open(r"C:\Users\{}\Desktop\finalfolder\finalfolderlog.txt".format(user_name), "a") as outfile:
                    line = in_file.readline()
                    while line:
                        match = re.search(text_match, line)
                        if match:
                            outfile.write(file + "\n")
                            outfile.write("\t" + line + "\n")
                        line = in_file.readline()

    except Exception as E:
        print (E)
    finally:
        print ("finally")

def set_workspace():
    user_name = getpass.getuser()
    folder_path = r"C:\Users\{}\AppData\Roaming\ESRI\Desktop10.4\ArcCatalog\\".format(user_name)
    return folder_path,user_name




main()

# open(r"C:\Users\{}\Desktop\actual back up folder\reconcile_log.txt".format(user_name), "r") as infile,