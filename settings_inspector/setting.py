import os
from .parser import Parser


class Setting(object):
    """
    Properties:

    * parent_setting = Setting()
    * children_settings = {}
    * setting = <module>
    * setting_file_path = ''
    * parser = Parser()
    * assignments = [VariableAssignment(),]
    """
    def __init__(self, setting_module_path, parent_setting=None):
        self.parent_setting = parent_setting
        self.children_settings = {}
        if setting_module_path == 'django.conf':
            setting_module_path = os.environ['DJANGO_SETTINGS_MODULE']
        parent_setting_path, leaf_setting_path = self.get_module_paths(setting_module_path)
        self.setting = getattr(__import__(parent_setting_path), leaf_setting_path)
        if self.setting is not None:
            self.setting_module_path = setting_module_path
            self.setting_file_path = self.get_settings_filepath()
            self.parser = Parser(self)
            self.parse()

    def __unicode__(self):
        return u"%s -- %s" % (self.setting_module_path, self.setting_file_path)

    def get_module_paths(self, module_path):
        if module_path.startswith('.') and self.parent_setting is not None:
            leaf_setting_path = module_path.split('.')[-1]
            parent_setting_path = self.parent_setting.setting_module_path.rsplit('.', 1)[0] + '.' + leaf_setting_path
            return parent_setting_path, leaf_setting_path
        return module_path, module_path.split('.')[-1]

    def parse(self):
        imports = self.parser.imports
        for line, module_path in imports:
            module_absolute_path = self.get_module_paths(module_path)[0]
            self.children_settings[line] = Setting(module_absolute_path, parent_setting=self)

        self.assignments = self.parser.assignments

    def get_settings_filepath(self):
        return self.setting.__file__.rsplit('.', 1)[0] + '.py'

    def get_assignments_by_name(self, varname):
        return [assignment for assignment in self.assignments if assignment.variable.name == varname]

    def get_variable_history(self, varname):
        stack = self.get_assignments_by_name(varname)
        for setting in self.children_settings.values():
            stack.extend(setting.get_variable_history(varname))
        return stack
