import os
from analyzers.radon_analyzer import analyze_repo
from services.analysis_service import analyze_radon_output
from services.summary_service import build_summary, build_categories


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


def run_pipeline(repo_url: str):
    repo_path = clone_repo(repo_url)

    issues = run_radon(repo_path)

    summary = build_summary(issues)
    categories = build_categories(issues)

    return {
        "repo_url": repo_url,
        "issues": issues,
        "summary": summary,
        "categories": categories
    }


if __name__ == "__main__":
    result = run_pipeline("https://github.com/psf/requests")

    import json
    print(json.dumps(result, indent=2))