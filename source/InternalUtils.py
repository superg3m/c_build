from .ColorUtils import *

level = 0
indent_spaces = " " * (level * 4)

def FORMAT_PRINT(msg):
    global indent_spaces
    color_lookup = [GREEN, BLUE, YELLOW, MAGENTA, CYAN, RED]
    color = color_lookup[level % len(color_lookup)]
    if msg:
        print(f"{color}{indent_spaces}{msg}{DEFAULT}")

def NORMAL_PRINT(msg):
    global indent_spaces
    if msg:
        print(f"{indent_spaces}{msg}")

def WARN_PRINT(msg):
    global indent_spaces
    color = YELLOW
    if msg:
        print(f"{color}{indent_spaces}{msg}{DEFAULT}")

def FATAL_PRINT(msg):
    global indent_spaces
    if msg:
        print(f"{FATAL}{indent_spaces}{msg}{DEFAULT}")