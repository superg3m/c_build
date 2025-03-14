import os

def IS_WINDOWS():
    return os.name == "nt"

def IS_LINUX():
    return os.name == "posix" and os.uname().sysname == "Linux"

def IS_DARWIN():
    return os.name == "posix" and os.uname().sysname == "Darwin"