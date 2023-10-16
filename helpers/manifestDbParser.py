'''
   Copyright (c) 2019 Jack Farley
   This file is part of iTunesBackupAnalyzer
   Usage or distribution of this software/code is subject to the
   terms of the GNU GENERAL PUBLIC LICENSE.
   manifestDbParser.py
   ------------
'''
from __future__ import unicode_literals
from __future__ import print_function
import helpers.deserializer as deserializer
import plistlib
import logging
import plistlib
import datetime
import io
import os
import re
import errno
import sqlite3
from pathlib_revised import Path2


def ReadUnixTime(unix_time): # Unix timestamp is time epoch beginning 1970/1/1
    '''Returns datetime object, or None upon error'''
    if unix_time not in ( 0, None, ''):
        try:
            if isinstance(unix_time, str):
                unix_time = float(unix_time)
            return datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=unix_time)
        except (ValueError, OverflowError, TypeError) as ex:
            logging.error("ReadUnixTime() Failed to convert timestamp from value " + str(unix_time) + " Error was: " + str(ex))
    return None

def createFolder(folderPath, logger):

    if not os.path.exists(folderPath):

        try:
            fixedFolderPath = Path2(folderPath)

            Path2(fixedFolderPath).makedirs()
        except Exception as ex:
            logger.exception("Could not make root directory: " + folderPath + "\nError was: " + str(ex))

def OpenDb(inputPath, logger):
    try:
        conn = sqlite3.connect(inputPath)
        logger.debug ("Opened database: " + inputPath + " successfully")
        return conn
    except Exception as ex:
        logger.exception ("Failed to open database: " + inputPath + " Exception was: " + str(ex))
    return None


'''Ingests all files/folders/plists'''
def recreate(fileId, relativePath, fType, root, sourceDir, logger, a_time, m_time):

    '''Fields with types of 4 have not been found in backups to my knowledge'''
    if fType == 4:
        logger.info("Found file with type of 4: " + relativePath)
        logger.info("Type 4 files aren't found in iTunes Backups... But we'll check anyway")
        type4File = os.path.join(sourceDir, fileId[0:2], fileId)
        if os.path.isfile(type4File):
            logger.info("The file actually exists... Please contact jfarley248@gmail.com to correct this code\n")
        else:
            logger.info("Nope, file: " + relativePath +  " does not exist")

    '''Fields with types of 2 are Folders'''
    if fType == 2:
        logger.debug("Trying to recreate directory: " + "\\" + relativePath + " from source file: " + fileId)
        try:
            recreateFolder(relativePath, root, logger)
            logger.debug("Successfully recreated directory: " + "\\" + relativePath + " from source file: " + fileId)
        except Exception as ex:
            logger.exception("Failed to recreate directory: " + relativePath + " from source file: "
                              + fileId + " Exception was: " + str(ex))

    '''Fields with types of 1 are Files'''
    if fType == 1:
        logger.debug("Trying to recreate file: " + "\\"  + relativePath + " from source file: " + fileId)
        try:
            recreateFile(fileId, relativePath, root, sourceDir, logger, a_time, m_time)
            logger.debug(
                "Successfully recreated file: "  + "\\" + relativePath + " from source file: " + fileId)
        except Exception as ex:
            logger.exception("Failed to recreate file: " + relativePath + " from source file: "
                              + fileId + " Exception was: " + str(ex))



'''Ingests all files/folders/plists'''
def recreateEnc(fileId, domain, relativePath, fType, root, sourceDir, logger, a_time, m_time, decrypt_object):

    '''Fields with types of 4 have not been found in backups to my knowledge'''
    if fType == 4:
        logger.info("Found file with type of 4: " + relativePath)
        logger.info("Type 4 files aren't found in iTunes Backups... But we'll check anyway")
        type4File = os.path.join(sourceDir, fileId[0:2], fileId)
        if os.path.isfile(type4File):
            logger.info("The file actually exists... Please contact jfarley248@gmail.com to correct this code\n")
        else:
            logger.info("Nope, file: " + relativePath +  " does not exist")

    '''Fields with types of 2 are Folders'''
    if fType == 2:
        logger.debug("Trying to recreate directory: " + domain + "\\" + relativePath + " from source file: " + fileId)
        try:
            recreateFolder(domain, relativePath, root, logger)
            logger.debug("Successfully recreated directory: " + domain + "\\" + relativePath + " from source file: " + fileId)
        except Exception as ex:
            logger.exception("Failed to recreate directory: " + relativePath + " from source file: "
                              + fileId + " Exception was: " + str(ex))

    '''Fields with types of 1 are Files'''
    if fType == 1:
        logger.debug("Trying to recreate file: " + domain + "\\"  + relativePath + " from source file: " + fileId)
        try:
            recreateFile(fileId, domain, relativePath, root, sourceDir, logger, a_time, m_time)
            logger.debug(
                "Successfully recreated file: " + domain + "\\" + relativePath + " from source file: " + fileId)
        except Exception as ex:
            logger.exception("Failed to recreate file: " + relativePath + " from source file: "
                              + fileId + " Exception was: " + str(ex))



'''Recreates the folder structures in the output directory based on type = 2'''
def recreateFolder(relativePath, root, logger):

    '''If the relative path is empty, then the domain is the root folder'''
    relativePath = re.sub('[<>:"|?*]', '_', relativePath)
    relativePath = relativePath.replace("/", "\\")
    if not relativePath:
        newFolder = root
        createFolder(newFolder, logger)

    else:
        newFolder = os.path.join(root, relativePath)
        createFolder(newFolder, logger)



'''Recreates the file structures in the output directory based on type = 3'''
def recreateFile(fileId, relativePath, root, sourceDir, logger, a_time, m_time):


    '''Source file created from taking first two characters of fileID,
       using that as subfolder of source directory, and finding full name of file'''
    subFolder = fileId[0:2]
    sourceFile = os.path.join(sourceDir, subFolder, fileId)

    '''Gets rid of folder slashes and replaces with backslashes, offending characters with underscores'''
    sanitizedRelPath = relativePath.replace("/", "\\")
    sanitizedRelPath = re.sub('[<>:"|?*]', '_', sanitizedRelPath)
    destFile = os.path.join(root, sanitizedRelPath)


    if not os.path.exists(os.path.dirname(destFile)):
        try:
            os.makedirs(os.path.dirname(destFile))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    '''Tries to copy all the files to their recreated directory'''
    try:
        logger.debug("Trying to copy " + sourceFile + " to " + destFile)
        Path2(sourceFile).copyfile(Path2(destFile))
        logger.debug("Successfully copied " + sourceFile + " to " + destFile)
        try:
            os.utime(destFile, (a_time, m_time))
        except:
            pass # silently fail
    except Exception as ex:
        logger.exception("Could not complete copy " + sourceFile + " to " + destFile + " Exception was: " + str(ex))

''' Main function for parsing Manifest.db
    Needs a connection to database, executes SQL, and calls on other functions to recreate folder structure'''
def readManiDb(manifestPath, sourceDir, outputDir, logger):

    '''Creates Root folder for recreated file structure'''
    root = os.path.join(outputDir, "Recreated_File_Structure")
    createFolder(root, logger)

    conn = OpenDb(manifestPath, logger)
    c = conn.cursor()
    query = '''SELECT fileId, domain, relativePath, flags, file FROM files'''
    try:
        logger.debug("Trying to execute query: " + query + " against database " + manifestPath)
        c.execute(query)
        logger.debug("Successfully executed query: " + query + " against database " + manifestPath)

    except Exception as ex:
        logger.exception("Could not execute query: " + query + " against database " + manifestPath
                          + " Exception was: " + str(ex))
    file_meta_list = []
    for fileListing in c:
        fileId = fileListing[0]
        domain = fileListing[1]
        relativePath = fileListing[2]
        fType = fileListing[3]
        info = getFileInfo(fileListing[4])
        ea = info.get('ExtendedAttributes', None)
        if ea:
            ea = bytes(ea)

        file_meta_list.append([ (domain + "/" + relativePath) if relativePath else domain, 
                                ReadUnixTime(info.get('LastModified', None)), 
                                ReadUnixTime(info.get('LastStatusChange', None)), ReadUnixTime(info.get('Birth', None)),
                                info.get('Size', None), info.get('InodeNumber', None), info.get('Flags', None), 
                                info.get('UserID', None), info.get('UserID', None),
                                info.get('Mode', None), info.get('ProtectionClass', None), ea
                                ])
        if len(file_meta_list) > 50000:
            WriteMetaDataToDb(file_meta_list, outputDir, logger)
            file_meta_list = []
        try:
            # Potential area to extract to decrypted backup instead of recreated structure
            recreate(fileId, relativePath, fType, root, sourceDir, logger, info.get('LastStatusChange', 0), info.get('LastModified', 0))
        except Exception as ex:
            logger.exception("Recreation failed for file {}/{}".format(domain, relativePath))

    if len(file_meta_list):
        WriteMetaDataToDb(file_meta_list, outputDir, logger)

def WriteMetaDataToDb(file_meta_list, outputDir, logger):
    outputFileInfoDb = os.path.join(outputDir, "File_Metadata.db")
    conn2 = OpenDb(outputFileInfoDb, logger)

    createMetaQuery = "CREATE TABLE IF NOT EXISTS Metadata (RelativePath TEXT, LastModified DATE, " \
                    "LastStatusChange DATE, Birth DATE, " \
                    "Size INTEGER, InodeNumber INTEGER, Flags INTEGER, UserID INTEGER, GroupID INTEGER, " \
                    "Mode INTEGER, ProtectionClass INTEGER, ExtendedAttributes BLOB)"

    try:
        conn2.execute(createMetaQuery)
    except sqlite3.Error:
        logger.exception("Failed to execute query: " + createMetaQuery)

    try:
        conn2.executemany('''INSERT INTO Metadata(RelativePath, LastModified, LastStatusChange, Birth, 
                        Size, InodeNumber, Flags, UserID, GroupID, 
                        Mode, ProtectionClass, ExtendedAttributes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                        file_meta_list)

    except sqlite3.Error:
        logger.exception("Error filling Metadata table.")

    conn2.commit()
    conn2.close()


def getFileInfo(plist_blob):
    '''Read the NSKeyedArchive plist, deserialize it and return file metadata as a dictionary'''
    info = {}
    try:
        f = io.BytesIO(plist_blob)
        info = deserializer.process_nsa_plist("", f)
        ea = info.get('ExtendedAttributes', None)
        if ea:
            #INVESTIGATE THIS MORE
            if type(ea) is bytes:
                pass
            else:
                ea = ea['NS.data']
                info['ExtendedAttributes'] = ea #str(biplist.readPlistFromString(ea))
    except Exception as ex:
        logging.exception("Failed to parse file metadata from db, exception was: " + str(ex))

    return info



