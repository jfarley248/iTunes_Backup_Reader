'''
   Copyright (c) 2019 Jack Farley
   This file is part of iTunes_Backup_Reader
   Usage or distribution of this software/code is subject to the
   terms of the GNU GENERAL PUBLIC LICENSE.
   iTunes_Backup_Reader.py
   ------------
'''
from __future__ import unicode_literals
from __future__ import print_function
import os
import logging
import argparse
import time
import sys
import ctypes
import glob
from helpers import plist_parser, recreator
from multiprocessing import Process


ASCII_ART = '''

  _ _____                   ___          _               ___             _         
 (_)_   _|  _ _ _  ___ ___ | _ ) __ _ __| |___  _ _ __  | _ \___ __ _ __| |___ _ _ 
 | | | || || | ' \/ -_|_-< | _ \/ _` / _| / / || | '_ \ |   / -_) _` / _` / -_) '_|
 |_| |_| \_,_|_||_\___/__/_|___/\__,_\__|_\_\\_,_| .__/_|_|_\___\__,_\__,_\___|_|  
                        |___|                    |_| |___|                         

'''


def createLogger(verbose, output_dir):

        log_out = os.path.join(output_dir, "iTunes_Backup_Reader.log")

        logger = logging

        if verbose:
            logger.basicConfig(handlers=[logger.StreamHandler(), logger.FileHandler(log_out)], level=logger.DEBUG,
                                format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                                datefmt='%m-%d %H:%M')

        else:
            logger.basicConfig(handlers=[logger.StreamHandler(), logger.FileHandler(log_out)], level=logger.INFO,
                                format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                                datefmt='%m-%d %H:%M')

        return logger


def parseArgs():

    parser = argparse.ArgumentParser(description='Utility to Read iTunes Backups')

    '''Gets paths to necessary folders'''
    parser.add_argument("-i", '--inputDir', required=True, type=str, dest='inputDir',
                        help='Path to iTunes Backup Folder')

    parser.add_argument("-o", '--outputDir', required=True, type=str, dest='outputDir',
                        help='Directory to store results')

    parser.add_argument("-t", "--type", help="Output type. txt csv or db", required=True, type=str,
                        dest='out_type')

    parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")

    parser.add_argument("-b", "--bulk", help="Bulk parse. Point at folder containing backup folders", action="store_true")

    parser.add_argument("--ir", help="Incident Response Mode. Will automatically check user folders for "
                                    "backups. Requires admin rights. Point at root of drive", action="store_true")



    parser.add_argument("-r", "--recreate", help="Tries to recreate folder structure for unencrypted backups",
                        action="store_true")

    parser.add_argument("-d", "--decrypt", help="Just decrypts the backup into an unecrypted, unparsed format",
                        action="store_true")

    parser.add_argument("-p",  help="Password for encrypted backups", default=None, type=str,
                        dest='password')

    args = parser.parse_args()


    '''Gets all values from users'''
    input_dir = args.inputDir
    output_dir = args.outputDir
    recreate = args.recreate
    decrypt = args.decrypt
    verbose = args.verbose
    out_type = args.out_type
    password = args.password
    bulk = args.bulk
    ir_mode = args.ir


    '''Check output directory and create directory if not exists'''
    if os.path.exists(output_dir):
        pass
    else:
        try:
            os.makedirs(output_dir)
        except Exception as ex:
            print("Could not create output directory: " + output_dir + " Exception was: " + str(ex))
            sys.exit()

    '''Create Logger'''
    logger = createLogger(verbose, output_dir)
    logger.debug("Created logger object")

    '''Cant have both IR Mode and Bulk mode'''
    if ir_mode and bulk:
        logger.error("Cannot have both IR Mode and Bulk mode, exiting")
        sys.exit()

    '''Check outtype'''
    if out_type.lower() == "db" or out_type.lower() == "csv" or out_type.lower() == "txt":
        pass
    else:
        logger.error("Out type of " + out_type + " is not valid. Choose csv, db, or txt")
        sys.exit()

    if bulk and password:
        logger.error("Cannot use bulk mode with encrypted backups")
        sys.exit()

    '''Checks admin rights for IR Mode'''
    if ir_mode:
        logger.debug("User chose IR Mode... Checking admin rights")
        try:
            is_admin = (os.getuid() == 0)
        except AttributeError:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        if is_admin:
            logger.debug("Admin rights found for IR Mode")
        if not is_admin:
            logger.error("Admin rights not found! Exiting")
            sys.exit()


    return input_dir, output_dir, recreate, decrypt, out_type, ir_mode, bulk, password, logger


def main():

    '''Start time'''
    start_time = time.time()

    '''Gets all user arguments'''
    input_dir, output_dir, recreate, decrypt, out_type, ir_mode, bulk, password, logger = parseArgs()

    '''Parse a single backup'''
    if not bulk and not ir_mode:
        logger.info("Starting to read backup at: " + input_dir)
        plist_parser.parsePlists(input_dir, output_dir, out_type, decrypt, logger)

        if recreate and not decrypt:
            logger.debug("User chose to recreate folders. Starting process now")
            recreator.startRecreate(input_dir, output_dir, password, 0, logger)


        '''Just decrypt backup and no recreate'''
        if decrypt and not recreate:
            if password is None:
                logger.error("You need to supply a password for decryption")
                sys.exit()
            recreator.startRecreate(input_dir, output_dir, password, decrypt, logger)


        if decrypt and recreate:
            logger.error("Cannot use -d and -r flags together. -r will decrypt the backup and recreate")
            sys.exit()

    '''Bulk parse'''
    if bulk:
        subfolders = os.listdir(input_dir)
        for folders in subfolders:
            current_folder = os.path.join(input_dir, folders)
            logger.info("Starting to read backup at: " + current_folder)
            plist_parser.parsePlists(current_folder, output_dir, out_type, decrypt, logger)

            if recreate:
                logger.info("User chose to recreate folders. Starting process now")
                recreator.startRecreate(current_folder, output_dir, password, logger)

    if ir_mode:
        path = "\\Users\\*\\AppData\\Roaming\\Apple Computer\\MobileSync\\Backup\\*"
        all_paths = glob.glob(path)


        for folders in all_paths:

            logger.info("Starting to read backup at: " + folders)
            plist_parser.parsePlists(folders, output_dir, out_type, logger)

            if recreate:
                logger.info("User chose to recreate folders. Starting process now")
                recreator.startRecreate(folders, output_dir, password, logger)


    end_time = time.time()
    logger.info("Program ended in: " + str(end_time - start_time) + " seconds")



if __name__ == "__main__":
    print(ASCII_ART)
    print("Written by Jack Farley\n")
    main()
