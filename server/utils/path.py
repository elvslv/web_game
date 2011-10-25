import os
from os.path import join

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(CURRENT_PATH, "../../"))

def join(*paths):
    if len(paths) == 1:
        return os.path.normpath(os.path.join(PROJECT_ROOT, *paths))
    else:
        return os.path.join(*paths)
