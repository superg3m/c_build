-- ANSI color codes for terminal output
RED = '\27[91m'
GREEN = '\27[92m'
BLUE = '\27[94m'
CYAN = '\27[96m'
WHITE = '\27[97m'
YELLOW = '\27[93m'
MAGENTA = '\27[95m'
GREY = '\27[90m'
BLACK = '\27[90m'
DEFAULT = '\27[0m'
FATAL = '\27[41m'

-- Initialize indentation level and indent spaces
level = 0
indent_spaces = string.rep(" ", level * 4)

-- Function to increase the indentation level
function UP_LEVEL()
    level = level + 1
    indent_spaces = string.rep(" ", level * 4)
end

-- Function to decrease the indentation level
function DOWN_LEVEL()
    level = level - 1
    indent_spaces = string.rep(" ", level * 4)
end

-- Function to print formatted messages with different colors based on the level
function FORMAT_PRINT(msg)
    local color_lookup = {GREEN, BLUE, YELLOW, MAGENTA, CYAN, RED}
    local color = color_lookup[(level % #color_lookup) + 1]
    if msg then
        print(string.format("%s%s%s%s", color, indent_spaces, msg, DEFAULT))
    end
end

-- Function to print normal messages without color
function NORMAL_PRINT(msg)
    if msg then
        print(indent_spaces .. msg)
    end
end

-- Function to print fatal error messages with a red background
function FATAL_PRINT(msg)
    if msg then
        print(string.format("%s%s%s%s", FATAL, indent_spaces, msg, DEFAULT))
    end
end

-- Function to perform a git pull operation in a given directory
function GIT_PULL(path)
    local current_directory = io.popen("pwd"):read("*l") -- Get the current directory
    os.execute("cd " .. path)
    os.execute("git fetch origin -q")
    os.execute("git reset --hard origin/main -q")
    os.execute("git pull -q")
    os.execute("cd " .. current_directory)
end
