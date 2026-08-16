import os
from pathlib import Path
import ast


def scan_repository(folder_path:str):
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
                    file_metadata = extract_metadata(full_path)
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
                "file_path":file_path.as_posix(),
                "error":f"SyntaxError: {e}"
            }
        except Exception as e:
            return{
                "file_path":file_path.as_posix(),
                "error":f"Error: {e}"
            }




def read_file(repository_path:str,
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

    root = Path(repository_path).resolve()

    if not root.exists():
        raise FileNotFoundError(f"{repository_path} does not exist")

    if not root.is_dir():
        raise ValueError(f"{repository_path} is not a directory")

    #convert requested file path to absolute path
    requested_path = (root / file_path).resolve()

    #security check
    # Ensure that the requested file is within the repository root

    try:
        requested_path.relative_to(root)
    except ValueError:
        raise ValueError(f"{file_path} is not within the repository root {repository_path}")

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



if __name__ == "__main__":

    repository_root = "."

    content = read_file(repository_root, "utils/travers.py")


    print(content)






    