from Project import Project, JSON_CONFIG_PATH, parse_json_file

project: Project = Project(parse_json_file(JSON_CONFIG_PATH))
project.build_project(False)
