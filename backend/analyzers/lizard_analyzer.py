import os
import lizard


def analyze_file(file_path: str):
    results = []

    try:
        analysis = lizard.analyze_file(file_path)

        for func in analysis.function_list:
            results.append({
                "name": func.name,
                "lineno": func.start_line,
                "length": func.length,
                "complexity": func.cyclomatic_complexity
            })

    except Exception as e:
        print(f"[Lizard Error] {file_path}: {e}")

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

                long_functions = [
                    f for f in file_result["functions"]
                    if f["length"] > 60
                ]

                if long_functions:
                    all_results.append({
                        "file": full_path,
                        "functions": long_functions
                    })

    return {
        "files": all_results
    }