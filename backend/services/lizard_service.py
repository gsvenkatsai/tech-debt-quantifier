import uuid
from analyzers.lizard_analyzer import analyze_repo as lizard_analyze


def generate_id():
    return str(uuid.uuid4())


def clean_file_path(file_path: str):
    normalized = file_path.replace("\\", "/")
    if "requests/" in normalized:
        return "src/requests/" + normalized.split("requests/")[-1]
    return normalized


def extract_module(file_path: str):
    normalized = file_path.replace("\\", "/")
    if "requests/" in normalized:
        path = normalized.split("requests/")[-1]
    else:
        path = normalized

    path = path.replace(".py", "").replace("/", ".")
    return f"requests.{path}"


def get_length_severity(length: int):
    if length >= 100:
        return "high"
    elif length >= 60:
        return "medium"
    else:
        return "low"


def get_length_impact(length: int):
    if length >= 100:
        return "Very long function, extremely hard to read and test"
    elif length >= 60:
        return "Long function, difficult to maintain"
    else:
        return "Acceptable length"


def estimate_effort(length: int):
    if length >= 100:
        return "high"
    elif length >= 60:
        return "medium"
    else:
        return "low"


def analyze_lizard_output(lizard_data: dict):
    issues = []

    for file_data in lizard_data.get("files", []):
        raw_file_path = file_data["file"]
        file_path = clean_file_path(raw_file_path)

        for func in file_data.get("functions", []):
            length = func["length"]
            severity = get_length_severity(length)

            issues.append({
                "id": generate_id(),

                "type": "long_function",
                "category": "code_quality",   # ✅ FIXED

                "severity": severity,
                "effort": estimate_effort(length),  # ✅ FIXED

                "file": file_path,
                "module": extract_module(file_path),
                "function": func["name"],
                "line": func["lineno"],

                "value": length,

                "message": f"{severity.capitalize()} length in function '{func['name']}' ({length} lines)",
                "impact": get_length_impact(length),

                "tags": ["maintainability", "readability"]
            })

    return {"issues": issues}


def run_lizard(repo_path: str):
    print("Running Lizard...")
    lizard_raw = lizard_analyze(repo_path)
    lizard_issues = analyze_lizard_output(lizard_raw)["issues"]
    return lizard_issues