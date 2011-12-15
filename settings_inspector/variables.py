from collections import defaultdict


class VariableDefaultDict(defaultdict):
    def __missing__(self, key):
        return Variable(name=key)


class Variable(object):
    def __init__(self, name):
        self.name = name
        self.assignments = []

    def get_assignments_from_setting(self, setting):
        for i, assignment in enumerate(reversed(self.assignments), 1):
            if assignment.setting == setting:
                return self.assignments[:i]
        return []


class VariableAssignment(object):
    def __init__(self, variable, setting, line, value):
        self.variable = variable
        self.setting = setting
        self.line = line
        self.value = value
        self.variable.assignments.append(self)

    def __unicode__(self):
        return u"@%d: %s: %s" % (self.line, self.variable.name, self.value)

    def is_overridden(self):
        return self.variable.assignments.index(self) < (len(self.variable.assignments) - 1)


class Registry(object):
    variables = VariableDefaultDict()


variable_registry = Registry()
