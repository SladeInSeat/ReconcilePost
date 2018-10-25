from __future__ import print_function
import arcpy
import getpass
import re
import StringIO
import smtplib
import datetime


""" This is a god awful mess that needs to be put into functions or objects for clarity"""

text_match = '\[(\d+/\d+/\d+.+)]\s(Warning: Conflicts found reconciling version)\s([SDE]+\.\w+)\.'


def main():
    try:
        arcpy.env.overwriteOutput = True
        arcpy.env.workspace,user_name = set_workspace()
        db_exclude = ['SDE@WebAppDev_CLUSTER.sde']
        version_exclude = list()
        conn_files = [file for file in arcpy.ListFiles("SDE@*") if file in db_exclude]
        print (conn_files)

        for file in conn_files:
            arcpy.AcceptConnections(file, False)
            arcpy.DisconnectUser(file,"ALL")

            db_string = r"Database Connections\{}".format(file)
            reconcile_errors = False
            versions_children = [version.name.encode('ascii') for version in arcpy.da.ListVersions(db_string) if version.parentVersionName not in ['sde.DEFAULT',None]]
            version_QA = [version.name.encode('ascii') for version in arcpy.da.ListVersions(db_string) if version.parentVersionName == 'sde.DEFAULT' and version.name[-3:]=='_QA']
            version_default = ['sde.DEFAULT']
            temp_report = StringIO.StringIO()


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

            with open(r"C:\Users\{}\Desktop\reconcile_folder\{}_{}.txt".format(user_name,file,version_QA[0]),'r') as in_file:
                line = in_file.readline()
                while line:
                    match = re.search(text_match,line)
                    if match:
                        reconcile_errors = True
                        temp_report.write(file + "\n")
                        temp_report.write("\t" + line + "\n")
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
                          'r') as in_file:
                    line = in_file.readline()
                    while line:
                        match = re.search(text_match, line)
                        if match:
                            temp_report.write(file + "\n")
                            temp_report.write("\t" + line + "\n")
                        line = in_file.readline()

        final_report = temp_report.getvalue()

        if len(final_report) > 0:
            print ("len is > 0")
            with open(r"C:\Users\{}\Desktop\finalfolder\finalfolderlog.txt".format(user_name), "a") as outfile:
                outfile.write(final_report)

            today = datetime.datetime.now().strftime("%d-%m-%Y")
            subject = 'Reconcile Post report ' + today
            sendto = "jssawyer@wpb.org"
            sender = 'scriptmonitorwpb@gmail.com'
            sender_pw = "Bibby1997"
            server = 'smtp.gmail.com'
            body_text = "From: {0}\r\nTo: {1}\r\nSubject: {2}\r\n" \
                        "\n{3}".format(sender, sendto, subject, final_report)

            gmail = smtplib.SMTP(server, 587)
            gmail.starttls()
            gmail.login(sender, sender_pw)
            gmail.sendmail(sender, sendto, body_text)
            gmail.quit()




    except Exception as E:
        print (E)
    finally:
        print ("finally")
        temp_report.close()
        for file in conn_files:
            arcpy.AcceptConnections(file, True)


def set_workspace():
    user_name = getpass.getuser()
    folder_path = r"C:\Users\{}\AppData\Roaming\ESRI\Desktop10.4\ArcCatalog\\".format(user_name)
    return folder_path,user_name




main()

