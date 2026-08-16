from pathlib import Path


def list_files(root:str = ".") -> list[str]:

    root_path = Path(root)

    files = []

    for path in root_path.rglob("*"):
        if not path.is_file():
            continue

        if ".git" in path.parts:
            continue

        files.append(str(path))

    return files


def read_file(file_path: str) -> str:

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"{file_path} does not exist")

    if not path.is_file():
        raise ValueError(f" {file_path} is not a file")

    return path.read_text(encoding="utf-8")




