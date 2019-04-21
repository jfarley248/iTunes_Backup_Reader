# iTunes_Backup_Analyzer
Python 3 Script to parse out iTunes backups

Download binary from the Releases section: https://github.com/jfarley248/iTunes_Backup_Analyzer/releases

*Current Version: 2.1.1*
## Updates in version 2.1
* Parses binary FRPD files to get the last connected computer names and usernames on the computer
* Sometimes when apps are sideloaded, they don't appear in "Applications", which has most the interesting data, but only in "Installed Applications" which only contains app's full name. Script now makes sure it gets those potentially sideloaded apps

## Updates in version 2.0
* Added support for recreating the file structure completely on unencrypted backups
* Added field for each installed application if they were possibly sideloaded
* More verbose logging
* Better exception handling
* Better KAPE implementation by separating backups into folders based on users

Backups located in C:\Users\{user}\AppData\Roaming\Apple Computer\MobileSync\Backup\{GUID}

Usage:
```
usage: iTunes_Backup_Analyzer.exe [-h] -i INPUTDIR [INPUTDIR ...]
                                  [-o OUTPUTDIR [OUTPUTDIR ...]] [-v] [-K]
                                  [-R]

Utility to parse out iTunes Backups

optional arguments:
  -h, --help            show this help message and exit
  -i INPUTDIR [INPUTDIR ...], --inputDir INPUTDIR [INPUTDIR ...]
                        Path to iTunes Backup Folder
  -o OUTPUTDIR [OUTPUTDIR ...], --outputDir OUTPUTDIR [OUTPUTDIR ...]
                        Directory to store results
  -v, --verbose         increase output verbosity
  -K, --kape            Flag for KAPE Tool, don't use
  -R, --recreate        Tries to recreate folder structure for unencrypted
                        backups
```


Sample Usage:
```
iTunes_Backup_Analyzer.exe -i "C:\Users\{user}\AppData\Roaming\Apple Computer\Mobilesync\Backup\cf88902bccf8e24459831b3eabd5c6d2462d7240" -o D:\Output_Directory -v -R
```

Artifacts Parsed:
* Recreation of the entire file structure on unencrypted backups
* Device Names
* Device Serial Numbers
* Product Names
* Detection of possibly sideloaded apps
* Product Models
* Phone Numbers
* iOS Version
* First Backup Timestamp
* Last Backup Timestamp
* If Passcode was Set
* If the Backup is Encrypted
* Device GUID, ICCID, IMEI,  & MEID
* iTunes Version
* All applications installed on device (Including sideloaded apps)
  * Device Installed on
  * Device Serial Number Installed on
  * App Name
  * AppleID used to Download
  * User's Full Name associated with AppleID
  * Purchase Date
  * App Version
  * Auto-Downloaded & Redownloaded
  * Publisher
  * Full App Name
  
  
## Future Updates
* Figure out how to decrypt Manifest.db with user known password
* General code refactoring and optimizations
* Need larger datasets to be tested on
