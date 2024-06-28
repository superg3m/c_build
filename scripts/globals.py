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

JSON_CONFIG_PATH: str = "./c_build_config.json"

level = 0
indent_spaces = " " * (level * 4)


def increase_global_level():
    global level, indent_spaces
    level += 1
    indent_spaces = " " * (level * 4)


def FORMAT_PRINT(msg: str, color: str):
    global indent_spaces
    print(f"{color}{indent_spaces}{msg}{DEFAULT}")
