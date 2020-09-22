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

import os
import helpers.deserializer as deserializer
from biplist import *
import logging
import plistlib
import datetime
import io
import os
import re
import errno
import sqlite3
from pathlib_revised import Path2
from shutil import copyfile




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

def readEncManiDb(manifestPath, sourceDir, outputDir, decrypt_object, decrypt_only, logger):

    '''Creates Root folder for recreated file structure'''
    root = outputDir
    createFolder(root, logger)


    '''Copy Decrypted manifest db to decrypted backup'''
    if decrypt_only:
        dest_manifest = os.path.join(outputDir, "BACKUP", "Manifest.db")
        copyfile(decrypt_object.decrypted_manifest_db, dest_manifest)

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

            if fType == 1:
                if decrypt_only:
                    file_path = os.path.join(outputDir, "BACKUP", fileId[0:2], fileId)
                else:
                    file_path = os.path.join(outputDir, "Recreated_Structure", relativePath)
                decrypt_object.decryptor_object.extract_file(relative_path=relativePath, output_filename=file_path)
        except Exception as ex:
            logger.exception("Recreation failed for file {}/{}".format(domain, relativePath))

    if len(file_meta_list):
        WriteMetaDataToDb(file_meta_list, outputDir, logger)