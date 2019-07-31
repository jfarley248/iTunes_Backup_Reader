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
import re
import errno
import sqlite3
from pathlib_revised import Path2



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
def recreate(fileId, domain, relativePath, fType, root, sourceDir, logger):

    '''Fields with types of 4 have not been found in backups to my knowledge'''
    if fType == 4:
        logger.info("Found file with type of 4: " + relativePath)
        logger.info("Type 4 files aren't found in iTunes Backups... But we'll check anyway")
        type4File = sourceDir + "\\" + fileId[0:2] + "\\" + fileId
        if os.path.isfile(type4File):
            logger.info("The file actually exists... Please contact jfarley248@gmail.com to correct this code\n")
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
            recreateFile(fileId, domain, relativePath, root, sourceDir, logger)
            logger.debug(
                "Successfully recreated file: " + domain + "\\" + relativePath + " from source file: " + fileId)
        except Exception as ex:
            logger.exception("Failed to recreate file: " + relativePath + " from source file: "
                              + fileId + " Exception was: " + str(ex))


'''Recreates the folder structures in the output directory based on type = 2'''
def recreateFolder(domain, relativePath, root, logger):

    '''If the relative path is empty, then the domain is the root folder'''
    domain = re.sub('[<>:"|?*]', '_', domain)
    relativePath = re.sub('[<>:"|?*]', '_', relativePath)
    relativePath = relativePath.replace("/", "\\")
    if not relativePath:
        newFolder = root + "\\" + domain
        createFolder(newFolder, logger)

    else:
        newFolder = root + "\\" + domain + "\\" + relativePath
        createFolder(newFolder, logger)



'''Recreates the file structures in the output directory based on type = 3'''
def recreateFile(fileId, domain, relativePath, root, sourceDir, logger):


    '''Source file created from taking first two characters of fileID,
       using that as subfolder of source directory, and finding full name of file'''
    subFolder = fileId[0:2]
    sourceFile = sourceDir + "\\" + subFolder + "\\" + fileId

    '''Gets rid of folder slashes and replaces with backslashes, offending characters with underscores'''
    sanitizedRelPath = relativePath.replace("/", "\\")
    sanitizedRelPath = re.sub('[<>:"|?*]', '_', sanitizedRelPath)
    destFile = root + "\\" + domain + "\\" + sanitizedRelPath


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
    except Exception as ex:
        logger.exception("Could not complete copy " + sourceFile + " to " + destFile + " Exception was: " + str(ex))

''' Main function for parsing Manifest.db
    Needs a connection to database, executes SQL, and calls on other functions to recreate folder structure'''
def readManiDb(manifestPath, sourceDir, outputDir, logger):

    '''Creates Root folder for recreated file structure'''
    root = outputDir + "\\" + "Recreated_File_Structure"
    createFolder(root, logger)

    conn = OpenDb(manifestPath, logger)
    c = conn.cursor()
    query = '''SELECT fileId, domain, relativePath, flags FROM files'''
    try:
        logger.debug("Trying to execute query: " + query + " against database " + manifestPath)
        c.execute(query)
        logger.debug("Successfully executed query: " + query + " against database " + manifestPath)



    except Exception as ex:
        logger.exception("Could not execute query: " + query + " against database " + manifestPath
                          + " Exception was: " + str(ex))
    for fileListing in c:
        fileId = fileListing[0]
        domain = fileListing[1]
        relativePath = fileListing[2]
        fType = fileListing[3]
        try:
            recreate(fileId, domain, relativePath, fType, root, sourceDir, logger)
        except Exception as ex:
            logger.exception("Recreation failed, exception was: " + str(ex))

