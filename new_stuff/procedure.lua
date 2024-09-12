local os = require("os")
local io = require("io")
local table = require("table")
local string = require("string")

local utility = loadfile("./utility.lua")()

local Procedure = {}
Procedure.__index = Procedure

function Procedure:new(build_directory)
  local instance = setmetatable({}, Procedure)
  instance.build_directory = build_directory
  instance.output_name = ""

  instance.should_build_executable = false
  instance.should_build_static_lib = false
  instance.should_build_dynamic_lib = false

  instance.source_files = {}
  instance.include_paths = {}
  instance.additional_libs = {}
  instance.compile_time_defines = {}

  return instance
end

function Procedure:resolve_source_glob(maybe_source_glob, is_recursive)
  local resolved_files = {}

  if string.find(maybe_source_glob, "*.c") then
    local source_dir = string.match(maybe_source_glob, "(.-)/") or "."
    local current_directory = utility.getcwd()

    utility.chdir(self.build_directory)
    utility.chdir(source_dir)

    if is_recursive then
      for root, dirs, files in utility.walk(utility.getcwd()) do
        for _, file in ipairs(files) do
          if string.find(file, "%.c$") then
            local relative_path = source_dir .. "/" .. utility.relpath(root .. "/" .. file):gsub("\\", "/")
            table.insert(resolved_files, relative_path)
          end
        end
      end
    else
      for _, file in ipairs(utility.listdir(utility.getcwd())) do
        if string.find(file, "%.c$") then
          local relative_path = utility.relpath(source_dir .. "/" .. file):gsub("\\", "/")
          table.insert(resolved_files, relative_path)
        end
      end
    end

    utility.chdir(current_directory)
  elseif string.find(maybe_source_glob, "%.c$") then
    table.insert(resolved_files, maybe_source_glob)
  end

  return resolved_files
end

function Procedure:set_output_name(output_name)
  self.output_name = output_name

  local extension = string.match(output_name, "%.(.-)$"):lower()

  if extension == ".exe" then
    self.should_build_executable = true
  elseif extension == ".lib" or extension == ".a" then
    self.should_build_static_lib = true
  elseif extension == ".so" or extension == ".o" or extension == ".dylib" then
    self.should_build_dynamic_lib = true
  else
    self.should_build_executable = true  -- For Linux
  end
end

function Procedure:set_source_files(source_files, recursive_search)
  for _, source_glob in ipairs(source_files) do
    local resolved_files = self:resolve_source_glob(source_glob, recursive_search)
    table.insert(self.source_files, resolved_files)
  end
end

function Procedure:set_include_paths(include_paths)
  self.include_paths = include_paths
end

function Procedure:set_additional_libs(additional_libs)
  self.additional_libs = additional_libs
end

function Procedure:set_compile_time_defines(compile_time_defines)
  self.compile_time_defines = compile_time_defines
end

-- Helper functions
function os.walk(path)
  local function yield(root, dirs, files)
    coroutine.yield(root, dirs, files)
  end

  local function walk(path)
    local stack = {{path, {}}}
    while #stack > 0 do
      local root, dirs = table.remove(stack)
      local files = {}
      for _, file in ipairs(os.listdir(root)) do
        if os.isdir(root .. "/" .. file) then
          table.insert(dirs, file)
        else
          table.insert(files, file)
        end
      end
      yield(root, dirs, files)
      for _, dir in ipairs(dirs) do
        table.insert(stack, {root .. "/" .. dir, {}})
      end
    end
  end

  return coroutine.wrap(walk)
end

return Procedure