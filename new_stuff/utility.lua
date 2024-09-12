-- ANSI color codes for terminal output
local RED = '\27[91m'
local GREEN = '\27[92m'
local BLUE = '\27[94m'
local CYAN = '\27[96m'
local WHITE = '\27[97m'
local YELLOW = '\27[93m'
local MAGENTA = '\27[95m'
local GREY = '\27[90m'
local BLACK = '\27[90m'
local DEFAULT = '\27[0m'
local FATAL = '\27[41m'

-- Initialize indentation level and indent spaces
local level = 0
local indent_spaces = string.rep(" ", level * 4)

-- Function to increase the indentation level
local function UP_LEVEL()
    level = level + 1
    indent_spaces = string.rep(" ", level * 4)
end

-- Function to decrease the indentation level
local function DOWN_LEVEL()
    level = level - 1
    indent_spaces = string.rep(" ", level * 4)
end

-- Function to print formatted messages with different colors based on the level
local function FORMAT_PRINT(msg)
    local color_lookup = {GREEN, BLUE, YELLOW, MAGENTA, CYAN, RED}
    local color = color_lookup[(level % #color_lookup) + 1]
    if msg then
        print(string.format("%s%s%s%s", color, indent_spaces, msg, DEFAULT))
    end
end

-- Function to print normal messages without color
local function NORMAL_PRINT(msg)
    if msg then
        print(indent_spaces .. msg)
    end
end

-- Function to print fatal error messages with a red background
local function FATAL_PRINT(msg)
    if msg then
        print(string.format("%s%s%s%s", FATAL, indent_spaces, msg, DEFAULT))
    end
end

-- Function to perform a git pull operation in a given directory
local function GIT_PULL(path)
    local current_directory = io.popen("pwd"):read("*l") -- Get the current directory
    os.execute("cd " .. path)
    os.execute("git fetch origin -q")
    os.execute("git reset --hard origin/main -q")
    os.execute("git pull -q")
    os.execute("cd " .. current_directory)
end

local powershell_terminal = io.popen("powershell.exe -NoExit -Command -", "w")
local function execute_powershell(command)
    if powershell_terminal then
        powershell_terminal:write(command .. "\n")
        powershell_terminal:flush()
    else
        print("PowerShell process is not running.")
    end
end

local function close_powershell_terminal()
    powershell_terminal:close()
end

local function vcvars()
    execute_powershell("../vars.ps1")
end

function relpath(path)
    return path:gsub("^/+", ""):gsub("/$", "")
end

function listdir(path)
    local files = {}
    for file in powershell_terminal:write("ls -1 " .. path .. "\n"):lines() do
    table.insert(files, file)
    end
    return files
end

function isdir(path)
    local f = io.open(path .. "/.", "r")
    if f then
    f:close()
    return true
    end
    return false
end

function getcwd()
    local val = execute_powershell("pwd"):read("*l")
    print("VALUE: " .. val)
    return val
end

function chdir(path)
  os.execute("cd " .. path)
end

function mkdir(path)
  os.execute("mkdir " .. path)
end

-- Return the module table
return {
    FORMAT_PRINT = FORMAT_PRINT,
    NORMAL_PRINT = NORMAL_PRINT,
    FATAL_PRINT = FATAL_PRINT,
    GIT_PULL = GIT_PULL,
    UP_LEVEL = UP_LEVEL,
    DOWN_LEVEL = DOWN_LEVEL,
    vcvars = vcvars,
    relpath = relpath,
    listdir = listdir,
    isdir = isdir,
    getcwd = getcwd,
    chdir = chdir,
    mkdir = mkdir,
}
