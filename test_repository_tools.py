import sys

from utils.travers import (
    _git_diff,
    read_file,
    search_code,
    scan_repository,
    get_project_metadata,
    write_file,
)


def main():

    repository_path = "."

    if len(sys.argv) > 1:
        repository_path = sys.argv[1]

    print("\n")
    print("=" * 70)
    print("REPOSITORY TOOL TEST")
    print("=" * 70)

    print(f"\nRepository: {repository_path}")

    # ------------------------------------------------
    # 1. PROJECT METADATA
    # ------------------------------------------------

    print("\n\n[1] get_project_metadata()")
    print("-" * 50)

    metadata = get_project_metadata(
        repository_path
    )

    print(metadata)

    # ------------------------------------------------
    # 2. SCAN REPOSITORY
    # ------------------------------------------------

    print("\n\n[2] scan_repository()")
    print("-" * 50)

    repository = scan_repository(
        repository_path
    )

    print(
        f"Python files found: {len(repository)}"
    )

    for file_metadata in repository[:10]:

        print(
            file_metadata["file_path"]
        )

    if len(repository) > 10:

        print(
            f"... and "
            f"{len(repository) - 10} more"
        )

    # ------------------------------------------------
    # 3. READ FILE
    # ------------------------------------------------

    print("\n\n[3] read_file()")
    print("-" * 50)

    # Try to find a Python file
    python_files = [
        item["file_path"]
        for item in repository
        if "error" not in item
    ]

    if python_files:

        file_to_read = python_files[0]

        print(
            f"Reading: {file_to_read}"
        )

        content = read_file(
            repository_path,
            file_to_read,
            start_line=1,
            end_line=10,
        )

        print("\nFirst 10 lines:")
        print(content)

    else:

        print(
            "No Python files available "
            "for read_file test."
        )

    # ------------------------------------------------
    # 4. SEARCH CODE
    # ------------------------------------------------

    print("\n\n[4] search_code()")
    print("-" * 50)

    results = search_code(
        repository_path,
        "import",
        file_extensions=[".py"],
    )

    print(
        f"Matches found: {len(results)}"
    )

    for result in results[:10]:

        print(
            f"{result['file_path']}:"
            f"{result['line_number']} "
            f"{result['line']}"
        )

    # ------------------------------------------------
    # 5. WRITE FILE
    # ------------------------------------------------

    print("\n\n[5] write_file()")
    print("-" * 50)

    test_file = (
        ".agent_tool_test.txt"
    )

    write_result = write_file(
        repository_path,
        test_file,
        "Temporary file created by Jenkins "
        "repository tool test.\n",
    )

    print(write_result)

    # ------------------------------------------------
    # 6. GIT DIFF
    # ------------------------------------------------

    print("\n\n[6] git_diff()")
    print("-" * 50)

    diff_result = _git_diff(
        repository_path
    )

    print(
        "Has changes:",
        diff_result["has_changes"],
    )

    print("\nDiff:")

    print(
        diff_result["diff"]
    )

    print("\n")
    print("=" * 70)
    print("ALL REPOSITORY TOOLS TEST COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()