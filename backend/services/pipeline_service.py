import os
from analyzers.radon_analyzer import analyze_repo
from services.analysis_service import analyze_radon_output
from services.summary_service import build_summary, build_categories
from analyzers.pip_audit_analyzer import run_pip_audit
from services.pip_audit_service import analyze_pip_audit_output
from services.coverage_service import analyze_coverage
from services.lizard_service import run_lizard   # ✅ NEW


def clone_repo(repo_url: str):
    repo_name = repo_url.split("/")[-1]
    clone_path = os.path.join("repos", repo_name)

    if not os.path.exists(clone_path):
        print("Cloning repo...")
        os.system(f"git clone {repo_url} {clone_path}")
    else:
        print("Repo already exists.")

    return clone_path


def run_radon(repo_path: str):
    raw_data = analyze_repo(repo_path)
    processed = analyze_radon_output(raw_data)
    return processed["issues"]


def run_pip(repo_path: str):
    raw = run_pip_audit(repo_path)
    processed = analyze_pip_audit_output(raw)
    return processed["issues"]


def run_coverage(repo_path: str):
    processed = analyze_coverage(repo_path)
    return processed["issues"]


def run_pipeline(repo_url: str):
    repo_path = clone_repo(repo_url)

    radon_issues = run_radon(repo_path)
    pip_issues = run_pip(repo_path)
    coverage_issues = run_coverage(repo_path)
    lizard_issues = run_lizard(repo_path)   # ✅ NEW

    all_issues = (
        radon_issues +
        pip_issues +
        coverage_issues +
        lizard_issues
    )

    summary = build_summary(all_issues)
    categories = build_categories(all_issues)

    return {
        "repo_url": repo_url,
        "issues": all_issues,
        "summary": summary,
        "categories": categories
    }


if __name__ == "__main__":
    result = run_pipeline("https://github.com/psf/requests")

    import json
    print(json.dumps(result, indent=2))