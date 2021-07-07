'''
   Copyright (c) 2019 Jack Farley
   This file is part of iTunes_Backup_Reader
   Usage or distribution of this software/code is subject to the
   terms of the GNU GENERAL PUBLIC LICENSE.
   writer.py
   ------------
'''
import os
import sqlite3
import csv

'''Opens a database'''
def OpenDb(inputPath, logger):
    try:
        conn = sqlite3.connect(inputPath)
        logger.debug ("Opened database: " + inputPath + " successfully")
        return conn
    except Exception as ex:
        logger.exception ("Failed to open database: " + inputPath + " Exception was: " + str(ex))
    return None

'''Write to a plain ole txt file'''
def writeToTxt(backup_list, application_list, output_file, logger):
    output = open(output_file, "w+")

    output.write("DEVICE BACKUP INFO\n" +
                 "Device Name: \t" + str(backup_list[0]) + "\n" +
                 "Product Name: \t" + str(backup_list[1]) + "\n" +
                 "Product Model: \t" + str(backup_list[2]) + "\n" +
                 "Phone Number: \t" + str(backup_list[3]) + "\n" +
                 "iOS Version: \t" + str(backup_list[4]) + "\n" +
                 "Backup Completetion: \t" + str(backup_list[5]) + "\n" +
                 "Backup Complete Write: \t" + str(backup_list[6]) + "\n" +
                 "Users & Computers Connected to: \t\n" + str(backup_list[7]) + "\n" +
                 "Is Passcode Set: \t" + str(backup_list[8]) + "\n" +
                 "Is Encrypted: \t" + str(backup_list[9]) + "\n" +
                 "GUID: \t" + str(backup_list[10]) + "\n" +
                 "ICCID: \t" + str(backup_list[11]) + "\n" +
                 "IMEI: \t" + str(backup_list[12]) + "\n" +
                 "MEID: \t" + str(backup_list[13]) + "\n" +
                 "Serial Number: \t" + str(backup_list[14]) + "\n" +
                 "Is Full Backup: \t" + str(backup_list[15]) + "\n" +
                 "Version: \t" + str(backup_list[16]) + "\n" +
                 "iTunes Version: \t" + str(backup_list[17]) +  "\n\n")

    output.write("\nAPPLICATIONS INSTALLED\n")
    for app in application_list:
        output.write("App Name: \t" + str(app[2]) + "\n" +
                     "Device Installed on: \t" + str(app[0]) + "\n" +
                     "Purchase Date: \t" + str(app[5]) + "\n" +
                     "Apple ID: \t" + str(app[3]) + "\n" +
                     "Apple ID Name: \t" + str(app[4]) + "\n" +
                     "Device Installed on Serial Number: \t" + str(app[1]) + "\n" +
                     "Is Possibly Sideloaded: \t" + str(app[6]) + "\n" +
                     "App Version: \t" + str(app[7]) + "\n" +
                     "Is Auto Downloaded: \t" + str(app[8]) + "\n" +
                     "Is Purchased Redownloaded: \t" + str(app[9]) + "\n" +
                     "Publisher: \t" + str(app[10]) + "\n" +
                     "Full App Name: \t" + str(app[11]) + "\n\n"
                     )
    output.close()

'''Write to an SQLite database'''
def writeToDb(backup_list, application_list, output_file, logger):
    '''Opens database for iTunes_Backups'''
    if os.path.exists(output_file):
        os.remove(output_file)
    conn = OpenDb(output_file, logger)
    c = conn.cursor()

    '''Creates database table for device data'''
    createBackQuery = "CREATE TABLE Device_Data ( Device_Name TEXT, Product_Name TEXT, " \
                      "Product_Model TEXT, Phone_Number TEXT, " \
                      "iOS_Version TEXT, Last_Backup_Completion DATE, " \
                      "Last_Backup_Write_Completed DATE, User_Computers TEXT, Passcode_Set BOOL, Encrypted BOOL, " \
                      "GUID TEXT, ICCID TEXT, IMEI TEXT, MEID TEXT, Serial_Num TEXT," \
                      "Full_Backup BOOL, Version TEXT, iTunes_Version TEXT);"
    try:
        c.execute(createBackQuery)
    except Exception as ex:
        logger.exception("Failed to execute query: " + createBackQuery + "\nException was: " + str(ex))

    try:
        '''Inserts for device data'''
        conn.executemany('''INSERT INTO Device_Data(Device_Name, Product_Name, Product_Model, Phone_Number, 
                iOS_Version, Last_Backup_Completion, 
                Last_Backup_Write_Completed, User_Computers, Passcode_Set, Encrypted, 
                GUID, ICCID, IMEI, MEID, Serial_Num,
                Full_Backup, Version, iTunes_Version) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (backup_list,))
    except Exception as ex:
        logger.exception("Error filling Backups table. Error was: " + str(ex))

    '''Creates database table for installed apps'''
    createAppQuery = "CREATE TABLE Applications (Device_Name TEXT, Device_SN TEXT, App_Name TEXT, AppleID TEXT, " \
                     "User_Full_Name TEXT, Purchase_Date DATE, Is_Possibly_Sideloaded BOOL, App_Version TEXT, Is_Auto_Download BOOL, " \
                     "Is_Purchased_Redownload BOOL, Publisher TEXT, Full_App_Name TEXT);"

    try:
        c.execute(createAppQuery)
    except Exception as ex:
        logger.exception("Failed to execute query: " + createAppQuery + "\nException was: " + str(ex))

    try:
        conn.executemany('''INSERT INTO Applications(Device_Name, Device_SN, App_Name, AppleID, 
                         User_Full_Name, Purchase_Date, Is_Possibly_Sideloaded, App_Version, Is_Auto_Download, 
                         Is_Purchased_Redownload, Publisher, Full_App_Name) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                         (application_list),)

    except Exception as ex:
        logger.exception("Error filling Applications table. Error was: " + str(ex))


    '''Closes iTunes_Backups.db'''
    conn.commit()
    conn.close()

'''Write to 2 different CSV files for applications and backup metadata'''
def writeToCsv(backup_list, application_list, output_file, logger):

    backup_csv = output_file + "Backups.csv"
    app_csv = output_file + "Applications.csv"


    with open(backup_csv, 'w', newline='') as backup_csv_handle:
        columns = ["Device_Name", "Product_Name", "Product_Model", "Phone_Number",
                "iOS_Version", "Last_Backup_Completion",
                "Last_Backup_Write_Completed", "User_Computers", "Passcode_Set", "Encrypted",
                "GUID", "ICCID", "IMEI", "MEID", "Serial_Num",
                "Full_Backup", "Version", "iTunes_Version"]
        wr = csv.writer(backup_csv_handle, quoting=csv.QUOTE_ALL)
        wr.writerows([columns, backup_list])

    with open(app_csv, 'w', newline='') as app_csv_handle:
        columns = ["Device_Name", "Device_SN", "App_Name", "AppleID", "User_Full_Name", "Purchase_Date",
                   "Is_Possibly_Sideloaded", "App_Version", "Is_Auto_Download", "Is_Purchased_Redownload",
                   "Publisher", "Full_App_Name"]
        wr = csv.writer(app_csv_handle, quoting=csv.QUOTE_ALL)
        wr.writerow(columns)
        wr.writerows(application_list)


def startWrite(backup_list, application_list, output_dir, out_type, logger):


    '''Write to TXT'''
    if out_type == "txt":
        text_file = "Device_" +  backup_list[14] + "_Output.txt"
        output_file = os.path.join(output_dir, text_file)
        logger.debug("Starting output to " + output_file)
        try:
            writeToTxt(backup_list, application_list, output_file, logger)
            logger.debug("Finished output to " + output_file)
        except Exception as ex:
            logger.exception("Could not write output to " + output_file + " Exception was: " + str(ex))

    '''Write to DB'''
    if out_type == "db":
        text_file = "Device_" + backup_list[14] + "_Output.db"
        output_file = os.path.join(output_dir, text_file)
        logger.debug("Starting output to " + output_file)
        try:
            writeToDb(backup_list, application_list, output_file, logger)
            logger.debug("Finished output to " + output_file)
        except Exception as ex:
            logger.exception("Could not write output to " + output_file + " Exception was: " + str(ex))

    '''Write to CSV'''
    if out_type == "csv":
        logger.debug("Starting  output")
        text_file = "Device_" + backup_list[14] + "_Output_"
        output_file = os.path.join(output_dir, text_file)
        try:
            writeToCsv(backup_list, application_list, output_file, logger)
            logger.debug("Finished output to " + output_file)
        except Exception as ex:
            logger.exception("Could not write CSV output. Exception was: " + str(ex))

