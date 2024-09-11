local powershell = io.popen("powershell.exe -NoExit -Command -", "w")

function execute_powershell(command)
    if powershell then
        powershell:write(command .. "\n")
        powershell:flush()
    else
        print("PowerShell process is not running.")
    end
end

-- Function to apply environment variables from the cache file
local function vcvars()
    execute_powershell("../vars.ps1")
    execute_powershell("cl")
end

-- Main function to generate and apply the cache, then compare environment variables
local function main()
    vcvars()
    -- local post_vcvars_env = get_env_vars()
end

-- Entry point
main()

powershell:close()