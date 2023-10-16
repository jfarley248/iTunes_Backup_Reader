'''
   Copyright (c) 2019 Jack Farley
   This file is part of iTunes_Backup_Reader
   Usage or distribution of this software/code is subject to the
   terms of the GNU GENERAL PUBLIC LICENSE.
   recreator.py
   ------------

   With help from: https://github.com/Anarky/mbdbEditor

'''

import plistlib
import os
from helpers import manifestDbParser, manifestMbdbParser, encryptedDbParser
import sys
from helpers import decryptor



def startRecreate(input_dir, output_dir, password, decrypt_only, logger):


    '''Check encryption'''
    manifest_plist_path = os.path.join(input_dir, "Manifest.plist")
    with open(manifest_plist_path, "rb") as fh:
        manifest_plist = plistlib.load(fh)

    encrypted = manifest_plist.get("IsEncrypted", {})
    version = float(manifest_plist.get("Version", {}))

    manifest_db_path = os.path.join(input_dir, "Manifest.db")



    if encrypted:
        if password is None:
            logger.error("You did not specify a password for your encrypted backup")

        if version >= 10:
            decrypt = decryptor.Decryptor(input_dir, output_dir, password, logger)
            manifest_db_path = decrypt.decrypted_manifest_db
        else:
            logger.error("Support for decrypting iOS 9 and under backups not currently implemented")
            return





        '''Create output directpry based on device serial number'''
        info_plist_path = os.path.join(input_dir, "Info.plist")
        info_plist = readPlist(info_plist_path)
        serial_number = info_plist.get('Serial Number', '')

        if not decrypt_only:

            output_dir = os.path.join(output_dir, "Device_" + serial_number + "_Folders")
            if not os.path.exists(output_dir): os.makedirs(output_dir)

        else:
            output_dir = os.path.join(output_dir, "Device_" + serial_number + "_DecryptedBackup")
            if not os.path.exists(output_dir): os.makedirs(output_dir)

        encryptedDbParser.readEncManiDb(manifest_db_path, input_dir, output_dir, decrypt, decrypt_only, logger)



        x = 0


    else:

        logger.info("Backup is not encrypted")

        '''Check if database is db or mbdb'''

        manifest_mbdb_path = os.path.join(input_dir, "Manifest.mbdb")
        if os.path.isfile(manifest_mbdb_path):
            logger.debug("Older Manifest.mbdb found")
            manifestMbdbParser.mbdbParser(manifest_mbdb_path, input_dir, output_dir, logger)
        if os.path.isfile(manifest_db_path):
            logger.debug("Modern Manifest.db found")
            manifestDbParser.readManiDb(manifest_db_path, input_dir, output_dir, logger)




