import os
from pathlib import Path
import ast
import re
import tomllib

from langchain_core.tools import tool
import subprocess


def scan_repository(folder_path:str):

    """Scan a repository and extract metadata from Python files."""
    #check path exists
    repo_path = Path(folder_path).resolve()

    if not repo_path.exists():
        raise FileNotFoundError(f"{folder_path} does not exist")

    if not repo_path.is_dir():
        raise ValueError(f"{folder_path} is not a directory")
    
    repo_metadata = []

    try:
        for dirpath,dirname,filename in os.walk(repo_path):

            #dont enter unnecessary directories like .git,venv,env,build,dist
            if any(exclude in dirpath for exclude in [".git","venv","env","build","dist"]):
                continue
            for file in filename:
                if file.endswith(".py"):
                    full_path = os.path.join(
                        dirpath,
                        file
                    )
                    #extrac metadata of the file_path
                    file_metadata = extract_metadata(full_path,repo_path)
                    repo_metadata.append(file_metadata)

        return repo_metadata
    except Exception as e:
        raise e



#extract import and function

def extract_metadata(file_path:Path,repo_path:Path):

    # extract import ,funtion ,classes from every files
    # file_path = Path(file_path)

    if file_path:
        try:
            source = file_path.read_text(encoding="utf-8")

            tree = ast.parse(source)

            imports = []
            function = []
            classes = []
            call_functions = []
            method_calls = []

            for node in ast.walk(tree):
                #import x
                if isinstance(node,ast.Import):

                    for name in node.names:
                        imports.append({
                            "module":name.name,
                            "alias":name.asname,
                            "lineno":node.lineno
                        })

                #from x import y
                elif isinstance(node,ast.ImportFrom):
                    module = node.module or ""
                    for alies in node.names:
                        imports.append({
                            "module":module,
                            "name":alies.name,
                            "alias":alies.asname,
                            "lineno":node.lineno
                        }
                        )
                #functions
                elif isinstance(node, (ast.FunctionDef,ast.AsyncFunctionDef)):
                    function.append({
                        "name":node.name,
                        "lineno":node.lineno,
                        "end_lineno":node.end_lineno,
                    }
                        
                    )
                #classes
                elif isinstance(node, ast.ClassDef):
                    medhods = []
                    for class_node in node.body:
                        if isinstance(class_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            medhods.append({
                                "name": class_node.name,
                                "lineno": class_node.lineno,
                                "end_lineno": class_node.end_lineno,
                            })
                    classes.append({
                        "name": node.name,
                        "lineno": node.lineno,
                        "end_lineno": node.end_lineno,
                        "methods": medhods
                    }
                    )

                #function / method calls
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        call_functions.append({
                            "name": node.func.id,
                            "lineno": node.lineno
                        }
                        )

                    elif isinstance(node.func,ast.Attribute):
                        method_calls.append({
                            "name": node.func.attr,
                            "lineno": node.lineno
                        }
                        )

            relative_file_path = file_path.relative_to(repo_path)


            return{
                "file_path":relative_file_path.as_posix,
                "imports":imports,
                "classes":classes,
                "funcions":function,
                "functions_call":call_functions,
                "method_calls":method_calls

            }
        except SyntaxError as e:
            return{
                "file_path":file_path,
                "error":f"SyntaxError: {e}"
            }
        except Exception as e:
            return{
                "file_path":file_path,
                "error":f"Error: {e}"
            }




def read_file(repository_root:str,
              file_path:str,
              start_line:int|None= None,
              end_line:int|None = None) -> str:
    
    """Read a file from inside the target repository.

    Args:
        repository_root:
            Absolute or relative path to the repository root.

        file_path:
            File path relative to the repository root.

        start_line:
            Optional starting line number. 1-based.

        end_line:
            Optional ending line number. Inclusive.

    Returns:
        File contents or selected line range.
    """

    root = Path(repository_root).resolve()

    if not root.exists():
        raise FileNotFoundError(f"{repository_root} does not exist")

    if not root.is_dir():
        raise ValueError(f"{repository_root} is not a directory")

    #convert requested file path to absolute path
    requested_path = (root / file_path).resolve()

    #security check
    # Ensure that the requested file is within the repository root

    try:
        requested_path.relative_to(root)
    except ValueError:
        raise ValueError(f"{file_path} is not within the repository root {repository_root}")

    if not requested_path.exists():
        raise FileNotFoundError(f"{file_path} does not exist in the repository")

    if not requested_path.is_file():
        raise ValueError(f"{file_path} is not a file")

    try:
        content = requested_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise ValueError(f"{file_path} is not a text file")


    #no line range specified, return entire content

    if start_line is None and end_line is None:
        return content

    lines = content.splitlines()

    # Default values
    if start_line is None:
        start_line = 1

    if end_line is None:
        end_line = len(lines)

    if start_line < 1:
        raise ValueError(
            "start_line must be >= 1"
        )

    if end_line < start_line:
        raise ValueError(
            "end_line must be >= start_line"
        )

    selcted_lines = lines[start_line-1:end_line] if start_line and end_line else lines[start_line-1:] if start_line else lines[:end_line]

    return "\n".join(selcted_lines)



def search_code(
        repository_root:str,
        query:str,
        file_extensions:list[str]|None = None,
        case_sensitive:bool = False,

)-> list[dict]:
    """Search for a query string in the code files of a repository.

    Args:
        repository_root:
            Absolute or relative path to the repository root.

        query:
            The string to search for.

        file_extensions:
            Optional list of file extensions to filter by (e.g., ['.py', '.js']).
            If None, all files are searched.

        case_sensitive:
            Whether the search should be case-sensitive. Default is False.
            """

    root = Path(repository_root).resolve()

    if not root.exists():
        raise FileNotFoundError(f"{repository_root} does not exist")

    if not root.is_dir():
        raise ValueError(f"{repository_root} is not a directory")

    if not query:
        raise ValueError("query string cannot be empty")

    if file_extensions is None:

        file_extensions = [
                ".py",
                ".js",
                ".ts",
                ".java",
                ".go",
                ".json",
                ".yaml",
                ".yml",
                ".md",
                ".txt",
            ]

    result = []

    search_query = query if case_sensitive else query.lower()

    for path in root.rglob("*"):

        if not path.is_file():
            continue

        #ignore files that are not in the specified extensions
        if any (
            part in {
                ".git",
                ".venv",
                "venv",
                "node_modules",
                "__pycache__",
                ".pytest_cache",
                ".mypy_cache",} for part in path.parts
        
        ):
            continue

        if path.suffix.lower() not in file_extensions:
            continue

        try:
            lines = path.read_text(encoding="utf-8").splitlines()

        except UnicodeDecodeError:
            continue

        for lineno, line in enumerate(lines, start = 1):
            comparison_line = (line if case_sensitive else line.lower())

            if search_query in comparison_line:
                relative_path = (path.relative_to(root))

                result.append({
                    "file_path": relative_path.as_posix(),
                    "line_number": lineno,
                    "line_content": line.strip()
                })


    return result



def get_project_metadata(
        repository_root:str,
):

    """Get metadata for the entire project.

    Args:
        repository_root:
            Absolute or relative path to the repository root."""


    root = Path(repository_root).resolve()

    if not root.exists():
        raise FileNotFoundError(f"{repository_root} does not exist")

    if not root.is_dir():
        raise ValueError(f"{repository_root} is not a directory")

    metadata = {
        "language": None,
        "frameworks": [],
        "package_managers": None,
        "dependencies": [],
        "test_frameworks": None,
        "entry_points": [],

    }


    #Detect python
    python_files = list(root.rglob("*.py"))

    if python_files:
        metadata["language"] = "Python"

    requirements_file = root/"requirements.txt"

    if requirements_file.exists():

        metadata["package_manager"] = "pip"

        dependencies = parse_requirements(
            requirements_file
        )

        metadata["dependencies"] = dependencies

    # --------------------------------
    # pyproject.toml
    # --------------------------------

    pyproject_file = root / "pyproject.toml"

    if pyproject_file.exists():

        if metadata["package_manager"] is None:
            metadata["package_manager"] = (
                "pyproject"
            )

        pyproject_dependencies = (
            parse_pyproject_dependencies(
                pyproject_file
            )
        )

        metadata["dependencies"].extend(
            pyproject_dependencies
        )

    # Remove duplicate dependencies
    metadata["dependencies"] = sorted(
        set(metadata["dependencies"])
    )

    # --------------------------------
    # Framework detection
    # --------------------------------

    dependencies_lower = {
        dependency.lower()
        for dependency in metadata["dependencies"]
    }

    if "fastapi" in dependencies_lower:
        metadata["frameworks"].append(
            "FastAPI"
        )

    if "flask" in dependencies_lower:
        metadata["frameworks"].append(
            "Flask"
        )

    if "django" in dependencies_lower:
        metadata["frameworks"].append(
            "Django"
        )

    if "sqlalchemy" in dependencies_lower:
        metadata["frameworks"].append(
            "SQLAlchemy"
        )

    if "pydantic" in dependencies_lower:
        metadata["frameworks"].append(
            "Pydantic"
        )

    # --------------------------------
    # Test framework
    # --------------------------------

    if "pytest" in dependencies_lower:
        metadata["test_framework"] = "pytest"

    elif "unittest" in dependencies_lower:
        metadata["test_framework"] = "unittest"

    # --------------------------------
    # Entry points
    # --------------------------------

    possible_entry_points = [
        "main.py",
        "app.py",
        "server.py",
        "manage.py",
    ]

    for filename in possible_entry_points:

        if (root / filename).exists():

            metadata["entry_points"].append(
                filename
            )

    return metadata


def parse_requirements(
    requirements_file: Path,
) -> list[str]:
    """
    Parse dependency names from requirements.txt.
    """

    dependencies = []

    lines = requirements_file.read_text(
        encoding="utf-8"
    ).splitlines()

    for line in lines:

        line = line.strip()

        # Ignore empty lines
        if not line:
            continue

        # Ignore comments
        if line.startswith("#"):
            continue

        # Ignore editable installs
        if line.startswith("-e"):
            continue

        # Remove version specification
        dependency = re.split(
            r"[<>=!~]",
            line,
            maxsplit=1,
        )[0].strip()

        if dependency:
            dependencies.append(
                dependency
            )

    return dependencies


def parse_pyproject_dependencies(
    pyproject_file: Path,
) -> list[str]:
    """
    Extract dependencies from pyproject.toml.
    """

    try:

        with open(
            pyproject_file,
            "rb"
        ) as file:

            data = tomllib.load(file)

    except Exception:
        return []

    dependencies = []

    project = data.get(
        "project",
        {}
    )

    for dependency in project.get(
        "dependencies",
        []
    ):

        dependency_name = re.split(
            r"[<>=!~]",
            dependency,
            maxsplit=1,
        )[0].strip()

        if dependency_name:
            dependencies.append(
                dependency_name
            )

    return dependencies
        


def _write_file(
    repository_root: str,
    file_path: str,
    content: str,
) -> dict:
    """
    Safely write text content to a file inside
    the target repository.
    """

    root = Path(repository_root).resolve()

    if not root.exists():
        raise FileNotFoundError(
            f"Repository does not exist: {root}"
        )

    if not root.is_dir():
        raise NotADirectoryError(
            f"Repository is not a directory: {root}"
        )

    requested_path = (
        root / file_path
    ).resolve()

    # --------------------------------
    # Security check
    # --------------------------------

    try:
        requested_path.relative_to(root)

    except ValueError:
        raise PermissionError(
            f"Cannot write outside repository: "
            f"{file_path}"
        )

    # --------------------------------
    # Validate extension
    # --------------------------------

    if requested_path.suffix.lower() in {
        ".exe",
        ".dll",
        ".bin",
        ".so",
    }:
        raise PermissionError(
            f"Binary file modification is not allowed: "
            f"{file_path}"
        )

    # --------------------------------
    # Create parent directories
    # --------------------------------

    requested_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------
    # Write file
    # --------------------------------

    requested_path.write_text(
        content,
        encoding="utf-8",
    )

    return {
        "status": "success",
        "file_path": requested_path
            .relative_to(root)
            .as_posix(),
        "message": "File written successfully",
    }

def _git_diff(repository_root: str) -> dict:
    """
    Return the current uncommitted Git diff
    for the target repository.
    """

    root = Path(repository_root).resolve()

    if not root.exists():
        raise FileNotFoundError(
            f"Repository does not exist: {root}"
        )

    if not root.is_dir():
        raise NotADirectoryError(
            f"Repository is not a directory: {root}"
        )

    try:
        result = subprocess.run(
            [
                "git",
                "diff",
                "--no-ext-diff",
                "--",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    except FileNotFoundError:
        raise RuntimeError(
            "Git is not installed or not available "
            "in PATH."
        )

    if result.returncode != 0:
        raise RuntimeError(
            f"Git diff failed:\n{result.stderr}"
        )

    return {
        "status": "success",
        "has_changes": bool(result.stdout.strip()),
        "diff": result.stdout,
    }


if __name__ == "__main__":

    import sys

    repository_path = sys.argv[1]
    _git_diff(repository_path)






    