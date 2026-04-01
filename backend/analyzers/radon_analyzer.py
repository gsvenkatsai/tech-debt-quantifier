import os
from radon.complexity import cc_visit


def analyze_file(file_path: str):
    results = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        blocks = cc_visit(code)

        for block in blocks:
            results.append({
                "name": block.name,
                "complexity": block.complexity,
                "lineno": block.lineno
            })

    except Exception as e:
        print(f"[Radon Error] {file_path}: {e}")

    return {
        "file": file_path,
        "functions": results
    }


def analyze_repo(repo_path: str):
    all_results = []

    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)

                file_result = analyze_file(full_path)

                if file_result["functions"]:
                    all_results.append(file_result)

    return {
        "tool": "radon",
        "files": all_results
    }