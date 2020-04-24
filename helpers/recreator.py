'''
   Copyright (c) 2019 Jack Farley
   This file is part of iTunes_Backup_Reader
   Usage or distribution of this software/code is subject to the
   terms of the GNU GENERAL PUBLIC LICENSE.
   recreator.py
   ------------

   With help from: https://github.com/Anarky/mbdbEditor

'''

from biplist import *
import os
from helpers import manifestDbParser, manifestMbdbParser
import sys



def startRecreate(input_dir, output_dir, logger):


    '''Check encryption'''
    manifest_plist_path = os.path.join(input_dir, "Manifest.plist")
    manifest_plist = readPlist(manifest_plist_path)
    encrypted = manifest_plist.get("IsEncrypted", {})







    if encrypted:
        logger.info("Backup is encrypted. Decryption support is not available")
    else:
        logger.info("Backup is not encrypted")

        '''Create output directpry based on device serial number'''
        info_plist_path = os.path.join(input_dir, "Info.plist")
        info_plist = readPlist(info_plist_path)
        serial_number = info_plist.get('Serial Number', '')
        output_dir = os.path.join(output_dir, "Device_" + serial_number + "_Folders")
        try:
            logger.debug("Trying to create directory: " + output_dir)
            os.makedirs(output_dir)
            logger.debug("Successfully created directory: " + output_dir)
        except Exception as ex:
            logger.exception("Could not create directory: " + output_dir + " Exception was: " + str(ex))
            sys.exit()


        '''Check if database is db or mbdb'''
        manifest_db_path = os.path.join(input_dir, "Manifest.db")
        manifest_mbdb_path = os.path.join(input_dir, "Manifest.mbdb")
        if os.path.isfile(manifest_mbdb_path):
            logger.debug("Older Manifest.mbdb found")
            manifestMbdbParser.mbdbParser(manifest_mbdb_path, input_dir, output_dir, logger)
        if os.path.isfile(manifest_db_path):
            logger.debug("Modern Manifest.db found")
            manifestDbParser.readManiDb(manifest_db_path, input_dir, output_dir, logger)




