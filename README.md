# iTunes_Backup_Reader
Python 3 Script to parse out iTunes Backups

Download binary from the Releases section: https://github.com/jfarley248/iTunes_Backup_Analyzer/releases

NOTE: KAPE Module only supports versions lower than 3.0

*Current Version: 3.0*
## Updates in version 3.0
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


Usage:
```
usage: iTunes_Backup_Reader.py [-h] -i INPUTDIR [INPUTDIR ...] -o OUTPUTDIR
                               [OUTPUTDIR ...] [-v] -t OUT_TYPE [OUT_TYPE ...]
                               [-r]

Utility to read iTunes Backups

optional arguments:
  -h, --help            show this help message and exit
  -i INPUTDIR [INPUTDIR ...], --inputDir INPUTDIR [INPUTDIR ...]
                        Path to iTunes Backup Folder
  -o OUTPUTDIR [OUTPUTDIR ...], --outputDir OUTPUTDIR [OUTPUTDIR ...]
                        Directory to store results
  -v, --verbose         increase output verbosity
  -t OUT_TYPE [OUT_TYPE ...], --type OUT_TYPE [OUT_TYPE ...]
                        Output type. txt csv or db
  -r, --recreate        Tries to recreate folder structure for unencrypted
                        backups

Process finished with exit code 0

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
* Add support for KAPE on version 3.0
* Figure out how to decrypt Manifest.db with user known password
* General code refactoring and optimizations
* Need larger datasets to be tested on
