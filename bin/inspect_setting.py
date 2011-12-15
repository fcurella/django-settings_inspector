#!/usr/bin/env python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__))))
from settings_inspector.setting import Setting


def main(setting_module_path='django.conf'):
    root_setting = Setting(setting_module_path)

if __name__ == "__main__":
    main(sys.argv[1])
