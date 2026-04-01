import subprocess
import uuid


def generate_id():
    return str(uuid.uuid4())


def get_severity(coverage):
    if coverage < 50:
        return "high"
    elif coverage < 70:
        return "medium"
    else:
        return "low"


def analyze_coverage(repo_path: str):
    issues = []

    try:
        result = subprocess.run(
            ["coverage", "report"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )

        lines = result.stdout.split("\n")

        for line in lines:
            if ".py" in line and "%" in line:
                parts = line.split()

                file_path = parts[0]
                coverage_percent = int(parts[-1].replace("%", ""))

                if coverage_percent >= 80:
                    continue  # ignore well-tested files

                severity = get_severity(coverage_percent)

                issues.append({
                    "id": generate_id(),

                    "type": "coverage",
                    "category": "testing",

                    "severity": severity,
                    "effort": "medium",

                    "file": file_path,
                    "module": file_path.replace(".py", "").replace("/", "."),
                    "function": None,
                    "line": None,

                    "value": 100 - coverage_percent,

                    "message": f"Low test coverage in {file_path} ({coverage_percent}%)",
                    "impact": "Untested code increases bug risk",

                    "tags": ["testing"]
                })

    except Exception as e:
        print("[coverage error]", e)

    return {"issues": issues}