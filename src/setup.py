import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": [
        "os",
        "sys",
        "configparser",
        "subprocess",
        "threading",
        "time",
        "os",
        "win32api",
        "win32con",
        "win32gui_struct",
        "win32gui"
    ],
    "include_files": ["logo.ico", "config.ini"]
}

setup(
    name = "rcloneBackupTool",
    version = "0.1.0",
    description = "Backup tool that uses rclone",
    author = "Tymec",
    url = "https://github.com/Tymec/rcloneBackupTool",
    options = {
        "build_exe": build_exe_options
    },
    executables = [
        Executable("main.py", icon="logo.ico", target_name="rCloneBackupTool.exe")
    ]
)