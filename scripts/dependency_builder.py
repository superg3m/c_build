import os

from scripts import Project
from scripts.globals import FORMAT_PRINT, GIT_PULL


class DependencyBuilder:
    def __init__(self, github_root: str):
        self.github_root = github_root
        self.debug = debug

    def build_dependency(self, parent_name: str, dependency: Project):
        FORMAT_PRINT(f"[{self, parent_name}] depends on:")

        FORMAT_PRINT(f"- {dependency.name}")
        if not os.path.exists(dependency.name):
            FORMAT_PRINT(f"missing {dependency.name} cloning...")
            os.system(f"git clone {self.github_root}/{dependency.name}.git")
        else:
            GIT_PULL(dependency.name)

        if not os.path.exists("c-build"):
            os.system("git clone https://github.com/superg3m/c-build.git")
        else:
            GIT_PULL("c-build")

        cached_current_directory_global = os.getcwd()
        os.chdir(dependency.name)
        dependency.build_project(self.debug)
        os.chdir(cached_current_directory_global)

    def build_dependencies(self, parent_name, project_dependencies):
        for dependency in project_dependencies:
            self.build_dependency(parent_name, dependency)