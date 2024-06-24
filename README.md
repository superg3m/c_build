current project is implicit but you can specify other projects that use c-build to rebuild itself

# Searches for all elements in the current directory of the project
the it cds into that directory calls build bingo
test if project has c_build_config.json
projects_dependencies_to_build = ["ckit"]

its like 80% of the way there heres what I need to figure out
- The replacing of $compiler_type is not going to work anymore. I think I want to just have an override switch and then force it to build
based on the ChildProject

I also think I will make that distinction of:
    Project 
    - ChildProjects (This should actually contain the information needed to build this project I want the object)

ok it sort of works I need to clean it up a ton and think through this more don't worry I have plenty of time
I really should write those essays tho sometime soon I think I vow to write those essays watching Leo its a perfect time no excuses


FULL REWRITE INBOUND

If you import a module that was already imported, it won't replace the functions that were previously imported. You need to remove the module first with Remove-Module, then import it again. I find it convenient to have this function in my profile:

function reload {
  param(
    [parameter(Mandatory=$true)]$Module
  )
  Write-Host;
  try {
    Remove-Module $Module -ea Stop;
  } catch {
    Write-Warning $error[0].Exception.Message;
    Write-Host;
  } finally {
    Import-Module $Module -Verbose;
  }
  Write-Host;
}

WORKS PRETTY WELL RIGHT NOW

eventually add gcc, clang