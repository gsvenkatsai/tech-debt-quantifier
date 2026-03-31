import uuid


def generate_id():
    return str(uuid.uuid4())


def get_severity(complexity: int):
    if complexity >= 20:
        return "high"
    elif complexity >= 10:
        return "medium"
    else:
        return "low"


def estimate_effort(complexity: int):
    if complexity >= 25:
        return "high"
    elif complexity >= 15:
        return "medium"
    else:
        return "low"


def get_impact(complexity: int):
    if complexity >= 20:
        return "High maintenance cost and bug-prone"
    elif complexity >= 10:
        return "Moderate maintenance difficulty"
    else:
        return "Low impact"


def clean_file_path(file_path: str):
    if "requests/" in file_path:
        return "src/requests/" + file_path.split("requests/")[-1]
    return file_path


def extract_module(file_path: str):
    if "requests/" in file_path:
        path = file_path.split("requests/")[-1]
    else:
        path = file_path

    path = path.replace(".py", "").replace("/", ".")
    return f"requests.{path}"


def analyze_radon_output(radon_data: dict):
    issues = []

    for file_data in radon_data.get("files", []):
        raw_file_path = file_data["file"]
        file_path = clean_file_path(raw_file_path)

        for func in file_data.get("functions", []):
            complexity = func["complexity"]

            if complexity < 10:
                continue

            severity = get_severity(complexity)

            issues.append({
                "id": generate_id(),
                "type": "complexity",
                "category": "code_quality",

                "severity": severity,
                "effort": estimate_effort(complexity),

                "file": file_path,
                "module": extract_module(file_path),
                "function": func["name"],
                "line": func["lineno"],

                "value": complexity,

                "message": f"{severity.capitalize()} complexity in function '{func['name']}'",
                "impact": get_impact(complexity),

                "tags": ["maintainability"]
            })

    return {
        "issues": issues
    }