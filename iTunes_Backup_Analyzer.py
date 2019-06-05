'''
   Copyright (c) 2019 Jack Farley
   This file is part of iTunesBackupAnalyzer
   Usage or distribution of this software/code is subject to the
   terms of the GNU GENERAL PUBLIC LICENSE.
   iTunes_Backup_Analyzer.py
   ------------
'''
from __future__ import unicode_literals
from __future__ import print_function
import os
import logging
import argparse
from biplist import *
import glob
from manifestParser import OpenDb, readManiDb, createFolder

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
    def __init__(self, Device_Installed, Device_SN, App_Name, AppleID, AppleID_Name, Purchase_Date,
                 Is_Possibly_Sideloaded, App_Version, Is_Auto_Downloaded, Is_Purchased_Redownload, Publisher,
                 Full_App_Name):

        self.Device_Installed = Device_Installed
        self.Device_SN = Device_SN
        self.App_Name = App_Name
        self.AppleID = AppleID
        self.AppleID_Name = AppleID_Name
        self.Purchase_Date = Purchase_Date
        self.Is_Possibly_Sideloaded = Is_Possibly_Sideloaded
        self.App_Version = App_Version
        self.Is_Auto_Downloaded = Is_Auto_Downloaded
        self.Is_Purchased_Redownload = Is_Purchased_Redownload
        self.Publisher = Publisher
        self.Full_App_Name = Full_App_Name


def PrintAll(backups, applications, userComps, output):

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
                      app.Is_Possibly_Sideloaded, app.App_Version, app.Is_Auto_Downloaded, app.Is_Purchased_Redownload,
                      app.Publisher, app.Full_App_Name,]
        application_list.append(apps_item)

    sqlWriter(backup_list, application_list, userComps, output)


'''Checks for plist files and DB in backups'''
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

        if os.path.exists(os.path.join(folder, "Manifest.db")):
            logging.debug("Found Manifest.db")
        else:
            logging.exception("Could not find Manifest.db in: ", folder)

        '''Checks for existence of output directory'''
        if os.path.isdir(folder):
            allBackups.append(folder)
        else:
            logging.exception("Error with output directory, is it valid?")

    else:
        logging.exception("Error with input directory " + folder + " is it valid?")

'''Checks the iTunes backup folders for legitimacy'''
def checkInput(inputDir, allBackups):
    if type(inputDir) == str:
        logging.debug("Checking for valid backup")
        checkPlists(inputDir, allBackups)



'''Gets folder for parsing the iTunes backups'''
def get_argument():



    parser = argparse.ArgumentParser(description='Utility to parse out iTunes Backups')

    '''Gets paths to necessary folders'''
    parser.add_argument("-i", '--inputDir', required=True, type=str, nargs='+', dest='inputDir',
                        help='Path to iTunes Backup Folder')
    parser.add_argument("-o", '--outputDir', required=False, type=str, nargs='+', dest='outputDir',
                        help='Directory to store results')
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-K", "--kape", help="Flag for KAPE Tool, don't use", action="store_true")
    parser.add_argument("-R", "--recreate", help="Tries to recreate folder structure for unencrypted backups",
                        action="store_true")


    args = parser.parse_args()
    users = []

    '''Sets up output path'''
    outputDir = args.outputDir[0] + '\\iTunesBackups'
    createFolder(outputDir)

    '''Log output path'''
    logOut = outputDir + '\\iTunes_Backup_Analyzer.log'
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    '''Sets up logger'''
    if args.verbose:
        logging.basicConfig(handlers=[logging.StreamHandler(), logging.FileHandler(logOut)], level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M')

    else:
        logging.basicConfig(handlers=[logging.StreamHandler(), logging.FileHandler(logOut)], level=logging.INFO,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M')

    logging.debug("Starting iTunes_Backup_Analyzer")

    '''Checks if Kape is being used'''
    if args.kape:
        logging.debug("Kape flag used")

        originalInPath = args.inputDir[0]
        origLen = len(originalInPath)

        args.inputDir[0] = glob.glob(args.inputDir[0]
                                     + "\\*\\Users\\*\\AppData\\Roaming\\Apple Computer\\Mobilesync\\Backup\\*")
        rawUserStrings = args.inputDir[0]

        '''Gets all users to create subdirectories for each user'''
        for items in rawUserStrings:
            '''Gets all users to create subdirectories for each user'''
            singleUser = items[origLen:]
            singleUser = singleUser[singleUser.find(originalInPath) + 1:singleUser.find("\\AppData")]
            singleUser = singleUser[singleUser.find("Users") + 6:]
            users.append(singleUser)

            '''Dictionary to paths of all backup folders to check'''
            allBackups = []
            checkInput(items, allBackups)
        return [rawUserStrings, outputDir, args.recreate, users]



    else:
        '''Dictionary to paths of all backup folders to check'''
        allBackups = []
        checkInput(args.inputDir[0], allBackups)
        return [allBackups, outputDir, args.recreate, users]



'''Reads the three plists for data pertaining to individual backups'''
def ReadBackupPlists(info_plist, status_plist, manifest_plist, backups):

    '''Reads plist inside Lockdown'''
    lockdown = manifest_plist.get('Lockdown', {})

    bkps = iDeviceBackup(
        info_plist.get('Device Name', ''),
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



'''Really sketchy way of, quote on quote, parsing the iTunes Prefs FRPD to find last 3 users/machines connected to'''
def frpdHelper(data):

    '''Array to store usernames and computers'''
    userComps = []

    '''Creates bytearrays for finding magic key and full name'''
    byteArr = bytearray(data)
    userByteArr = bytearray()

    '''The bytes here are always 88 bytes before the start of host usernames'''
    magicOffset = byteArr.find(b'\x01\x01\x80\x00\x00')
    magic = byteArr[magicOffset:magicOffset + 5]

    if magic == b'\x01\x01\x80\x00\x00':
        logging.debug("Found magic bytes in iTunes Prefs FRPD... Finding Usernames and Desktop names now")
        '''93 is the offset after the magic that we see user names'''
        for x in range (int(magicOffset + 92), len(data)):
            if (data[x]) == 0:
                '''157 is the offset after the magic where the computer name is found'''
                x = int(magicOffset) + 157
                if userByteArr.decode() == "":
                    continue
                else:
                    userComps.append(userByteArr.decode())
                    userByteArr = bytearray()
                    continue
            else:
                char =  (data[x])
                userByteArr.append(char)

        return userComps

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
        logging.debug("Found magic name in SINF")
        for x in range (int(magicOffset+4), len(data)):
            if (data[x]) == 0:
                break
            else:
                char =  (data[x])
                userByteArr.append(char)

        userName = userByteArr.decode()
        logging.debug("Found user's name from SINF: " + userName)
        return userName
    else:
        return ""


def ReadApplicationPlists(info_plist, singleApplication, applications):
    '''This is all apps installed'''
    singleApp = info_plist.get("Applications", '')

    '''Now we single it down to the specific app we are looking for, which is another embedded plist'''
    appPlist = singleApp.get(singleApplication, {})

    '''Checks if any sideloaded apps are in the dict, which won't have data'''
    if len(appPlist) != 0:
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
            logging.debug("No full name found for: " + iTunesPlist.get('itemName', '')
                          + " This means it could be sideloaded")
            sideloaded = True
        else:
            sideloaded = False

        apps = Applications(
            info_plist.get('Device Name', ''),
            info_plist.get('Serial Number', ''),
            iTunesPlist.get('itemName', ''),
            accountInfo.get('AppleID', ''),
            name,
            downloadInfo.get('purchaseDate', ''),
            sideloaded,
            iTunesPlist.get('bundleVersion', ''),
            iTunesPlist.get('is-auto-download', ''),
            iTunesPlist.get('is-purchased-redownload', ''),
            iTunesPlist.get('artistName', ''),
            iTunesPlist.get('softwareVersionBundleId', ''))

    else:
        apps = Applications(
            '',
            '',
            singleApplication,
            '',
            '',
            '',
            1,
            '',
            '',
            '',
            '',
            singleApplication,)

    applications.append(apps)

'''Function to find difference in two lists'''
def diff(first, second):
    second = set(second)
    return [item for item in first if item not in second]

'''Reads data from each plist supplied'''
def ReadDataFromPlists(info_plist, status_plist, manifest_plist, backups, applications):

    if manifest_plist.get('IsEncrypted', ''):
        logging.info("The device: \'" + info_plist.get('Device Name', '')  + "\' iTunes Backup is encrypted!")

    ReadBackupPlists(info_plist, status_plist, manifest_plist, backups)

    allApps = info_plist.get('Applications', '')

    '''Sometimes apps are missing from the Applications field but are present in the Installed Applictaion fields
    Usually this happens with sideloaded apps'''
    compare = []
    for a in allApps:
        compare.append(a)
    installedApps = info_plist.get('Installed Applications', '')
    missingApps = diff(installedApps, compare)
    if len(missingApps) != 0:
        for apps in missingApps:
            logging.info("Found evidence of a sideloaded app: " + apps)
            allApps[str(apps)] = {}
    for singleApps in allApps:
        ReadApplicationPlists(info_plist, singleApps, applications)




def sqlWriter(backups, applications, userComps, output):

    '''Opens database for iTunes_Backups'''
    backupDb = os.path.join(output, "iTunes_Backups.db")
    if os.path.exists(backupDb):
        os.remove(backupDb)
    conn = OpenDb(backupDb)
    c = conn.cursor()

    '''Creates database table for device data'''
    createBackQuery = "CREATE TABLE Device_Data ( Device_Name TEXT, Product_Name TEXT, " \
                      "Product_Model TEXT, Phone_Number TEXT, "\
			"iOS_Version TEXT, First_Backup_UTC DATE, "\
			"Last_Backup_UTC DATE, Passcode_Set BOOL, Encrypted BOOL, "\
			"GUID TEXT, ICCID TEXT, IMEI TEXT, MEID TEXT, Serial_Num TEXT,"\
			"Full_Backup BOOL, Version TEXT, iTunes_Version TEXT);"
    try:
        c.execute(createBackQuery)
    except Exception as ex:
        logging.exception("Failed to execute query: " + createBackQuery + "\nException was: " + str(ex))

    try:
        '''Inserts for device data'''
        conn.executemany('''INSERT INTO Device_Data(Device_Name, Product_Name, Product_Model, Phone_Number, 
            iOS_Version, First_Backup_UTC, 
            Last_Backup_UTC, Passcode_Set, Encrypted, 
            GUID, ICCID, IMEI, MEID, Serial_Num,
            Full_Backup, Version, iTunes_Version) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', backups)
    except Exception as ex:
        logging.exception("Error filling Backups table. Error was: " + str(ex))


    '''Creates database table for installed apps'''
    createAppQuery = "CREATE TABLE Applications (Device_Name TEXT, Device_SN TEXT, App_Name TEXT, AppleID TEXT, " \
                     "User_Full_Name TEXT, Purchase_Date DATE, Is_Possibly_Sideloaded BOOL, App_Version TEXT, Is_Auto_Download BOOL, " \
                     "Is_Purchased_Redownload BOOL, Publisher TEXT, Full_App_Name TEXT);"

    try:
        c.execute(createAppQuery)
    except Exception as ex:
        logging.exception("Failed to execute query: " + createAppQuery + "\nException was: " + str(ex))

    try:
        conn.executemany('''INSERT INTO Applications(Device_Name, Device_SN, App_Name, AppleID, 
                     User_Full_Name, Purchase_Date, Is_Possibly_Sideloaded, App_Version, Is_Auto_Download, 
                     Is_Purchased_Redownload, Publisher, Full_App_Name) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''', applications)

    except Exception as ex:
        logging.exception("Error filling Applications table. Error was: " + str(ex))






    '''Creates database table for computer user accounts and computer names'''
    createCompQuery = "CREATE TABLE Computers_Connected_To (User_Account_Name TEXT, Computer_Name TEXT);"

    try:
        c.execute(createCompQuery)
    except Exception as ex:
        logging.exception("Failed to execute query: " + createCompQuery + "\nException was: " + str(ex))

    try:
        for x in range (0, len(userComps),2):
            y = userComps[x]
            z = userComps[x+1]
            conn.execute('''INSERT INTO Computers_Connected_To(User_Account_Name, Computer_Name) VALUES (?,?)''', (y, z))


    except Exception as ex:
        logging.exception("Error filling Computers_Connected_To table. Error was: " + str(ex))





    '''Closes iTunes_Backups.db'''
    conn.commit()
    conn.close()


def readbackup(singleIn, singleOut, recreate):

    currentDevice = ""
    encrypted = 0

    backups = []
    applications = []

    '''Paths for the plists'''
    status_plist_path = os.path.join(singleIn, "Status.plist")
    manifest_plist_path = os.path.join(singleIn, "Manifest.plist")
    info_plist_path = os.path.join(singleIn, "Info.plist")
    manifest_db_path = os.path.join(singleIn, "Manifest.db")

    try:
        info_plist = readPlist(info_plist_path)

        "Uses Product Name and Serial Number to have a folder which contains artifacts for that specific device"
        productName = info_plist.get('Product Name', '')
        SN = info_plist.get('Serial Number', '')
        currentDevice = productName + "_" + SN
    except:
        logging.exception("Failed to read Info.plist from path {}".format(info_plist_path))
        info_plist = {}
    try:
        status_plist = readPlist(status_plist_path)
    except:
        logging.exception("Failed to read Status.plist from path {}".format(status_plist_path))
        status_plist = {}
    try:
        '''Uses Manifest.plist to check encryption to decide whether Manifest.db 
           and folder structure recreation should occur'''
        manifest_plist = readPlist(manifest_plist_path)
        encrypted = manifest_plist.get('IsEncrypted', '')
    except:
        logging.exception("Failed to read Manifest.plist from path {}".format(manifest_plist_path))
        manifest_plist = {}

    ReadDataFromPlists(info_plist, status_plist, manifest_plist, backups, applications)

    '''Creates directory specific for each device'''
    customOutput = singleOut + "\\" + currentDevice
    logging.debug("Trying to create directory: " + customOutput)
    createFolder(customOutput)

    '''Find host username of the user who backed it up plus the computers it has connected to, 
    which there are two locations for, so we'll check them both, see if they're equal, and if not, parse them both'''

    '''First location for the FRPD'''
    iTunesPrefsPlist = info_plist.get('iTunes Files', {})
    binaryFrpd = iTunesPrefsPlist.get('iTunesPrefs', '')

    '''First location for the FRPD'''
    nestediTunesPrefPlist = iTunesPrefsPlist.get('iTunesPrefs.plist', {})
    parsedNested = readPlistFromString(nestediTunesPrefPlist)
    iPodPrefsBinaryFrpd = parsedNested.get('iPodPrefs', '')

    '''Check if they're equal'''
    if iPodPrefsBinaryFrpd == binaryFrpd:
        logging.debug("The two binary FRPD's matched, this is expected, parsing one now")
        try:
            userComps = frpdHelper(binaryFrpd)
            logging.debug("Successfully parsed binary FRPD")
        except Exception as ex:
            logging.exception("Could not parse binary FRPD, exception was: " + str(ex))
    else:
        logging.info("The two checked binary FRPD's do not match, we'll parse them both now")
        userComp1 = frpdHelper(binaryFrpd)
        userComp2 = frpdHelper(iPodPrefsBinaryFrpd)
        userComps = userComp1 + userComp2



    '''Send the data to the printer'''
    PrintAll(backups, applications, userComps, customOutput)


    if recreate:
        if encrypted == 0:
            '''Read manifest DB and recreates folder structure'''
            logging.info("Starting to recreate folder structure for: " + currentDevice)
            try:
                readManiDb(manifest_db_path, singleIn, customOutput)
            except Exception as ex:
                logging.exception("Could not recreate file structure for " +
                                  currentDevice + ", exception was: " + str(ex))

        else:
            logging.info("Device: " + currentDevice + " is encrypted, cannot reconstruct folder structure")
    if recreate == 0:
        logging.info("User chose not to recreate folders")


def main():
    args = get_argument()
    inputDir = args[0]
    outputDir = args[1]
    recreate = args[2]
    users = args[3]

    if len(inputDir) > 1:
        logging.info(str(len(inputDir)) + " Backups found!")
        userCursor = 0
        for folders in inputDir:

            if users != "":
                currentUser = users[userCursor]
                userCursor = userCursor + 1
                outputDir = args[1] + "\\" + currentUser

            readbackup(folders, outputDir,  recreate)


    else:
        logging.info("1 Backup found!")
        try:
            logging.info("Reading backup now")
            readbackup(inputDir[0], outputDir, recreate)
            logging.info("Backup successfully parsed")
        except Exception as ex:
            logging.exception("Backup could not be parsed, exception was: " + str(ex))

    logging.info("Program end")

if __name__ == "__main__":
    main()
