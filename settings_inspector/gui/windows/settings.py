import curses
from bisect import bisect_right
from .base import ScrollWindow


class SettingsWindow(ScrollWindow):
    def __init__(self, settings, *args, **kwargs):
        super(SettingsWindow, self).__init__(*args, **kwargs)
        self.root_settings = settings
        self.reset()
        self.render()
        return self

    def reset(self):
        self.settings = {}
        self.current_line = 0
        self.current_column = 0
        self.add_settings(self.root_settings)
        self.refresh()

    def lineno_pad(self, setting):
        lines = setting.parser.lines
        return len(str(len(lines))) + 1

    def add_settings(self, setting, line=0):
        self.settings[line] = (setting, self.current_column)
        title = u"- %s" % setting
        self.write(title, attr=curses.A_BOLD)
        lineno_pad = self.lineno_pad(setting)
        lines = setting.parser.lines

        for lineno, line in enumerate(lines, 1):
            self.next_line()
            text = u"%s: %s" % (str(lineno).rjust(lineno_pad), line)

            assignment = setting.assignments_lines.get(lineno - 1, False)
            if assignment and assignment.is_overridden():
                text = '*' + text[1:]
            self.write(text)
            if lineno - 1 in setting.children_settings:
                self.next_line()
                self.tab()
                self.add_settings(setting.children_settings[lineno - 1], self.current_line)
                self.untab()

    def add_variables(self, setting):
        self.tab()
        for i, assignment in enumerate(setting.assignments):
            self.next_line()
            self.write(u"%s" % assignment)

    def setting_line(self, setting):
        return [line for (line, _setting) in self.settings.items() if _setting[0] == setting][0]

    def get_setting_at_line(self, lineno):
        k_no = bisect_right(self.settings.keys(), lineno) - 1
        k = self.settings.keys()[k_no]
        return self.settings[k][0]
