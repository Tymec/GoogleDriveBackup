<img align="right" width="200" src="./res/logo.png"></img>
rCloneBackupTool
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-green.svg)](https://www.python.org/)
[![MIT license](https://img.shields.io/badge/License-MIT-green.svg)](https://lbesson.mit-license.org/)
===
## Backup tool that uses rclone
For available cloud services and how to setup rclone check out: https://rclone.org/docs/
<br>
<br>
<br>
### config.ini usage:
```
You can add as many jobs as you want. Section names needs to be JOB_#. Use default 'config.ini' for reference.
Each job needs to have these three options: NAME, PATH and REMOTE:
- NAME          = Name of the job           (ex. Users Backup)
- PATH          = Path to backup from       (ex. C:\Users)
- REMOTE        = rclone path to backup to  (ex. GoogleDrive:Backups)

Each section can be manually adjusted to your needs, ie. you can for example add 'BWLIMIT 10' to the ARGUMENTS section:
- [OPTIONS]     = DO NOT CHANGE UNLESS YOU KNOW WHAT YOU'RE DOING
- [PARAMETERS]  = rclone flags that do not take any arguments, ie. --verbose (1 = true, 0 = false)
- [ARGUMENTS]   = check out https://rclone.org/flags/ for more
```
### [Download](https://github.com/Tymec/rcloneBackupTool/releases/latest)
---
You can use https://nssm.cc/ to run the script on boot.
