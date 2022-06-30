import sys
import configparser
import subprocess
import threading
import time
import os
import win32api
import win32con
import win32gui_struct
import win32gui
from tinyWinToast.tinyWinToast import *

_cwd = os.path.dirname(os.path.realpath(__file__))
TRAY_ICON   = os.path.join(_cwd, "logo.ico")
TRAY_TEXT   = "rClone Backup (Test)"

current_program = win32gui.GetForegroundWindow()

class SysTray(threading.Thread):
    QUIT = 'QUIT'
    SPECIAL_ACTIONS = [QUIT]

    PROCESS_DONE = 0
    PROCESS_COUNT = 0

    FIRST_ID = 1023

    def __init__(self, icon, hover_text, menu_options, on_quit=None, on_status=None, default_menu_index=None, window_class_name=None):
        threading.Thread.__init__(self)
        self.icon = icon
        self.hover_text = hover_text
        self.on_quit = on_quit
        self._is_alive = True
        
        self.menu_options = menu_options.append(('Status', None, on_status))
        self.menu_options = menu_options.append(('Quit', None, self.QUIT))
        self._next_action_id = self.FIRST_ID
        self.menu_actions_by_id = set()
        self.menu_options = self._add_ids_to_menu_options(list(menu_options))
        self.menu_actions_by_id = dict(self.menu_actions_by_id)
        del self._next_action_id

        self.default_menu_index = (default_menu_index or 0)
        self.window_class_name = window_class_name or "SysTrayIconPy"

    @staticmethod
    def _force_kill():
        current_pid = os.getpid()
        os.system("taskkill /pid %s /f" % current_pid)

    def run(self):
        message_map = {
            win32gui.RegisterWindowMessage("TaskbarCreated"): self.restart,
            win32con.WM_DESTROY: self.destroy,
            win32con.WM_COMMAND: self.command,
            win32con.WM_USER+20: self.notify
        }

        # Register the Window class.
        wc = win32gui.WNDCLASS()
        hinst = wc.hInstance = win32gui.GetModuleHandle(None)
        wc.lpszClassName = self.window_class_name
        wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW;
        wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        wc.hbrBackground = win32con.COLOR_WINDOW
        wc.lpfnWndProc = message_map # could also specify a wndproc.
        class_atom = win32gui.RegisterClass(wc)

        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow(
            class_atom,
            self.window_class_name,
            style,
            0,
            0,
            win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT,
            0,
            0,
            hinst,
            None
        )
        win32gui.UpdateWindow(self.hwnd)
        self.notify_id = None
        self.refresh_icon()

        #win32gui.PumpMessages()
        while self._is_alive:
            win32gui.PumpWaitingMessages()
        win32gui.DestroyWindow(self.hwnd)

    @staticmethod
    def non_string_iterable(obj):
        try:
            iter(obj)
        except TypeError:
            return False
        else:
            return not isinstance(obj, str)

    def create_notification(self, title, message, duration=10):
        hinst = win32gui.GetModuleHandle(None)
        if os.path.isfile(self.icon):
            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            hicon = win32gui.LoadImage(
                hinst,
                self.icon,
                win32con.IMAGE_ICON,
                0,
                0,
                icon_flags
            )
        else:
            print("Can't find icon file - using default.")
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, (self.hwnd, 0, win32gui.NIF_INFO, win32con.WM_USER + 20, hicon, "Balloon Tooltip", message, 200, title))

    def _add_ids_to_menu_options(self, menu_options):
        result = []
        for menu_option in menu_options:
            option_text, option_icon, option_action = menu_option
            if callable(option_action) or option_action in self.SPECIAL_ACTIONS:
                self.menu_actions_by_id.add((self._next_action_id, option_action))
                result.append(menu_option + (self._next_action_id,))
            elif self.non_string_iterable(option_action):
                result.append((option_text, option_icon, self._add_ids_to_menu_options(option_action), self._next_action_id))
            else:
                print('Unknown item', option_text, option_icon, option_action)
            self._next_action_id += 1
        return result

    def refresh_icon(self):
        # Try and find a custom icon
        hinst = win32gui.GetModuleHandle(None)
        if os.path.isfile(self.icon):
            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            hicon = win32gui.LoadImage(
                hinst,
                self.icon,
                win32con.IMAGE_ICON,
                0,
                0,
                icon_flags
            )
        else:
            print("Can't find icon file - using default.")
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        if self.notify_id: message = win32gui.NIM_MODIFY
        else: message = win32gui.NIM_ADD
        self.notify_id = (
            self.hwnd,
            0,
            win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP,
            win32con.WM_USER + 20,
            hicon,
            self.hover_text
        )
        win32gui.Shell_NotifyIcon(message, self.notify_id)

    def restart(self, hwnd, msg, wparam, lparam):
        self.refresh_icon()

    def destroy(self, hwnd, msg, wparam, lparam):
        if self.on_quit: self.on_quit(self)
        nid = (self.hwnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        win32gui.PostQuitMessage(0) # Terminate the app.
        self._is_alive = False

    def notify(self, hwnd, msg, wparam, lparam):
        if lparam == win32con.WM_LBUTTONDBLCLK:
            self.execute_menu_option(self.default_menu_index + self.FIRST_ID)
        elif lparam == win32con.WM_RBUTTONUP:
            self.show_menu()
        elif lparam == win32con.WM_LBUTTONUP:
            pass
        return True

    def show_menu(self):
        menu = win32gui.CreatePopupMenu()
        self.create_menu(menu, self.menu_options)
        #win32gui.SetMenuDefaultItem(menu, 1000, 0)

        pos = win32gui.GetCursorPos()
        # See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winui/menus_0hdi.asp
        win32gui.SetForegroundWindow(self.hwnd)
        win32gui.TrackPopupMenu(
            menu,
            win32con.TPM_LEFTALIGN,
            pos[0],
            pos[1],
            0,
            self.hwnd,
            None
        )
        win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)

    def create_menu(self, menu, menu_options):
        for option_text, option_icon, option_action, option_id in menu_options[::-1]:
            if option_icon:
                option_icon = self.prep_menu_icon(option_icon)

            if option_id in self.menu_actions_by_id:                
                item, extras = win32gui_struct.PackMENUITEMINFO(text=option_text, hbmpItem=option_icon, wID=option_id)
                win32gui.InsertMenuItem(menu, 0, 1, item)
            else:
                submenu = win32gui.CreatePopupMenu()
                self.create_menu(submenu, option_action)
                item, extras = win32gui_struct.PackMENUITEMINFO(text=option_text, hbmpItem=option_icon, hSubMenu=submenu)
                win32gui.InsertMenuItem(menu, 0, 1, item)

    def prep_menu_icon(self, icon):
        # First load the icon.
        ico_x = win32api.GetSystemMetrics(win32con.SM_CXSMICON)
        ico_y = win32api.GetSystemMetrics(win32con.SM_CYSMICON)
        hicon = win32gui.LoadImage(0, icon, win32con.IMAGE_ICON, ico_x, ico_y, win32con.LR_LOADFROMFILE)

        hdcBitmap = win32gui.CreateCompatibleDC(0)
        hdcScreen = win32gui.GetDC(0)
        hbm = win32gui.CreateCompatibleBitmap(hdcScreen, ico_x, ico_y)
        hbmOld = win32gui.SelectObject(hdcBitmap, hbm)
        # Fill the background.
        brush = win32gui.GetSysColorBrush(win32con.COLOR_MENU)
        win32gui.FillRect(hdcBitmap, (0, 0, 16, 16), brush)
        # unclear if brush needs to be feed.  Best clue I can find is:
        # "GetSysColorBrush returns a cached brush instead of allocating a new
        # one." - implies no DeleteObject
        # draw the icon
        win32gui.DrawIconEx(hdcBitmap, 0, 0, hicon, ico_x, ico_y, 0, 0, win32con.DI_NORMAL)
        win32gui.SelectObject(hdcBitmap, hbmOld)
        win32gui.DeleteDC(hdcBitmap)

        return hbm

    def command(self, hwnd, msg, wparam, lparam):
        id = win32gui.LOWORD(wparam)
        self.execute_menu_option(id)

    def execute_menu_option(self, id):
        menu_action = self.menu_actions_by_id[id]      
        if menu_action == self.QUIT:
            self._is_alive = False
        else:
            menu_action(self)

def tray_quit(tray):
    tray.create_notification(
        'rClone Backup (Test)', 
        "Quitting test."
    )
    print('Quitting.')

def status(toast):
    toast = Toast()
    toast.appId = "AppID"
    toast.setTitle("TITLE", maxLines=1)
    toast.setMessage("MESSAGE", maxLines=1)
    toast.addProgress(Progress(title="Title", value="0.6", valueStringOverride="15/20", status="Save..."))
    toast.setIcon(TRAY_ICON, crop=CROP_CIRCLE)
    toast.addText("from email", placement="attribution", maxLines=1)
    toast.show()
    
def update_status(toast):
    toast.setProgress(Progress(title="Title", value="0.9", valueStringOverride="19/20", status="Save..."))
    toast.show()
    #d = {'progressValue': "0.9", 'progressValueString': "19/20"}
    #toast.update(200, d)

sys_tray = SysTray(TRAY_ICON, TRAY_TEXT, [], on_quit=tray_quit, on_status=None, default_menu_index=1, window_class_name=TRAY_TEXT)
sys_tray.start()

toast = Toast()
status(toast)
while sys_tray._is_alive:
    update_status(toast)
    time.sleep(1)

if not sys_tray._is_alive:
    sys_tray.create_notification(
        'rClone Backup (Test)', 
        "Just testing out the notification system."
    )
    
sys_tray._is_alive = False