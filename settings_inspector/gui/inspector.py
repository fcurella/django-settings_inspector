import sys
import curses
import locale
from .windows.settings import SettingsWindow
from .windows.variables import VariablesWindow


class InspectorUI(object):
    def __init__(self, root_setting):
        self.root_setting = root_setting
        locale.setlocale(locale.LC_ALL, '')
        self.code = locale.getpreferredencoding()
        self.render()

    # catch any weird termination situations
    def __del__(self):
        self.restore_screen()

    def render(self):
        try:
            sys.exit(self._render())
        finally:
            self.restore_screen()

    def restore_screen(self):
        curses.nocbreak()
        curses.echo()
        curses.noraw()
        curses.endwin()
    
    def show_variables(self):
        self.win = VariablesWindow(self.root_setting, parent_ui=self, screen=self.stdscr)
        self.stdscr.refresh()
    
    def show_settings(self):
        self.win = SettingsWindow(self.root_setting, parent_ui=self, screen=self.stdscr)
        self.stdscr.refresh()

    def _render(self):
        self.stdscr = curses.initscr()
        curses.raw()
        curses.noecho()
        curses.cbreak()

        self.show_settings()
