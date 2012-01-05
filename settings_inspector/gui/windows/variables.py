from .base import ScrollWindow
from settings_inspector.gui import keys


class VariablesWindow(ScrollWindow):
    def __init__(self, settings, *args, **kwargs):
        super(VariablesWindow, self).__init__(*args, **kwargs)
        self.root_settings = settings
        self.reset()
        self.render()
        return self

    def reset(self):
        self.settings = {}
        self.current_line = 0
        self.current_column = 0
        self.add_variables()
        self.refresh()

    def add_variables(self):
        for name, variable in self.root_settings.variable_registry.variables.items():
            self.write(u"%s = %s" % (variable.name, variable.value))
            self.next_line()

    def on_ch(self, cmd):
        if cmd == keys.LOWERCASE_S:
            self.parent_ui.show_settings()
        else:
            super(VariablesWindow, self).on_ch(cmd)


class VariableHistoryWindow(ScrollWindow):
    def __init__(self, settings, variable, *args, **kwargs):
        super(VariableHistoryWindow, self).__init__(*args, **kwargs)
        self.root_settings = settings
        self.variable = variable
        self.reset()
        self.render()
        return self

    def reset(self):
        self.settings = {}
        self.current_line = 0
        self.current_column = 0
        self.add_variable()
        self.refresh()

    def add_variable(self):
        for assignment in self.variable.assignment:
            self.write(u"%s" % (assignment))
            self.next_line()
