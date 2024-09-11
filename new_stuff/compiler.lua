-- Constants and enums equivalent
CompilerType = {
    INVALID = 0,
    CL = 1,
    GCC_CC_CLANG = 2
}

CompilerAction = {
    NO_ACTION = 0,
    WARNING_LEVEL = 1,
    DISABLE_SPECIFIC_WARNING = 2,
    WARNING_AS_ERRORS = 3,
    COMPILE_TIME_DEFINES = 4,
    NO_LOGO = 5,
    STD_VERSION = 6,
    REPORT_FULL_PATH = 7,
    OBJECTS_ONLY = 8,
    OUTPUT = 9,
    MULTI_THREADING = 10,
    ADDRESS_SANITIZER = 11
}

COMPILER_LOOKUP_TABLE = {
        [CompilerType.CL] = {
            [CompilerAction.WARNING_LEVEL] = "/W",             -- Warning level flag for cl
            [CompilerAction.DISABLE_SPECIFIC_WARNING] = "/wd", -- Disable specific warning flag for cl
            [CompilerAction.WARNING_AS_ERRORS] = "/WX",        -- Treat warnings as errors flag for cl
            [CompilerAction.COMPILE_TIME_DEFINES] = "/D",      -- Compile time defines flag for cl
            [CompilerAction.NO_LOGO] = "/nologo",              -- No logo flag for cl
            [CompilerAction.STD_VERSION] = "/std:",            -- C/C++ standard version flag for cl
            [CompilerAction.REPORT_FULL_PATH] = "/FC",         -- Full report flag for cl
            [CompilerAction.OBJECTS_ONLY] = "/c",              -- Compile only (don't link) for cl
            [CompilerAction.OUTPUT] = "/Fe",                   -- Output file flag for cl
            [CompilerAction.MULTI_THREADING] = "/MP",          -- Multi-threading flag for cl
            [CompilerAction.ADDRESS_SANITIZER] = "/fsanitize=address", -- Address sanitizer flag (example for cl)
        },
        [CompilerType.GCC_CC_CLANG] = {
            [CompilerAction.WARNING_LEVEL] = "-Wall",           -- Warning level flag for gcc, clang
            [CompilerAction.DISABLE_SPECIFIC_WARNING] = "-Wno-", -- Disable specific warning flag for gcc, clang
            [CompilerAction.WARNING_AS_ERRORS] = "-Werror",     -- Treat warnings as errors flag for gcc, clang
            [CompilerAction.COMPILE_TIME_DEFINES] = "-D",       -- Compile time defines flag for gcc, clang
            [CompilerAction.NO_LOGO] = "",                      -- No equivalent for no-logo in gcc/clang
            [CompilerAction.STD_VERSION] = "-std=",             -- C/C++ standard version flag for gcc, clang
            [CompilerAction.REPORT_FULL_PATH] = "-fmacro-backtrace-limit=0", -- Full report flag for gcc, clang
            [CompilerAction.OBJECTS_ONLY] = "-c",               -- Compile only (don't link) flag for gcc, clang
            [CompilerAction.OUTPUT] = "-o",                     -- Output file flag for gcc, clang
            [CompilerAction.MULTI_THREADING] = "-pthread",      -- Multi-threading flag for gcc, clang
            [CompilerAction.ADDRESS_SANITIZER] = "-fsanitize=address", -- Address sanitizer flag for gcc, clang
        }
    }

-- Compiler class equivalent in Lua
Compiler = {}
Compiler.__index = Compiler

function Compiler:new(compiler_name, std_version)
    local obj = {
        name = compiler_name,
        std_version = std_version or "c11",
        should_debug_with_visual_studio = false,
        should_rebuild_project_dependencies = false,
        type = nil,
        compiler_command = {compiler_name},
        action = CompilerAction.NO_ACTION
    }
    obj.type = obj:choose_compiler_type()
    setmetatable(obj, self)
    return obj
end

function Compiler:choose_compiler_type()
    if self.name == "cl" then
        return CompilerType.CL
    elseif self.name == "gcc" or self.name == "cc" or self.name == "clang" then
        return CompilerType.GCC_CC_CLANG
    else
        FATAL_PRINT("Compiler " .. self.name .. " is not supported")
        os.exit(-15)
    end
end

function Compiler:get_compiler_lookup()
    if self.action == CompilerAction.NO_ACTION then
        FATAL_PRINT("Compiler No Action")
        os.exit(-15)
    end
    return COMPILER_LOOKUP_TABLE[self.type][self.action]
end

function Compiler:set_action(action)
    self.action = action
end

function Compiler:set_warning_level(warning_level_string)
    if not warning_level_string then return end
    self:set_action(CompilerAction.WARNING_LEVEL)
    local flag = self:get_compiler_lookup()
    table.insert(self.compiler_command, flag .. warning_level_string)
end

function Compiler:disable_specific_warnings(specific_warnings)
    self:set_action(CompilerAction.DISABLE_SPECIFIC_WARNING)
    local flag = self:get_compiler_lookup()
    for _, warning in ipairs(specific_warnings) do
        if warning then
            table.insert(self.compiler_command, flag .. warning)
        end
    end
end

function Compiler:set_treat_warnings_as_errors(is_error)
    if not is_error then return end
    self:set_action(CompilerAction.WARNING_AS_ERRORS)
    local flag = self:get_compiler_lookup()
    table.insert(self.compiler_command, flag)
end

function Compiler:set_compile_time_defines(compile_time_defines)
    self:set_action(CompilerAction.COMPILE_TIME_DEFINES)
    local define_flag = self:get_compiler_lookup()
    for _, define in ipairs(compile_time_defines) do
        if define then
            table.insert(self.compiler_command, define_flag .. define)
        end
    end
end

function Compiler:compile_procedure(procedure, is_debug)
    for _, source in ipairs(procedure.source_files) do
        if source then
            table.insert(self.compiler_command, source)
        end
    end

    -- Add no logo flag
    self:set_action(CompilerAction.NO_LOGO)
    local no_logo_flag = self:get_compiler_lookup()
    if no_logo_flag then
        table.insert(self.compiler_command, no_logo_flag)
    end

        -- Add std version flag
    self:set_action(CompilerAction.STD_VERSION)
    local std_version_flag = self:get_compiler_lookup()
    table.insert(self.compiler_command, std_version_flag .. self.std_version)

    -- Add full report
    self:set_action(CompilerAction.REPORT_FULL_PATH)
    local report_full_path_flag = self:get_compiler_lookup()
    if report_full_path_flag then
        table.insert(self.compiler_command, report_full_path_flag)
    end

    -- Add object flag
    if procedure.should_build_static_lib then
        self:set_action(CompilerAction.OBJECTS_ONLY)
        local object_flag = self:get_compiler_lookup()
        table.insert(self.compiler_command, object_flag)
    else
        if procedure.should_build_dynamic_lib then
            if self.name == "cl" then
                table.insert(self.compiler_command, "/LD")
            else
                table.insert(self.compiler_command, "-shared")
            end
        end

        -- Add output flag
        self:set_action(CompilerAction.OUTPUT)
        local output_flag = self:get_compiler_lookup()
        table.insert(self.compiler_command, output_flag)
        table.insert(self.compiler_command, procedure.output_name)
    end

    -- Add multi-threading flag
    self:set_action(CompilerAction.MULTI_THREADING)
    local multi_threading_flag = self:get_compiler_lookup()
    if multi_threading_flag then
        table.insert(self.compiler_command, multi_threading_flag)
    end

    -- Add optimization flag
    if is_debug then
        if self.type == CompilerType.CL then
            table.insert(self.compiler_command, "/Od")
            table.insert(self.compiler_command, "/Zi")
        else
            table.insert(self.compiler_command, "-g")
        end

        -- Add address sanitizer flag
        if package.config:sub(1,1) ~= '\\' then
            self:set_action(CompilerAction.ADDRESS_SANITIZER)
            local address_sanitizer_flag = self:get_compiler_lookup()
            table.insert(self.compiler_command, address_sanitizer_flag)
        end
    else
        if self.type == CompilerType.CL then
            table.insert(self.compiler_command, "/O2")
        else
            table.insert(self.compiler_command, "-O2")
        end
    end

    -- Add include paths
    for _, include_path in ipairs(procedure.include_paths) do
        if include_path then
            if self.type == CompilerType.CL then
                table.insert(self.compiler_command, "/I" .. include_path)
            else
                table.insert(self.compiler_command, "-I" .. include_path)
            end
        end
    end

    -- Add additional compiler flags
    -- for _, flag in ipairs(procedure.compiler_inject_into_args) do
    --     if flag then
    --         table.insert(self.compiler_command, flag)
    --     end
    -- end

    if not procedure.should_build_static_lib then
        if #procedure.additional_libs > 0 and procedure.additional_libs[1] and self.type == CompilerType.CL then
            table.insert(self.compiler_command, "/link")
        end
        for _, lib in ipairs(procedure.additional_libs) do
            if lib then
                table.insert(self.compiler_command, lib)
            end
        end
    end

    -- Create build directory if it doesn't exist
    local build_dir = procedure.build_directory
    if not io.open(build_dir, "r") then
        os.execute("mkdir " .. build_dir)
    end

    -- Change to build directory
    local current_dir = io.popen("cd"):read()
    os.execute("cd " .. build_dir)

    -- Execute compiler command
    local result = io.popen(table.concat(self.compiler_command, " "), "r")
    local output = result:read("*a")
    result:close()

    -- Print output
    for line in output:gmatch("([^\n]*)\n") do
        NORMAL_PRINT(line)
    end

    -- Check for errors
    if procedure.should_build_static_lib then
        -- Build static lib
        -- NOTE: This will need to be implemented
    elseif result ~= 0 then
        FATAL_PRINT("FAILED TO COMPILE!")
    else
        FORMAT_PRINT("Compilation of " .. procedure.output_name .. " successful")
    end

    -- Reset compiler command
    self.compiler_command = {self.name}

    -- Change back to original directory
    os.execute("cd " .. current_dir)
end

-- Example usage:
local compiler = Compiler:new("gcc", "c11")
compiler:set_warning_level("3")
compiler:disable_specific_warnings({""})
compiler:set_treat_warnings_as_errors(true)

local procedure = {
    source_files = {"main.c", "utils.c"},
    include_paths = {"/usr/include", "/usr/local/include"},
    additional_libs = {"-lm", "-lpthread"},
    output_name = "my_program",
    build_directory = "build",
}

compiler:compile_procedure(procedure, true)