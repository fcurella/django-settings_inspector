import sys
import curses
import locale


class InspectorUI(object):
    tab_size = 4
    current_line = 0
    current_indent = 0
    current_column = 0

    def __init__(self, root_setting):
        self.root_setting = root_setting
        self.scroll_index = 0
        locale.setlocale(locale.LC_ALL, '')
        self.code = locale.getpreferredencoding()

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
        curses.endwin()

    def _render(self):
        self.stdscr = curses.initscr()
        self.lines = [(i, 0, '', curses.A_DIM) for i in range(self.stdscr.getmaxyx()[0])]
        self.stdscr.keypad(True)
        curses.noecho()
        curses.cbreak()

        self.add_settings(self.root_setting)
        self.refresh()
        while 1:
            self.on_ch(self.stdscr.getch())

    def next_line(self):
        self.current_line = self.current_line + 1
        return self.current_line
    
    def carriage_return(self):
        self.current_indent = self.current_column = 0
        return self.next_line()

    def tab(self):
        self.current_indent = self.current_indent + 1
        self.current_column = self.current_indent * self.tab_size
        return self.current_column

    def write(self, text, attr=curses.A_DIM):
            new_line = (self.current_line, self.current_column, text, attr)
            if self.current_line >= len(self.lines):
                for missing in range(self.current_line - len(self.lines)):
                    empty_line = (len(self.lines) + missing, 0, '', curses.A_DIM)
                    self.lines.append(empty_line)
                self.lines.append(new_line)
            else:
                self.lines[self.current_line] = new_line

    def refresh(self):
        self.stdscr.clear()
        start = self.scroll_index
        end = start + self.stdscr.getmaxyx()[0]
        for line, column, text, attr in self.lines[start:end]:
            self.stdscr.addstr(line - start, column, text, attr)
        self.stdscr.refresh()

    def add_settings(self, parent_setting, indentation=0):
        if indentation > self.current_indent:
            self.tab()
        self.write(u"- %s" % parent_setting, attr=curses.A_BOLD)
        self.add_variables(parent_setting)
        new_indentation = indentation + 1
        self.next_line()
        for i, setting in enumerate(parent_setting.children_settings.values(), 1):
            self.add_settings(setting, indentation=new_indentation)

    def add_variables(self, setting):
        self.tab()
        for i, assignment in enumerate(setting.assignments):
            self.next_line()
            self.write(u"%s" % assignment)
    
    def on_ch(self, cmd):
        win_height = self.stdscr.getmaxyx()[0]
        if cmd in [curses.KEY_DOWN]:
            if self.scroll_index+win_height < len(self.lines):
                self.scroll_index += 1
        elif cmd == curses.KEY_UP:
            if self.scroll_index > 0:
                self.scroll_index -= 1
        elif cmd == 32:
            tmp_scroll = self.scroll_index + win_height
            if tmp_scroll+win_height > len(self.lines):
                tmp_scroll = len(self.lines) - win_height
            self.scroll_index = tmp_scroll

        self.refresh()
