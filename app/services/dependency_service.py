import ast
import os
import requests


def get_python_imports(source_code):
    """
    Extract imported modules from Python source code.
    """

    imports = []

    try:
        tree = ast.parse(source_code)

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

    except SyntaxError:
        return []

    return sorted(set(imports))


def get_file_dependencies(raw_url):
    """
    Download a Python file and identify its imported modules.
    """

    try:
        response = requests.get(raw_url, timeout=10)

        if response.status_code != 200:
            return []

        return get_python_imports(response.text)

    except requests.RequestException:
        return []


def is_project_dependency(module_name, project_root):
    """
    Determine whether an imported module belongs to the project.
    """

    return (
        module_name == project_root
        or module_name.startswith(project_root + ".")
    )


def classify_dependencies(imports, project_root="app"):
    """
    Separate project dependencies from external dependencies.
    """

    project_dependencies = []
    external_dependencies = []

    for module in imports:

        if is_project_dependency(module, project_root):
            project_dependencies.append(module)
        else:
            external_dependencies.append(module)

    return {
        "project_dependencies": sorted(set(project_dependencies)),
        "external_dependencies": sorted(set(external_dependencies))
    }


def find_reverse_dependencies(file_imports, target_module):
    """
    Check whether a file imports the target module.
    """

    for imported_module in file_imports:

        if (
            imported_module == target_module
            or imported_module.startswith(target_module + ".")
        ):
            return True

    return False


def get_module_name_from_file(file_path, project_root="app"):
    """
    Convert a Python file path into a Python module name.

    Example:
        app/services/risk_service.py

    becomes:
        app.services.risk_service
    """

    normalized_path = file_path.replace(os.sep, "/")

    if not normalized_path.endswith(".py"):
        return None

    normalized_path = normalized_path[:-3]

    if normalized_path.endswith("/__init__"):
        normalized_path = normalized_path[:-9]

    return normalized_path.replace("/", ".")


def scan_project_dependencies(
    project_directory="app",
    target_module=None
):
    """
    Scan Python files in the project and find files
    that import the target module.
    """

    affected_files = []

    if not target_module:
        return affected_files

    for root, directories, files in os.walk(project_directory):

        directories[:] = [
            directory
            for directory in directories
            if directory != "__pycache__"
        ]

        for filename in files:

            if not filename.endswith(".py"):
                continue

            file_path = os.path.join(root, filename)

            current_module = get_module_name_from_file(file_path)

            if current_module == target_module:
                continue

            try:
                with open(
                    file_path,
                    "r",
                    encoding="utf-8"
                ) as file:
                    source_code = file.read()

                imports = get_python_imports(source_code)

                if find_reverse_dependencies(
                    imports,
                    target_module
                ):
                    affected_files.append(file_path)

            except (OSError, UnicodeDecodeError):
                continue

    return sorted(affected_files)


def get_dependency_impact(affected_file_count):
    """
    Convert the number of affected files into a dependency impact level.
    """

    if affected_file_count >= 3:
        return "High"

    elif affected_file_count >= 1:
        return "Medium"

    return "Low"


def analyze_dependency_impact(
    changed_files,
    project_directory="app"
):
    """
    Analyze dependency impact for changed Python files.
    """

    dependency_analysis = []

    for file in changed_files:

        filename = file.get("filename", "")

        if not filename.endswith(".py"):
            continue

        target_module = get_module_name_from_file(filename)

        if not target_module:
            continue

        affected_files = scan_project_dependencies(
            project_directory=project_directory,
            target_module=target_module
        )

        affected_file_count = len(affected_files)

        dependency_impact = get_dependency_impact(
            affected_file_count
        )

        dependency_analysis.append(
            {
                "file": filename,
                "module": target_module,
                "affected_files": affected_files,
                "affected_file_count": affected_file_count,
                "dependency_impact": dependency_impact
            }
        )

    return dependency_analysis