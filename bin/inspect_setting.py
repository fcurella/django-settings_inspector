#!/usr/bin/env python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__))))

from settings_inspector.setting import Setting
from settings_inspector.gui.inspector import InspectorUI


def main(argv):
    if len(argv) > 1:
        setting_module_path = argv[1]
    else:
        setting_module_path = 'django.conf'
    root_setting = Setting(setting_module_path)
    gui = InspectorUI(root_setting)
    gui.render()

if __name__ == "__main__":
    main(sys.argv)
