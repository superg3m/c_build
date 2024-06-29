import os

RED: str = '\033[91m'
GREEN: str = '\033[92m'
BLUE: str = '\033[94m'
CYAN: str = '\033[96m'
WHITE: str = '\033[97m'
YELLOW: str = '\033[93m'
MAGENTA: str = '\033[95m'
GREY: str = '\033[90m'
BLACK: str = '\033[90m'
DEFAULT: str = '\033[0m'
FATAL = "\033[41m"

JSON_CONFIG_PATH: str = "./c_build_config.json"

level = 0
indent_spaces = " " * (level * 4)


def UP_LEVEL():
    global level, indent_spaces
    level += 1
    indent_spaces = " " * (level * 4)


def DOWN_LEVEL():
    global level, indent_spaces
    level -= 1
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


def FATAL_PRINT(msg):
    global indent_spaces
    if msg:
        print(f"{FATAL}{indent_spaces}{msg}{DEFAULT}")


def GIT_PULL_OR_CLONE(path: str):
    current_directory = os.getcwd()
    os.chdir(path)
    os.system("git fetch origin -q")
    os.system("git reset --hard origin/main -q")
    os.system("git pull -q")
    os.chdir(current_directory)
