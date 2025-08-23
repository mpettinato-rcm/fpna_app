#!/usr/bin/env python
import os
import sys

# Force Python to include the project directory in its search path
sys.path.append(os.path.dirname(__file__))

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
