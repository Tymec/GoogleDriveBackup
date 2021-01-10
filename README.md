<img align="right" width="200" src="./res/logo.png"></img>
GoogleDriveBackup
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-green.svg)](https://www.python.org/)
[![MIT license](https://img.shields.io/badge/License-MIT-green.svg)](https://lbesson.mit-license.org/)
===
### Google Drive Backup script using rclone
```
config.ini usage:
You can add as many jobs as you want. Section names needs to be JOB_#.
Each job needs to have these three options: NAME, PATH and REMOTE:
- NAME          = Name of the job
- PATH          = Path to backup from
- REMOTE        = rclone path to backup to

Each section can be manually adjusted to your needs, ie. you can for example add 'BWLIMIT 10' to the ARGUMENTS section:
- [OPTIONS]     = DO NOT CHANGE UNLESS YOU KNOW WHAT YOU'RE DOING
- [PARAMETERS]  = rclone flags that do not take any arguments, ie. --verbose (1 = true, 0 = false)
- [ARGUMENTS]   = check out https://rclone.org/flags/ for more
```
---
You can use https://nssm.cc/ to run the script on boot.
