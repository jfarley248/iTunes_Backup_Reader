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
from helpers import plist_parser, recreator


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

    parser = argparse.ArgumentParser(description='Utility to read iTunes Backups')

    '''Gets paths to necessary folders'''
    parser.add_argument("-i", '--inputDir', required=True, type=str, nargs='+', dest='inputDir',
                        help='Path to iTunes Backup Folder')
    parser.add_argument("-o", '--outputDir', required=True, type=str, nargs='+', dest='outputDir',
                        help='Directory to store results')
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-t", "--type", help="Output type. txt csv or db", required=True, type=str, nargs='+', dest='out_type')
    parser.add_argument("-r", "--recreate", help="Tries to recreate folder structure for unencrypted backups",
                        action="store_true")

    args = parser.parse_args()


    '''Gets all values from users'''
    input_dir = args.inputDir[0]
    output_dir = args.outputDir[0]
    recreate = args.recreate
    verbose = args.verbose
    out_type = args.out_type[0]





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

    '''Check outtype'''
    if out_type.lower() == "db" or out_type.lower() == "csv" or out_type.lower() == "txt":
        pass
    else:
        logger.error("Out type of " + out_type + " is not valid. Choose csv, db, or txt")
        sys.exit()

    return input_dir, output_dir, recreate, out_type,logger


def main():

    '''Start time'''
    start_time = time.time()

    '''Gets all user arguments'''
    input_dir, output_dir, recreate, out_type, logger = parseArgs()

    plist_parser.parsePlists(input_dir, output_dir, out_type, logger)

    if recreate:
        logger.debug("User chose to recreate folders. Starting process now")
        recreator.startRecreate(input_dir, output_dir, logger)




    end_time = time.time()
    logger.info("Program ended in: " + str(end_time - start_time) + " seconds")



if __name__ == "__main__":
    main()
