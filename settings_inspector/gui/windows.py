import curses


class ScrollWindow(object):
    tab_size = 4
    current_line = 0
    current_indent = 0
    current_column = 0
    current_highlight = -1

    def __init__(self, parent_ui, screen, lines=None, cols=None, begin_y=0, begin_x=0):
        self.scroll_line = 0
        self.scroll_column = 0
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

    def untab(self):
        self.current_indent = self.current_indent - 1
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

    def highlight_line(self, lineno):
        win_height, win_width = self.win.getmaxyx()
        self.current_highlight = lineno
        if self.current_highlight >= (self.scroll_line + win_height):
            self.scroll_line = self.current_highlight - win_height + 1
        elif self.current_highlight < self.scroll_line:
            self.scroll_line = self.current_highlight

        self.refresh()

    def remove_highlight(self):
        self.current_highlight = -1
        self.refresh()

    def highlight_next(self):
        win_height, win_width = self.win.getmaxyx()
        if (self.current_highlight + 1) < len(self.lines):
            self.highlight_line(self.current_highlight + 1)

    def highlight_prev(self):
        if self.current_highlight > 0:
            self.highlight_line(self.current_highlight - 1)

    def refresh(self):
        self.win.clear()
        win_height, win_width = self.win.getmaxyx()
        start = self.scroll_line
        end = start + win_height
        for line, column, text, attr in self.lines[start:end]:
            text = (' ' * column) + text
            if line == self.current_highlight:
                attr = curses.A_STANDOUT
            try:
                self.win.addstr(line - start, 0, text[self.scroll_column:self.scroll_column + win_width], attr)
            except curses.error:
                pass
        self.win.refresh()

    def scroll_down(self):
        win_height, win_width = self.win.getmaxyx()
        if self.scroll_line + win_height < len(self.lines):
            self.scroll_line += 1
            self.refresh()

    def scroll_page_down(self):
        win_height, win_width = self.win.getmaxyx()
        tmp_scroll = self.scroll_line + win_height
        if tmp_scroll + win_height > len(self.lines):
            tmp_scroll = len(self.lines) - win_height
        self.scroll_line = tmp_scroll
        self.refresh()

    def scroll_up(self):
        if self.scroll_line > 0:
            self.scroll_line -= 1
            self.refresh()

    def scroll_left(self):
        if self.scroll_column > 0:
            self.scroll_column -= 1
            self.refresh()

    def scroll_right(self):
        win_height, win_width = self.win.getmaxyx()
        max_lines_length = max([len(line[2]) for line in self.lines])
        if self.scroll_column + win_width < max_lines_length:
            self.scroll_column += 1
            self.refresh()

    def on_ch(self, cmd):
        if cmd in [curses.KEY_DOWN, 10]:
            self.scroll_down()
        elif cmd == curses.KEY_UP:
            self.scroll_up()
        elif cmd == 32:
            self.scroll_page_down()

        elif cmd == curses.KEY_LEFT:
            self.scroll_left()
        elif cmd == curses.KEY_RIGHT:
            self.scroll_right()

        elif cmd == 120:
            self.highlight_next()
        elif cmd == 88:
            self.highlight_prev()


class SettingsWindow(ScrollWindow):
    def __init__(self, settings, *args, **kwargs):
        self.settings = settings
        super(SettingsWindow, self).__init__(*args, **kwargs)
        self.add_settings(self.settings)
        self.render()
        return self

    def add_settings(self, setting):
        self.write(u"- %s" % setting, attr=curses.A_BOLD)
        lines = setting.parser.lines
        lineno_pad = len(str(len(lines)))

        for lineno, line in enumerate(lines, 1):
            self.next_line()
            self.write(u"%s: %s" % (str(lineno).rjust(lineno_pad), line))
            if lineno - 1 in setting.children_settings:
                self.next_line()
                self.tab()
                self.add_settings(setting.children_settings[lineno - 1])
                self.untab()

    def add_variables(self, setting):
        self.tab()
        for i, assignment in enumerate(setting.assignments):
            self.next_line()
            self.write(u"%s" % assignment)
