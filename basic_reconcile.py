import arcpy
import os
import getpass


def main():
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace,user_name = set_workspace()
    db_exclude_list = ['SDE@WebAppDev_CLUSTER.sde']
    conn_files = [file for file in arcpy.ListFiles("SDE@*") if file in db_exclude_list]

    with open(r"C:\Users\{}\Desktop\actual back up folder\reconcile_log.txt".format(user_name),"a") as out_file1:
        out_file1.write('********************************************************************\n')


    for file in conn_files:
        db_string = "Database Connections\{}".format(file)
        versions_children = [version.name.encode('ascii') for version in arcpy.da.ListVersions(db_string) if version.parentVersionName not in ['sde.DEFAULT',None]]
        version_QA = [version.name.encode('ascii') for version in arcpy.da.ListVersions(db_string) if version.parentVersionName == 'sde.DEFAULT' and version.name[-3:]=='_QA']
        version_default = ['sde.DEFAULT']
        arcpy.ReconcileVersions_management(file,"ALL_VERSIONS",version_QA[0],versions_children,"LOCK_ACQUIRED","ABORT_CONFLICTS","BY_ATTRIBUTE","FAVOR_TARGET_VERSION","POST","KEEP_VERSION",r"C:\Users\{}\Desktop\reconcile_folder\{}_{}.txt".format(user_name,file,version_QA[0]))
        arcpy.ReconcileVersions_management(file,"ALL_VERSIONS",version_default[0],version_QA[0],"LOCK_ACQUIRED","ABORT_CONFLICTS","BY_ATTRIBUTE","FAVOR_TARGET_VERSION","POST","KEEP_VERSION",r"C:\Users\{}\Desktop\reconcile_folder\{}_{}.txt".format(user_name,file,version_default[0]))

        with open(r"C:\Users\{}\Desktop\actual back up folder\reconcile_log.txt".format(user_name),"a") as out_file, open(r"C:\Users\{}\Desktop\reconcile_folder\{}_{}.txt".format(user_name,file,version_QA[0]),'r') as in_fileQA, open(r"C:\Users\{}\Desktop\reconcile_folder\{}_{}.txt".format(user_name,file,version_default[0]),'r') as in_fileDefault:
            out_file.write('**************\n')
            lineQA = in_fileQA.readline()
            while lineQA:
                out_file.write(lineQA)
                lineQA = in_fileQA.readline()
            out_file.write('\n')

            lineDefault = in_fileDefault.readline()
            while lineDefault:
                out_file.write(lineDefault)
                lineDefault = in_fileDefault.readline()
            out_file.write('\nDone\n')


def set_workspace():
    user_name = getpass.getuser()
    folder_path = "C:\Users\{}\AppData\Roaming\ESRI\Desktop10.4\ArcCatalog\\".format(user_name)
    return folder_path,user_name




main()

