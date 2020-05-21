'''
   Copyright (c) 2020 Jack Farley
   This file is part of iTunes_Backup_Reader
   Usage or distribution of this software/code is subject to the
   terms of the GNU GENERAL PUBLIC LICENSE.
   decryptor.py

   Decryption made possible by:
        Google's iPhone-dataprotection
        James Sharkey jsharkey13 - https://github.com/jsharkey13/iphone_backup_decrypt
        Andrewdotn
   ------------
'''



from kaitaistruct import  KaitaiStruct, KaitaiStream, BytesIO


from helpers.iphone_backup_decrypt import EncryptedBackup





class Decryptor:
    def __init__(self, input_dir, output_dir, password, logger):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.logger = logger
        self.password = password
        self.decrypted_manifest_db = None
        self.start_decryption()

    def start_decryption(self):



        backup_path = self.input_dir
        decrypt = EncryptedBackup(backup_directory=backup_path, passphrase=self.password, outputdir=self.output_dir, log= self.logger)
        self.decrypted_manifest_db = decrypt._decrypted_manifest_db_path




