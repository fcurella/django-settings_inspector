import curses
from settings_inspector.gui import keys


class ScrollWindow(object):
    tab_size = 4
    current_line = 0
    current_indent = 0
    current_column = 0
    current_highlight = 0
    highlight = False

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

    def write(self, text, attr=curses.A_DIM, current_line=None, current_column=None):
        if current_line is None:
            current_line = self.current_line
        if current_column is None:
            current_column = self.current_column

        new_line = (current_line, current_column, text, attr)
        if current_line >= len(self.lines):
            for missing in range(current_line - len(self.lines)):
                empty_line = (len(self.lines) + missing, 0, '', curses.A_DIM)
                self.lines.append(empty_line)
            self.lines.append(new_line)
        else:
            self.lines[current_line] = new_line

    def highlight_line(self, lineno):
        win_height, win_width = self.win.getmaxyx()
        self.current_highlight = lineno
        self.highlight = True
        if self.current_highlight >= (self.scroll_line + win_height):
            self.scroll_line = self.current_highlight - win_height + 1
        elif self.current_highlight < self.scroll_line:
            self.scroll_line = self.current_highlight

        self.refresh()

    def remove_highlight(self):
        self.highlight = False
        self.refresh()

    def highlight_next(self):
        win_height, win_width = self.win.getmaxyx()
        if (self.current_highlight + 1) < len(self.lines):
            if self.highlight:
                self.highlight_line(self.current_highlight + 1)
            else:
                self.highlight_line(self.current_highlight)

    def highlight_prev(self):
        if self.current_highlight > 0:
            if self.highlight:
                self.highlight_line(self.current_highlight - 1)
            else:
                self.highlight_line(self.current_highlight)

    def refresh(self):
        self.win.clear()
        win_height, win_width = self.win.getmaxyx()
        start = self.scroll_line
        end = start + win_height
        for line, column, text, attr in self.lines[start:end]:
            text = (' ' * column) + text
            if line == self.current_highlight and self.highlight:
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
        elif cmd == keys.SPACE:
            self.scroll_page_down()

        elif cmd == curses.KEY_LEFT:
            self.scroll_left()
        elif cmd == curses.KEY_RIGHT:
            self.scroll_right()

        elif cmd == keys.LOWERCASE_X:
            self.highlight_next()
        elif cmd == keys.UPPERCASE_X:
            self.highlight_prev()
