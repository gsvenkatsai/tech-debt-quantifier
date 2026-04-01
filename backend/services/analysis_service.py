import uuid
import lizard
from radon.complexity import cc_visit
import os

# --- Helper Functions ---

def clean_file_path(file_path: str, repo_name: str):
    """Removes local folder structure to keep paths relative."""
    search_pattern = f"{repo_name}"
    if search_pattern in file_path:
        return file_path.split(search_pattern)[-1].lstrip("\\/")
    return file_path

def extract_module(file_path: str, repo_name: str):
    """Converts a file path into a Python module dot-notation."""
    # First clean the path using the repo_name
    path = clean_file_path(file_path, repo_name)
    # Remove extension and swap slashes for dots
    path = path.replace(".py", "").replace("/", ".").replace("\\", ".")
    return f"{repo_name}.{path}"

def get_severity(complexity: int):
    if complexity >= 20: return "high"
    elif complexity >= 10: return "medium"
    return "low"

def estimate_effort(complexity: int):
    if complexity >= 25: return "high"
    elif complexity >= 15: return "medium"
    return "low"

def get_impact(complexity: int):
    if complexity >= 20: return "High maintenance cost and bug-prone"
    elif complexity >= 10: return "Moderate maintenance difficulty"
    return "Low impact"

# --- Analysis Workers ---

def run_lizard(repo_path: str):
    """Runs Lizard and returns raw dictionary data."""
    analysis = lizard.analyze_files([repo_path])
    return [vars(f) for f in analysis]

def run_radon(repo_path: str):
    """Runs Radon to get Cyclomatic Complexity."""
    results = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        code = f.read()
                        complexity_data = cc_visit(code)
                        for item in complexity_data:
                            results.append({
                                "file": full_path,
                                "name": item.name,
                                "complexity": item.complexity,
                                "lineno": item.lineno
                            })
                except Exception as e:
                    print(f"Skipping {full_path} due to error: {e}")
    return results

# --- Formatter (The Phase 2 Style Logic) ---

def format_to_phase2_style(raw_radon, blast_scores, repo_name):
    issues = []
    heatmap = []
    summary = {"total_issues": 0, "high": 0, "medium": 0, "low": 0, "debt_score": 0, "avg_blast_radius": 0}
    
    total_br = 0
    for item in raw_radon:
        complexity = item["complexity"]
        # FIXED: Passing repo_name here
        mod_name = extract_module(item["file"], repo_name)
        br = blast_scores.get(mod_name, 0)
        total_br += br
        
        impact_score = complexity * br
        
        if complexity >= 10:
            severity = get_severity(complexity)
            summary[severity] += 1
            
            # FIXED: Corrected path cleaning
            display_file = clean_file_path(item["file"], repo_name)
            
            issues.append({
                "id": f"err-{len(issues) + 1:03d}",
                "type": "complexity",
                "category": "code_quality",
                "severity": severity,
                "effort": estimate_effort(complexity),
                "file": display_file,
                "module": mod_name,
                "function": item["name"],
                "line": item["lineno"],
                "value": complexity,
                "blast_radius": br,
                "system_impact_score": impact_score,
                "message": f"{severity.capitalize()} complexity in function '{item['name']}'",
                "impact": get_impact(complexity),
                "tags": ["architectural-debt"] if br > 10 else ["code-quality"]
            })
            
            heatmap.append({
                "file": display_file,
                "x_complexity": complexity,
                "y_blast_radius": br,
                "z_priority": impact_score,
                "quadrant": "High Impact" if br > 10 else "Quick Wins"
            })
    
    summary["total_issues"] = len(issues)
    summary["avg_blast_radius"] = round(total_br / len(raw_radon), 1) if raw_radon else 0
    # Simple debt score calculation
    summary["debt_score"] = min(100, (summary["high"] * 15) + (summary["medium"] * 5))
    
    return issues, summary, heatmap

# --- Main Entry Point ---

def run_static_analysis(repo_path, repo_name, blast_scores=None):
    """Main function called by pipeline_service."""
    if blast_scores is None:
        blast_scores = {}

    raw_radon = run_radon(repo_path)
    raw_lizard = run_lizard(repo_path)

    # FIXED: Calling the formatter with all 3 required arguments
    issues, summary, heatmap = format_to_phase2_style(raw_radon, blast_scores, repo_name)

    return {
        "raw": {
            "radon": {"tool": "radon", "files": raw_radon},
            "lizard": {"tool": "lizard", "files": raw_lizard}
        },
        "issues": issues,
        "summary": summary,
        "heatmap": heatmap,
        "categories": {"code_quality": len(issues)}
    }