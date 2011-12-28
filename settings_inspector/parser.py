import re
from .variables import VariableAssignment


regex_import = re.compile('from\s+(\S+)\s+import\s+\*')
regex_assignment = re.compile("([A-Z0-9_]+)\s*=")
regex_import2 = re.compile("(try:)?\s*(from\s+(\S+)\s+import\s+\*)\s*(except.*)?\n*(\s+.+)?")


class Parser(object):
    def __init__(self, setting):
        self.setting = setting
        self.lines = None
        self.reset()

    def reset(self):
        self.imports = []
        self.assignments = []
        self.parse()

    def parse(self):
        if self.lines is None:
            fh = open(self.setting.setting_file_path)
            self.lines = fh.readlines()
            fh.close()
        self.clean_imports()
        self.find_stuff()

    def find_stuff(self):
        names = [name for name in dir(self.setting.setting) if name.isupper()]
        for l, line in enumerate(self.lines):
            for module in self.get_modules(line):
                self.imports.append((l, module))
            for name in self.find_names(line, names):
                variable = self.setting.variable_registry.variables[name]
                self.assignments.append(VariableAssignment(setting=self.setting, variable=variable, line=l, value=self.get_variable_value(name)))

    def find_text(self, text):
        lines = [l for l, line in enumerate(self.lines, 1) if text in line]
        return lines

    def clean_imports(self):
        raw_settings = ''.join(self.lines)
        clean_settings_lines = regex_import2.sub('', raw_settings)

        fake_globals = {
            '__file__': self.setting.setting_file_path
        }
        exec(clean_settings_lines, fake_globals)
        self.raw_setting = dict([(k, v) for k, v in fake_globals.items() if k == k.upper()])

    def get_variable_value(self, varname):
        return self.raw_setting[varname]

    def find_names(self, text, names):
        return [name for name in regex_assignment.findall(text) if name in names]

    def get_modules(self, line):
        "from module import *"
        occurrencies = regex_import.findall(line)
        if occurrencies:
            return occurrencies
        return []
