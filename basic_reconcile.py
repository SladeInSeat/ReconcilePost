from __future__ import print_function
import arcpy
import getpass
import re
import datetime

text_match = '\[(\d+/\d+/\d+.+)]\s(Warning: Conflicts found reconciling version)\s([SDE]+\.\w+)\.'

def main():
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace,user_name = set_workspace()
    db_exclude_list = ['SDE@WebAppDev_CLUSTER.sde']
    conn_files = [file for file in arcpy.ListFiles("SDE@*") if file in db_exclude_list]
    print (conn_files)

    for file in conn_files:
        db_string = r"Database Connections\{}".format(file)
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

        with open(r"C:\Users\{}\Desktop\actual back up folder\reconcile_log.txt".format(user_name),"a") as out_file,\
             open(r"C:\Users\{}\Desktop\reconcile_folder\{}_{}.txt".format(user_name,file,version_QA[0]),'r') as in_fileQA:
             out_file.write('**************\n')
             lineQA = in_fileQA.readline()
             while lineQA:
                 out_file.write(lineQA)
                 lineQA = in_fileQA.readline()
             out_file.write('\n')

        with open(r"C:\Users\{}\Desktop\actual back up folder\reconcile_log.txt".format(user_name), "r") as infile, \
            open(r"C:\Users\{}\Desktop\finalfolder\finalfolderlog.txt".format(user_name), "a") as outfile:
            line = infile.readline()
            while line:
                match = re.search(text_match,line)
                if match:
                    print (match.group(1))
                    print (match.group(2))
                    print (match.group(3))
                    outfile.write(match.group(1))
                    outfile.write(match.group(2))
                    outfile.write(match.group(3))
                line = infile.readline()




        ''' Parse logs here. search for failed reconciles/posts, save line of failures, append to new file or dict of db: bad version, stop reconciling of QA to Default
            there is a race condition here bc the conflict is only identified after the 1st version posts (unless someone has edited QA, naughty!)'''

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



        with open(r"C:\Users\{}\Desktop\actual back up folder\reconcile_log.txt".format(user_name),"a") as out_file,\
             open(r"C:\Users\{}\Desktop\reconcile_folder\{}_{}.txt".format(user_name, file, version_default[0]),'r')\
                     as in_fileDefault:
            lineDefault = in_fileDefault.readline()
            while lineDefault:
                out_file.write(lineDefault)
                lineDefault = in_fileDefault.readline()
            out_file.write('\nDone\n')


def set_workspace():
    user_name = getpass.getuser()
    folder_path = r"C:\Users\{}\AppData\Roaming\ESRI\Desktop10.4\ArcCatalog\\".format(user_name)
    return folder_path,user_name




main()

