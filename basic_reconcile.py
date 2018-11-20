from __future__ import print_function
import arcpy
import getpass
import re
import StringIO
import smtplib
import datetime
import traceback

#   Regular expression match used on logs from reconcile/post tool from ESRI, match == failure to reconcile
text_match = r'\[(\d+/\d+/\d+.+)]\s(Warning.+)\s([SDE]+\.\w+)\.'
temp_report = StringIO.StringIO()


def main():
    try:
        arcpy.env.overwriteOutput = True
        user_name = "GIS_Admin"
        arcpy.env.workspace = r"C:\Users\{}\AppData\Roaming\ESRI\Desktop10.4\ArcCatalog\\".format(user_name)
        db_exclude = ['SDE@Address_CLUSTER.sde', 'SDE@WebAppDev_CLUSTER.sde']
        version_exclude = ['"CITYHALL\\CDGLASS".cglass',  # Expliciit list of versions to not reconclie
                           '"CITYHALL\\MORIO".addr_101618',
                           '"CITYHALL\\MORIO".BLDG_101618',
                           '"CITYHALL\\MORIO".DAZ',
                           '"CITYHALL\\MORIO".mow_contractor_082918',
                           '"CITYHALL\MORIO".WTP_102918',
                           'SDE.mowing_091718',
                           '"CITYHALL\\TGRAHAM".GRAHAM_SANITARY',
                           '"CITYHALL\\TGRAHAM".TGRAHAM_TELECOM',
                           '"CITYHALL\\TGRAHAM".T_GRAHAM_STORM',
                           '"CITYHALL\\TGRAHAM".TGRAHAM_WATER',
                           '"CITYHALL\\ACASTILLO".OandFlorida',
                           '"CITYHALL\\SEDGE".Edge_Sanitary',
                           '"CITYHALL\\SEDGE".Edge_Stormwater',
                           '"CITYHALL\\SEDGE".Edge_Fiber',
                           '"CITYHALL\\SEDGE".Edge_Water',
                           'CEICHENMULLER.Ceichenmuller',
                           'SDE.Editor_WoodlawnCemetery_App']
        static_reconcilelist = ['GISADMIN.Address_QA',  # explicit list of versions to reconcile
                                'GISADMIN.CIP_QA',
                                'GISADMIN.Citizen_QA',
                                'GISADMIN.Editor_BuildingElevation',
                                'GISADMIN.Editor_CityProperties',
                                'GISADMIN.Editor_GreenBusiness_App',
                                'GISADMIN.Editor_HCD',
                                'GISADMIN.Editor_Historic',
                                'GISADMIN.Editor_ROWIrrigation_App',
                                'GISADMIN.Editor_CIP',
                                'GISADMIN.Editor_ROWPermits_App',
                                'GISADMIN.Editor_VehicleCharging_App',
                                'GISADMIN.Editor_TrafficCalming_App',
                                'GISADMIN.Editor_StreetLights',
                                'GISADMIN.Elevation_QA',
                                'GISADMIN.GPS_Collections',
                                'GISADMIN.HistoricStructures_Editor',
                                'GISADMIN.Land_QA',
                                'GISADMIN.Parks_QA',
                                'GISADMIN.Planning_QA',
                                'GISADMIN.PublicLandSurvey_QA',
                                'GISADMIN.PublicSafety_QA',
                                'GISADMIN.PublicWorksGrid',
                                'GISADMIN.PublicWorks_QA',
                                'GISADMIN.Sanitary_QA',
                                'GISADMIN.Storm_QA',
                                'GISADMIN.Telecom_QA',
                                'GISADMIN.Transportation_QA',
                                'GISADMIN.Water_QA',
                                'GISADMIN.Watershed_QA',
                                'sde.DEFAULT']

        conn_files = [file for file in arcpy.ListFiles("SDE@*") if file not in db_exclude]
        print(conn_files)

        for file in conn_files:
            arcpy.AcceptConnections(file, False)
            arcpy.DisconnectUser(file, "ALL")

            print("file: {}".format(file))
            reconcile_errors = False
            versions_children = [version.name.encode('ascii') for version in arcpy.da.ListVersions(file)
                                 if version.parentVersionName not in ['sde.DEFAULT', None]
                                 and version.name in static_reconcilelist]
            version_QA = [version.name.encode('ascii') for version in arcpy.da.ListVersions(file)
                          if version.parentVersionName == 'sde.DEFAULT'
                          and version.name[-3:] == '_QA' and version.name in static_reconcilelist]
            version_default = ['sde.DEFAULT']

            print("children: {}\nQA: {}\ndefault: {}".format(versions_children, version_QA, version_default))

            if len(versions_children) > 0:
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
                                                   r"C:\Jobs\reconcile_post\reconcile_logs\{}_{}.txt".format(file,
                                                                                                             version_QA[
                                                                                                                 0]))

                with open(r"C:\Jobs\reconcile_post\reconcile_logs\{}_{}.txt".format(file, version_QA[0]),
                          'r') as in_file:
                    line = in_file.readline()
                    while line:
                        match = re.search(text_match, line)
                        if match:
                            reconcile_errors = True
                            temp_report.write("\n{}\n".format(file))
                            temp_report.write("\t{}\n".format(line))
                        line = in_file.readline()
            else:
                print('not reconciling {}, len of versions_children was 0'.format(file))

            if reconcile_errors == False and (len(version_QA) > 0):
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
                                                   r"C:\Jobs\reconcile_post\reconcile_logs\{}_{}.txt".format(file,
                                                                                                             version_default[
                                                                                                                 0]))

                with open(r"C:\Jobs\reconcile_post\reconcile_logs\{}_{}.txt".format(file, version_default[0]),
                          'r') as in_file:
                    line = in_file.readline()
                    while line:
                        match = re.search(text_match, line)
                        if match:
                            temp_report.write("\n{}\n".format(file))
                            temp_report.write("\t{}\n".format(line))
                        line = in_file.readline()
            else:
                print('did not reconcile bc errors or no QA')
                temp_report.write(file + " \ndid not reconcile either because of errors (listed above)"
                                         " or No QA version found\n\n")

        final_report = temp_report.getvalue()
        print("printing final_report: \n", final_report)

        if len(final_report) > 0:
            print("final_report has lenght, emailing")
            today = datetime.datetime.now().strftime("%m-%d-%Y")
            with open(r"C:\Jobs\reconcile_post\reconcile_logs\report_{}.txt".format(today), "w") as outfile:
                outfile.write(final_report)
            sendMail("Reconcile Post report", ["JSSawyer@wpb.org,JJudge@wpb.org"], "Reconcile Post report",
                     final_report)
        else:
            print("final report no length, ending")

    except Exception as E:
        log = traceback.format_exc()
        print('Exception: {}'.format(log))
        sendMail("Reconcile script failure report", ["JSSawyer@wpb.org,JJudge@wpb.org"],
                 "An error occurred, here is the log; ", log)


    finally:
        temp_report.close()
        for file in conn_files:
            arcpy.AcceptConnections(file, True)


def set_workspace():
    user_name = getpass.getuser()
    folder_path = r"C:\Users\{}\AppData\Roaming\ESRI\Desktop10.4\ArcCatalog\\".format(user_name)
    return folder_path, user_name


def sendMail(subject_param, sendto_param, body_text_param, report_param):
    today = datetime.datetime.now().strftime("%m-%d-%Y")
    subject = "{} {}".format(subject_param, today)
    sender = 'scriptmonitorwpb@gmail.com'
    sender_pw = 'Bibby1997'
    server = 'smtp.gmail.com'
    body_text = "From: {0}\r\nTo: {1}\r\nSubject: {2}\r\n" \
                "\n{3}\n\t{4}" \
        .format(sender, sendto_param, subject, body_text_param, report_param)

    gmail = smtplib.SMTP(server, 587)
    gmail.starttls()
    gmail.login(sender, sender_pw)
    gmail.sendmail(sender, sendto_param, body_text)
    gmail.quit()


main()

