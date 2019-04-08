# iTunesBackupAnalyzer
Python 3 Script to parse out iTunes backups and outputs to an SQLite Database

*Current Version: 1.0*

Point it at either a directory of backups, or a single backup folder containing the Info.plist, Manifest.plist, and Status.plist

Usage:
```
usage: iTunes_Backup_Analyzer.exe [-h] -i INPUTDIR [INPUTDIR ...] -o OUTPUTDIR
                                  [OUTPUTDIR ...] [-v] [-K]

Utility to parse out iTunes Backup plists and DB

optional arguments:
  -h, --help            show this help message and exit
  -i INPUTDIR [INPUTDIR ...], --inputDir INPUTDIR [INPUTDIR ...]
                        Path to iTunes Backup Folder
  -o OUTPUTDIR [OUTPUTDIR ...], --outputDir OUTPUTDIR [OUTPUTDIR ...]
                        Directory to store results
  -v, --verbose         increase output verbosity
  -K, --Kape            Use this flag for Kape Tool, don't use
```


Sample Usage:
```
iTunes_Backup_Analyzer.exe -i "C:\Users\{user}\AppData\Roaming\Apple Computer\Mobilesync\Backup\cf88902bccf8e24459831b3eabd5c6d2462d7240" -o D:\Output_Directory
```

Artifacts Parsed:
* Device Names
* Device Serial Numbers
* Product Names
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
* Submit KAPE .mkape file to the official repo (needs a bit more testing with command line options)
* Add field to indicate if app was sideloaded (currently it logs suspicious apps to console)
* Parse Manifest.db on unencrypted backups
* Add option to decode Manifest.db if user knows password
* General code refactoring and optimizations
* Need larger datasets to be tested on
