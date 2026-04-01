import json
import subprocess


def run_pip_audit(repo_path: str):
    try:
        result = subprocess.run(
            ["pip-audit", "-r", f"{repo_path}/requirements.txt", "-f", "json"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("pip-audit failed or no requirements.txt")
            return {"vulnerabilities": []}

        data = json.loads(result.stdout)

        return data

    except Exception as e:
        print(f"[pip-audit error]: {e}")
        return {"vulnerabilities": []}