# iTunes_Backup_Reader
Python 3 Script to read iTunes Backups

Download binary from the Releases section: https://github.com/jfarley248/iTunes_Backup_Analyzer/releases

[*Current Version: 4.0.1*](https://github.com/jfarley248/iTunes_Backup_Reader/releases/tag/v4.0.1)
* Added support for decrypting iOS 10 + Backups
    * Code implemented from https://github.com/jsharkey13/iphone_backup_decrypt




Usage:
```
usage: iTunes_Backup_Reader.py [-h] -i INPUTDIR -o OUTPUTDIR -t OUT_TYPE [-v]
                               [-b] [--ir] [-r] [-d] [-p PASSWORD]

Utility to Read iTunes Backups

optional arguments:
  -h, --help            show this help message and exit
  -i INPUTDIR, --inputDir INPUTDIR
                        Path to iTunes Backup Folder
  -o OUTPUTDIR, --outputDir OUTPUTDIR
                        Directory to store results
  -t OUT_TYPE, --type OUT_TYPE
                        Output type. txt csv or db
  -v, --verbose         increase output verbosity
  -b, --bulk            Bulk parse. Point at folder containing backup folders
  --ir                  Incident Response Mode. Will automatically check user
                        folders for backups. Requires admin rights. Point at
                        root of drive
  -r, --recreate        Tries to recreate folder structure for unencrypted
                        backups
  -d, --decrypt         Just decrypts the backup into an unecrypted, unparsed
                        format
  -p PASSWORD           Password for encrypted backups



```

Backups located in C:\Users\{user}\AppData\Roaming\Apple Computer\MobileSync\Backup\{GUID}

Artifacts Parsed:
* Recreation of the entire file structure on unencrypted backups
* Device Names
* Device Serial Numbers
* Product Names
* Detection of possibly sideloaded apps
* Product Models
* Phone Numbers
* iOS Version
* Backup Completed
* Backup Completed Write
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
  
  
## Updates in Version 3

#### Version 3.1

* KAPE Support with updated module 
* IR Mode which automatically goes through drive and finds iTunes backups
* Bulk processing - Point at a directory of iTunes backups to read them all at once

#### Version 3.0

* Partial rewrite
* Now FULLY supports parsing unencrypted MBDB backups!
    * ex. You can now recreate file structures with older iTunes Backups
* Can now output to CSV, TXT or DB
* More detailed application reports
* More accurate timestamp labeling 
* Many bug fixes
* Still no support for decrypting backups :( 
* New name to more accurately describe what this tool is doing

*Big thanks to Tony Knutson @bigt252002 for helping me test and providing ideas and feedback on new features!*
 
## Updates in version 2.1
* Parses binary FRPD files to get the last connected computer names and usernames on the computer
* Sometimes when apps are sideloaded, they don't appear in "Applications", which has most the interesting data, but only in "Installed Applications" which only contains app's full name. Script now makes sure it gets those potentially sideloaded apps

## Updates in version 2.0
* Added support for recreating the file structure completely on unencrypted backups
* Added field for each installed application if they were possibly sideloaded
* More verbose logging
* Better exception handling
* Better KAPE implementation by separating backups into folders based on users
  
# Future Updates
* General code refactoring and optimizations
* Need larger datasets to be tested on

# Known Issues
* Problems with recreating file structure if NTFS long paths are not enabled
