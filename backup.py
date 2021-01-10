import sys
import configparser
import subprocess
import threading
import time
from WinUtils import SysTray

CONFIG_PATH = "config.ini"
LOG_PATH    = "logs"
TRAY_ICON   = "rclone.ico"
TRAY_TEXT   = "rClone Backup"

class MissingJob(Exception):
    """Raised when no job is found"""
    pass

class MissingOption(Exception):
    """Raised when an option is missing"""
    pass

class MissingSection(Exception):
    """Raised when an a section is missing"""
    pass

class Command(threading.Thread):
    def __init__(self, cmd, name):
        threading.Thread.__init__(self)
        self.name = name
        self.log_path = f"{LOG_PATH}/{name}.log"
        self.cmd = cmd
        self.quit = False
        self.finished = False

    def run(self):
        open(self.log_path, 'w').close()
        with open(self.log_path, 'a') as f:
            process = subprocess.Popen(
                self.cmd, 
                stdout = f,
                stderr = subprocess.STDOUT,
                universal_newlines = True
            )
            
            while process.poll() is None and not self.quit:
                time.sleep(1)
            self.finished = True

def parse_jobs(cfg):
    jobs = {}
    for job in [i for i in cfg.sections() if "JOB" in i]:
        jobs[job] = {
            "name": config[job]["NAME"],
            "path": config[job]["PATH"],
            "remote": config[job]["REMOTE"]
        }
    if not jobs:
        raise MissingJob("No jobs were found.")
    return jobs

def parse_cfg(section, cfg):
    if section not in cfg:
        raise MissingSection(f"Missing '{section}' section.")

    parsed = {}
    for key, val in cfg.items(section):
        parsed[key] = val
    return parsed

def create_commands(jobs, arguments, parameters, options):
    cmds = {}
    cmd = "rclone"

    for opt in options.values():
        cmd += f" {opt}"
    
    for param, val in parameters.items():
        if (val == "1"):
            cmd += f" --{param}"

    for arg, val in arguments.items():
        cmd += f" --{arg} {val}"

    for job in jobs.values():
        job_cmd = f"{cmd} \"{job['path']}\" \"{job['remote']}\""

        cmds[job['name']] = job_cmd
    
    return cmds

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

try:
    jobs = parse_jobs(config)
    arguments = parse_cfg("ARGUMENTS", config)
    parameters = parse_cfg("PARAMETERS", config)
    options = parse_cfg("OPTIONS", config)
    if not options.get('mode'):
        raise MissingOption("mode", "Mode option is required for rclone to function.")
except Exception as e:
    print(e)
    sys.exit()

commands = create_commands(jobs, arguments, parameters, options)

processes = []
for name, command in commands.items():
    cmd = Command(command, name)
    cmd.start()
    processes.append(cmd)
process_count = len(processes) 

def tray_quit(tray):
    tray.create_notification(
        'rClone Backup Status', 
        f"Finished: {process_count - len(processes)}/{process_count} jobs"
    )
    print('Quitting.')

sys_tray = SysTray(TRAY_ICON, TRAY_TEXT, [], on_quit=tray_quit, default_menu_index=1, window_class_name="rClone Backup")
sys_tray.start()

processes_finished = False

while not processes_finished and sys_tray._is_alive:
    processes_finished = len(processes) == 0
    
    new_processes = processes
    for process in processes:
        if process.finished:
            new_processes.remove(process);
            continue
    print(f"Finished: {process_count - len(processes)}/{process_count} jobs")
    processes = new_processes
    time.sleep(1)

sys_tray._is_alive = False
if len(processes) > 0:
    for process in processes:
        process.quit = True
