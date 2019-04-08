'''
   Copyright (c) 2019 Jack Farley
   This file is part of iTunesBackupAnalyzer
   Usage or distribution of this software/code is subject to the
   terms of the MIT License.
   iTunes_Backup_Analyzer.py
   ------------
'''
from __future__ import unicode_literals
from __future__ import print_function
import os
import logging
import argparse
from biplist import *
import sqlite3
import glob

'''Class to organize backup data'''
class iDeviceBackup:
    def __init__(self, Device_Name, Product_Name, Product_Model, Phone_Num, iOS_Vers, First_Backup_UTC,
                 Last_Backup_UTC, Passcode_Set, Encrypted, GUID, ICCID, IMEI, MEID, SN, Full_Backup, Version, iTunes_Vers):

        self.Device_Name = Device_Name
        self.Product_Name = Product_Name
        self.Product_Model = Product_Model
        self.Phone_Num = Phone_Num
        self.iOS_Vers = iOS_Vers
        self.First_Backup_UTC = First_Backup_UTC
        self.Last_Backup_UTC = Last_Backup_UTC
        self.Passcode_Set = Passcode_Set
        self.Encrypted = Encrypted
        self.GUID = GUID
        self.ICCID = ICCID
        self.IMEI = IMEI
        self.MEID = MEID
        self.SN = SN
        self.Full_Backup = Full_Backup
        self.Version = Version
        self.iTunes_Vers = iTunes_Vers

'''Class to organize Application data'''
class Applications:
    def __init__(self, Device_Installed, Device_SN, App_Name, AppleID, AppleID_Name, Purchase_Date, App_Version,
                 Is_Auto_Downloaded, Is_Purchased_Redownload, Publisher, Full_App_Name):

        self.Device_Installed = Device_Installed
        self.Device_SN = Device_SN
        self.App_Name = App_Name
        self.AppleID = AppleID
        self.AppleID_Name = AppleID_Name
        self.Purchase_Date = Purchase_Date
        self.App_Version = App_Version
        self.Is_Auto_Downloaded = Is_Auto_Downloaded
        self.Is_Purchased_Redownload = Is_Purchased_Redownload
        self.Publisher = Publisher
        self.Full_App_Name = Full_App_Name


def PrintAll(backups, applications, output):

    '''Create list of backup data to be sent to SQL Writer'''
    backup_list = []
    for bkp in backups:
        bkps_item = [ bkp.Device_Name, bkp.Product_Name, bkp.Product_Model, bkp.Phone_Num,
                      bkp.iOS_Vers, bkp.First_Backup_UTC, bkp.Last_Backup_UTC, bkp.Passcode_Set,
                      bkp.Encrypted, bkp.GUID, bkp.ICCID, bkp.IMEI, bkp.MEID,
                      bkp.SN, bkp.Full_Backup, bkp.Version, bkp.iTunes_Vers,
                     ]
        backup_list.append(bkps_item)

    '''Create list of application data to be sent to SQL Writer'''
    application_list = []
    for app in applications:
        apps_item = [ app.Device_Installed, app.Device_SN, app.App_Name, app.AppleID, app.AppleID_Name, app.Purchase_Date,
                      app.App_Version, app.Is_Auto_Downloaded, app.Is_Purchased_Redownload, app.Publisher,
                      app.Full_App_Name,]
        application_list.append(apps_item)

    sqlWriter(backup_list, application_list, output)


def OpenDb(inputPath):
    try:
        conn = sqlite3.connect(inputPath)
        logging.debug ("Opened database successfully")
        return conn
    except:
        logging.exception ("Failed to open database")
    return None

'''Checks for plist files in backups'''
def checkPlists(folder, allBackups):

    if os.path.isdir(folder):
        if os.path.exists(os.path.join(folder, "Info.plist")):
            logging.debug("Found Info.plist")
        else:
            logging.exception("Could not find Info.Plist in: ", folder)

        if os.path.exists(os.path.join(folder, "Manifest.plist")):
            logging.debug("Found Manifest.plist")
        else:
            logging.exception("Could not find Manifest.Plist in: ", folder)

        if os.path.exists(os.path.join(folder, "Status.plist")):
            logging.debug("Found Status.plist")
        else:
            logging.exception("Could not find Status.Plist in: ", folder)

        '''Checks for existence of output directory'''
        if os.path.isdir(folder):
            allBackups.append(folder)
        else:
            logging.exception("Error with output directory, is it valid?")

    else:
        logging.exception("Error with input directory, is it valid?")

'''Checks the iTunes backup folders for legitimacy'''
def checkInput(inputDir, allBackups):
    if type(inputDir) == str:
        logging.debug("Single folder given... Checking for valid backup")
        checkPlists(inputDir, allBackups)
    if type(inputDir) == list:
        logging.debug("List of folders given... Checking for valid backups")
        for child in inputDir:
            checkPlists(child, allBackups)


'''Gets folder for parsing the iTunes backups'''
def get_argument():
    parser = argparse.ArgumentParser(description='Utility to parse out iTunes Backup plists and DB')

    '''Gets paths to necessary folders'''
    parser.add_argument('-i', '--inputDir', required=True, type=str, nargs='+', dest='inputDir', help='Path to iTunes Backup Folder')
    parser.add_argument('-o', '--outputDir', required=True, type=str, nargs='+', dest='outputDir', help='Directory to store results')
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-K", "--Kape", help="Use this flag for Kape Tool, don't use", action="store_true")

    args = parser.parse_args()

    '''Sets up logger'''
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M')
    else:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M')

    '''Checks if Kape is being used'''
    if args.Kape:
        logging.debug("Kape flag used")
        args.inputDir[0] = glob.glob(args.inputDir[0] + "\\C\\Users\\*\\AppData\\Roaming\\Apple Computer\\Mobilesync\\Backup\\*")

    '''Dictionary to paths of all backup folders to check'''
    allBackups = []
    checkInput(args.inputDir[0], allBackups)
    logging.info(str(len(allBackups)) + " Backups found!")
    return [allBackups, args.outputDir[0]]



'''Reads the three plists for data pertaining to individual backups'''
def ReadBackupPlists(info_plist, status_plist, manifest_plist, backups):

    lockdown = manifest_plist.get('Lockdown', {})
    deviceName = info_plist.get('Device Name', '')

    bkps = iDeviceBackup(
        deviceName,
        info_plist.get('Product Name', ''),
        info_plist.get('Product Type', ''),
        info_plist.get('Phone Number', ''),
        lockdown.get('ProductVersion', ''),
        manifest_plist.get('Date', ''),
        info_plist.get('Last Backup Date', ''),
        manifest_plist.get('WasPasscodeSet', ''),
        manifest_plist.get('IsEncrypted', ''),
        info_plist.get('GUID', ''),
        info_plist.get('ICCID', ''),
        info_plist.get('IMEI', ''),
        info_plist.get('MEID', ''),
        info_plist.get('Serial Number', ''),
        status_plist.get('IsFullBackup', ''),
        status_plist.get('Version', ''),
        info_plist.get('iTunes Version', ''))
    backups.append(bkps)

'''Really sketchy way of, quote on quote, parsing the SINF to find the full name'''
def sinfHelper(data):

    '''Creates bytearrays for finding magic key and full name'''
    byteArr = bytearray(data)
    userByteArr = bytearray()

    '''Looks for magic keyword of name'''
    magicOffset = byteArr.find(b"name")
    magic= byteArr[magicOffset:magicOffset+4]
    if magic == b"name":
        '''Finds characters until null terminator, appends to userByteArr'''
        for x in range (int(magicOffset+4), len(data)):
            if (data[x]) == 0:
                break
            else:
                char =  (data[x])
                userByteArr.append(char)

        userName = userByteArr.decode()
        return userName
    else:
        return ""


def ReadApplicationPlists(info_plist, singleApplication, applications):
    '''This is all apps installed'''
    singleApp = info_plist.get("Applications")

    '''Now we single it down to the specific app we are looking for, which is another embedded plist'''
    appPlist = singleApp.get(singleApplication, {})
    iTunesBinaryPlist = appPlist.get('iTunesMetadata', {})
    iTunesPlist = readPlistFromString(iTunesBinaryPlist)

    '''Find Apple ID & Purchase Date'''
    downloadInfo = iTunesPlist.get('com.apple.iTunesStore.downloadInfo', {})
    accountInfo = downloadInfo.get('accountInfo', {})

    '''Find full name of person associated with Apple ID from ApplicationSINF'''
    binarySinf = appPlist.get('ApplicationSINF', {})

    '''Gets users full name from SINF'''
    name = sinfHelper(binarySinf)
    if name == "":
        logging.debug("No full name found for: " + iTunesPlist.get('itemName', '') + " This means it could be sideloaded")

    apps = Applications(
        info_plist.get('Device Name', ''),
        info_plist.get('Serial Number', ''),
        iTunesPlist.get('itemName', ''),
        accountInfo.get('AppleID', ''),
        name,
        downloadInfo.get('purchaseDate', ''),
        iTunesPlist.get('bundleVersion', ''),
        iTunesPlist.get('is-auto-download', ''),
        iTunesPlist.get('is-purchased-redownload', ''),
        iTunesPlist.get('artistName', ''),
        iTunesPlist.get('softwareVersionBundleId', ''))

    applications.append(apps)


'''Reads data from each plist supplied'''
def ReadDataFromPlists(info_plist, status_plist, manifest_plist, backups, applications):

    if manifest_plist.get('IsEncrypted', ''):
        logging.info("The device: \'" + info_plist.get('Device Name', '')  + "\' iTunes Backup is encrypted!")

    ReadBackupPlists(info_plist, status_plist, manifest_plist, backups)


    allApps = info_plist.get('Applications', '')
    for singleApps in allApps:
        ReadApplicationPlists(info_plist, singleApps, applications)


def sqlWriter(backups, applications, output):

    '''Opens database for iTunes_Backups'''
    backupDb = os.path.join(output, "iTunes_Backups.db")
    if os.path.exists(backupDb):
        os.remove(backupDb)
    conn = OpenDb(backupDb)
    c = conn.cursor()

    '''Creates database table for backups'''
    createBackQuery = "CREATE TABLE Backups ( Device_Name TEXT, Product_Name TEXT, Product_Model TEXT, Phone_Number TEXT, "\
			"iOS_Version TEXT, First_Backup_UTC DATE, "\
			"Last_Backup_UTC DATE, Passcode_Set BOOL, Encrypted BOOL, "\
			"GUID TEXT, ICCID TEXT, IMEI TEXT, MEID TEXT, Serial_Num TEXT,"\
			"Full_Backup BOOL, Version TEXT, iTunes_Version TEXT);"
    try:
        c.execute(createBackQuery)
    except Exception as ex:
        logging.exception("Failed to execute query: " + createBackQuery + "\nException was: " + str(ex))

    try:
        conn.executemany('''INSERT INTO Backups(Device_Name, Product_Name, Product_Model, Phone_Number, 
            iOS_Version, First_Backup_UTC, 
            Last_Backup_UTC, Passcode_Set, Encrypted, 
            GUID, ICCID, IMEI, MEID, Serial_Num,
            Full_Backup, Version, iTunes_Version) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', backups)
    except Exception as ex:
        logging.exception("Error filling Backups table. Error was: " + str(ex))


    '''Creates database table for installed apps'''
    createAppQuery = "CREATE TABLE Applications (Device_Name TEXT, Device_SN TEXT, App_Name TEXT, AppleID TEXT, " \
                     "User_Full_Name TEXT, Purchase_Date DATE, App_Version TEXT, Is_Auto_Download BOOL, " \
                     "Is_Purchased_Redownload BOOL, Publisher TEXT, Full_App_Name TEXT);"

    try:
        c.execute(createAppQuery)
    except Exception as ex:
        logging.exception("Failed to execute query: " + createAppQuery + "\nException was: " + str(ex))

    try:
        conn.executemany('''INSERT INTO Applications(Device_Name, Device_SN, App_Name, AppleID, 
                     User_Full_Name, Purchase_Date, App_Version, Is_Auto_Download, 
                     Is_Purchased_Redownload, Publisher, Full_App_Name) VALUES (?,?,?,?,?,?,?,?,?,?,?)''', applications)

    except Exception as ex:
        logging.exception("Error filling Applications table. Error was: " + str(ex))


    '''Closes iTunes_Backups.db'''
    conn.commit()
    conn.close()


def main():
    args = get_argument()

    backups = []
    applications = []

    for folders in args[0]:
        '''Paths for the plists'''
        status_plist_path = os.path.join(folders , "Status.plist")
        manifest_plist_path = os.path.join(folders , "Manifest.plist")
        info_plist_path = os.path.join(folders , "Info.plist")

        try:
            info_plist = readPlist(info_plist_path)
        except:
            logging.exception("Failed to read Info.plist from path {}".format(info_plist_path))
            info_plist = {}
        try:
            status_plist = readPlist(status_plist_path)
        except:
            logging.exception("Failed to read Status.plist from path {}".format(status_plist_path))
            status_plist = {}
        try:
            manifest_plist = readPlist(manifest_plist_path)
        except:
            logging.exception("Failed to read Manifest.plist from path {}".format(manifest_plist_path))
            manifest_plist = {}


        ReadDataFromPlists(info_plist, status_plist, manifest_plist, backups, applications)

        PrintAll(backups, applications, args[1])

if __name__ == "__main__":
    main()
