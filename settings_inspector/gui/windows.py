import curses


class ScrollWindow(object):
    tab_size = 4
    current_line = 0
    current_indent = 0
    current_column = 0

    def __init__(self, parent_ui, screen, lines=None, cols=None, begin_y=0, begin_x=0):
        self.scroll_line = 0
        self.screen = screen
        self.parent_ui = parent_ui
        if lines is not None and cols is not None:
            self.win = screen.subwin(lines, cols, begin_y, begin_x)
        else:
            self.win = screen.subwin(begin_y, begin_x)
        self.win.keypad(True)
        self.lines = [(i, 0, '', curses.A_DIM) for i in range(self.win.getmaxyx()[0])]
        return self
        #self.render()

    def render(self):
        self.refresh()
        while 1:
            self.on_ch(self.win.getch())

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
        self.win.clear()
        start = self.scroll_line
        end = start + self.win.getmaxyx()[0]
        for line, column, text, attr in self.lines[start:end]:
            self.win.addstr(line - start, column, text, attr)
        self.win.refresh()

    def on_ch(self, cmd):
        win_height = self.win.getmaxyx()[0]
        if cmd in [curses.KEY_DOWN]:
            if self.scroll_line + win_height < len(self.lines):
                self.scroll_line += 1
        elif cmd == curses.KEY_UP:
            if self.scroll_line > 0:
                self.scroll_line -= 1
        elif cmd == 32:
            tmp_scroll = self.scroll_line + win_height
            if tmp_scroll + win_height > len(self.lines):
                tmp_scroll = len(self.lines) - win_height
            self.scroll_line = tmp_scroll

        self.refresh()


class SettingsWindow(ScrollWindow):
    def __init__(self, settings, *args, **kwargs):
        self.settings = settings
        super(SettingsWindow, self).__init__(*args, **kwargs)
        self.add_settings(self.settings)
        self.render()
        return self

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