'''
   Copyright (c) 2019 Jack Farley
   This file is part of iTunes_Backup_Reader
   Usage or distribution of this software/code is subject to the
   terms of the GNU GENERAL PUBLIC LICENSE.
   manifestMbdbParser.py
   ------------

   With help from: https://github.com/Anarky/mbdbEditor

'''




from helpers.structs import MBDB_HEADER
import hashlib
from shutil import copyfile
import os

'''Recreate mbdb paths'''
def mbdbParser(manifest_mbdb_path, input_dir, output_dir, logger):
    manifest_mbdb_handle = open(manifest_mbdb_path, "rb")
    manifest_mbdb = manifest_mbdb_handle.read()

    '''Parse entire structure using struct MBDB_HEADER in structs.py'''
    data = MBDB_HEADER.parse(manifest_mbdb)

    '''Create custom output based on device Serial Number'''


    '''Check header of file'''
    if data.Header != "mbdb":
        logger.error("Manifest.mbdb does not have a valid header of 0xmbdb, is it corrupted?")
        return

    '''Go through each record, recreating the file structure'''
    for record in data.Records:

        '''Create domain path if it doesnt exist'''
        domain = (record.Domain.String).decode("utf-8")
        domain_path = os.path.join(output_dir + "\\" + str(domain))
        if os.path.isdir(domain_path):
            pass
        else:
            try:
                logger.debug("Trying to create directory: " + domain_path)
                os.makedirs(domain_path)
                logger.debug("Successfully created path")
            except Exception as ex:
                logger.exception("Could not create directory: " + domain_path + " Exception was: " + str(ex))

        path = (record.Path.String).decode("utf-8")
        domain_hash = domain.encode()
        path_hash = path.encode()
        if record.Size != 0:

            fileid = hashlib.sha1( domain_hash + b'-' + path_hash)
            fileid_hash = fileid.hexdigest()
            file_path = os.path.join(input_dir + "\\" + fileid_hash)
            if os.path.isfile(file_path):

                '''Do some fun reversing strings to get the directory of the path so that we can copy the file properly'''
                dest_path = os.path.join(output_dir + "\\" + domain + "\\" + path)
                dest_path = dest_path.replace("/", "\\")
                reversed_dest_path = dest_path[::-1]
                dest_path_root_reversed = reversed_dest_path.split('\\', 1)[-1]
                dest_path_root = dest_path_root_reversed[::-1]
                if os.path.isdir(dest_path_root):
                    copyfile(file_path, dest_path)
                else:
                    os.makedirs(dest_path_root)
                    copyfile(file_path, dest_path)


