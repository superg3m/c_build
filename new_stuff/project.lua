local os = require("os")
local io = require("io")
local table = require("table")
local string = require("string")

local Compiler = loadfile("./compiler.lua")()
local Procedure = loadfile("./procedure.lua")()
local utility = loadfile("./utility.lua")()

local Project = {}
Project.__index = Project

function Project:new(name, compiler_name, std_version, github_root)
  local instance = setmetatable({}, Project)
  instance.name = name
  instance.std_version = std_version or "c11"
  instance.compiler_name = compiler_name
  instance.github_root = github_root or "https://github.com/superg3m"
  instance.internal_compiler = Compiler:new(compiler_name, std_version)
  instance.should_debug_with_visual_studio = false
  instance.should_rebuild_project_dependencies = false
  instance.dependencies = {}
  instance.procedures = {}
  instance.executable_procedures = {}

  instance:assert_std_is_valid()

  return instance
end

function Project:assert_std_is_valid()
  local acceptable_versions = {
    [0] = {"c11", "c17", "clatest"},  -- CL
    [1] = {"c89", "c90", "c99", "c11", "c17", "c18", "c23"},  -- GCC_CC_CLANG
  }

  local ret = false
  for _, version in ipairs(acceptable_versions[self.internal_compiler.type]) do
    if version == self.std_version then
      ret = true
      break
    end
  end

  if not ret then
    print("Std version: " .. self.std_version .. " not supported, choose one of these: " .. table.concat(acceptable_versions[self.internal_compiler.type.value], ", "))
  end
end

function Project:set_executables_to_run(executable_names)
  local executable_map = {}
  for _, proc in ipairs(self.procedures) do
    if proc then
      executable_map[proc.output_name] = proc
    end
  end

  for _, executable_name in ipairs(executable_names) do
    if executable_map[executable_name] then
      table.insert(self.executable_procedures, executable_map[executable_name])
    else
      print("Invalid executable name(s), expected: " .. table.concat(table.keys(executable_map), ", ") .. " | got: " .. executable_name)
      os.exit(-15)
    end
  end
end

function Project:add_procedure(build_directory)
  local proc = Procedure:new(build_directory)
  table.insert(self.procedures, proc)

  if not utility.isdir(build_directory) then
    utility.mkdir(build_directory)
  end

  return proc
end

function Project:build()
  print("|----------------------------------------- Start -----------------------------------------|")
  self.internal_compiler:compile_procedures(self.procedures)

  local start_time = utility.clock()
  if self.compiler_name == "cl" then
    utility.vcvars()
  end

  for _, dependency_string in ipairs(self.dependencies) do
    if not utility.isdir(dependency_string) then
      print("missing " .. dependency_string .. " cloning...")
      os.execute("git clone " .. self.github_root .. "/" .. dependency_string .. ".git")
    end

    local cached_current_directory_global = utility.getcwd()
    utility.chdir(dependency_string)
    os.execute("lua c_build.lua " .. self.compiler_name)
    utility.chdir(cached_current_directory_global)
  end

  local end_time = utility.clock()
  local elapsed_time = end_time - start_time
  print("|------------------------------- Time elapsed: " .. tostring(elapsed_time) .. " seconds -------------------------------|")
end

function Project:inject_as_argument(arg)
  table.insert(self.internal_compiler.compiler_command, arg)
end

function Project:set_project_dependencies(project_dependency_strings)
  for _, dependency_string in ipairs(project_dependency_strings) do
    if dependency_string then
      table.insert(self.dependencies, dependency_string)
    end
  end
end

function Project:set_rebuild_project_dependencies(should_rebuild_project_dependencies)
  self.should_rebuild_project_dependencies = should_rebuild_project_dependencies
end

function Project:set_debug_with_visual_studio(should_debug_with_visual_studio)
  self.should_debug_with_visual_studio = should_debug_with_visual_studio
end

function Project:set_compiler_warning_level(warning_level_string)
  self.internal_compiler:set_warning_level(warning_level_string)
end

function Project:disable_specific_warnings(specific_warnings)
  self.internal_compiler:disable_specific_warnings(specific_warnings)
end

function Project:set_compile_time_defines(compile_time_defines)
  self.internal_compiler:set_compile_time_defines(compile_time_defines)
end

function Project:set_treat_warnings_as_errors(is_error)
  self.internal_compiler:set_treat_warnings_as_errors(is_error)
end

return Project