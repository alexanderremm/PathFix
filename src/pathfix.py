import os
import pathlib
import sys
import threading
import time
import wx
import wx.adv
import win32api
import win32con
import win32clipboard

TRAY_TOOLTIP = 'PathFix'
TRAY_ICON = 'icon.png'

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("./src/")

    return os.path.join(base_path, relative_path)

def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.Append(item)
    return item

class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        self.shutdown = False # Flag to determine whether the app and subsystems should shutdown
        self.enabled = True # Enabled flag
        self.frame = frame
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

        # Ctrl+C detection module
        self.copy_det = threading.Thread(target=self.copy_det_thread, daemon=True)
        self.copy_det.start()

    def CreatePopupMenu(self):
        menu = wx.Menu()
        if self.enabled:
            create_menu_item(menu, 'Disable', self.on_disable)
        else:
            create_menu_item(menu, 'Enable', self.on_enable)
        create_menu_item(menu, 'About', self.on_about)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)

        return menu

    def set_icon(self, path):
        fpath = resource_path(path)
        icon = wx.Icon(wx.Bitmap(fpath))
        self.SetIcon(icon, TRAY_TOOLTIP)

    def on_left_down(self, event):
        print('Tray icon was left-clicked.')

    def on_enable(self, event):
        self.enabled = True
        print('enabled')

    def on_disable(self, event):
        self.enabled = False
        print('disabled')

    def on_about(self, event):
        wx.MessageBox("Version 0.1", caption="About PathFix")

    def on_exit(self, event):
        self.shutdown = True
        wx.CallAfter(self.Destroy)
        self.frame.Close()
    
    def copy_det_thread(self):
        while not self.shutdown:
            if self.enabled:
                ctrl_flag = wx.GetKeyState(wx.WXK_CONTROL)
                c_flag = win32api.GetAsyncKeyState(ord('C'))
                if (ctrl_flag and c_flag):
                    # Attempt to get the path/data
                    try:
                        # Open clipboard
                        win32clipboard.OpenClipboard()
                        cb_data = win32clipboard.GetClipboardData()
                        path = pathlib.Path(cb_data)
                        print(path.as_posix())
                        win32clipboard.EmptyClipboard()
                        win32clipboard.SetClipboardText(path.as_posix())
                        # Close clipboard
                        win32clipboard.CloseClipboard()
                    except:
                        # Unable to get/handle specified clipboard data
                        pass
                time.sleep(0.1)


class App(wx.App):
    def OnInit(self):
        frame=wx.Frame(None)
        self.SetTopWindow(frame)
        TaskBarIcon(frame)
        return True

def main():
    app = App(False)
    app.MainLoop()


if __name__ == '__main__':
    main()
