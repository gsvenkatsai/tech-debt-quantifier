import os
import stat
from analyzers.radon_analyzer import analyze_repo
from services.analysis_service import run_static_analysis
from services.graph_service import build_dependency_graph
from services.summary_service import build_summary, build_categories
from analyzers.pip_audit_analyzer import run_pip_audit
from services.pip_audit_service import analyze_pip_audit_output
from services.coverage_service import analyze_coverage
from services.lizard_service import run_lizard   # ✅ NEW
from services.graph_service import build_repo_graph
import git
import shutil
import uuid
from services.graph_service import build_dependency_graph
from services.analysis_service import run_static_analysis
from services.analysis_service import run_static_analysis
from services.graph_service import build_dependency_graph

def clone_repo(repo_url: str):
    # Remove .git if it exists to get the clean folder name
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    clone_path = os.path.join("backend", "repos", repo_name)
    
    if not os.path.exists(clone_path):
        print(f"🚀 Cloning {repo_name}...")
        os.system(f"git clone {repo_url} {clone_path}")
    
    return clone_path, repo_name


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

def clean_path_for_mapping(raw_path):
    # Convert backslashes to forward slashes for Windows compatibility
    normalized = raw_path.replace("\\", "/")
    
    # We only want the part of the path starting from 'src' or 'tests'
    if "src/" in normalized:
        return "src" + normalized.split("src")[-1]
    if "tests/" in normalized:
        return "tests" + normalized.split("tests")[-1]
    
    # Fallback: just return the filename if nothing else matches
    return os.path.basename(normalized)

def run_pipeline(repo_url: str):
    repo_path = clone_repo(repo_url)

    # 1. Run Phase 1 Analyzers
    radon_issues = run_radon(repo_path)
    pip_issues = run_pip(repo_path)
    coverage_issues = run_coverage(repo_path)
    lizard_issues = run_lizard(repo_path) 

    all_issues = (
        radon_issues +
        pip_issues +
        coverage_issues +
        lizard_issues
    )

    # 2. Get the Graph Data from Person A's service
    blast_map, edges = build_repo_graph(repo_path)

    # 3. Enrichment & Heatmap Generation
    enriched_issues = []
    heatmap_data = []

    for issue in all_issues:
        clean_name = clean_path_for_mapping(issue.get("file", ""))
        
        # --- FIX FOR RADIUS LIST ERROR ---
        raw_radius = blast_map.get(clean_name, 0)
        if isinstance(raw_radius, list):
            # If it's a list of connections, the "radius" is the number of connections
            safe_radius = len(raw_radius)
        else:
            try:
                safe_radius = int(raw_radius)
            except (ValueError, TypeError):
                safe_radius = 0
        
        # --- ULTIMATE SAFETY CHECK FOR VALUE ---
        raw_val = issue.get("value", 0)
        
        if isinstance(raw_val, list):
            # Take the first number in the list if available
            val = int(raw_val[0]) if (raw_val and str(raw_val[0]).isdigit()) else 0
        else:
            try:
                val = int(raw_val) if raw_val is not None else 0
            except (ValueError, TypeError):
                val = 0
            
        # 4. Final Math
        system_impact = val * safe_radius
        
        # Update the issue object with clean data
        issue["value"] = val 
        issue["blast_radius"] = safe_radius
        issue["system_impact_score"] = system_impact
        issue["clean_path"] = clean_name

        enriched_issues.append(issue)

        heatmap_data.append({
            "file": clean_name,
            "x_complexity": val,
            "y_blast_radius": safe_radius,
            "z_impact": system_impact
        })

    # 5. Sort by System Impact Score
    enriched_issues.sort(key=lambda x: x.get("system_impact_score", 0), reverse=True)
    
    # 6. Re-calculate summary based on enriched data
    summary = build_summary(enriched_issues)
    categories = build_categories(enriched_issues)

    return {
        "repo_url": repo_url,
        "summary": summary,
        "categories": categories,
        "top_10_priority": enriched_issues[:10],
        "all_issues": enriched_issues,
        "graph": {
            "nodes": [{"id": k, "label": os.path.basename(k), "blast_radius": (len(v) if isinstance(v, list) else v)} for k, v in blast_map.items()],
            "edges": edges
        },
        "heatmap": heatmap_data
    }

if __name__ == "__main__":
    import json
    
    print("\n🚀 STARTING MASTER PIPELINE ANALYSIS...")
    target_repo = "https://github.com/psf/requests"
    
    try:
        # 1. Run the full pipeline
        result = run_pipeline(target_repo)
        
        # 2. Define the output filename
        output_filename = "master_output.json"
        
        # 3. SAVE TO FILE
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
            
        print("\n" + "="*40)
        print("✅ ANALYSIS COMPLETE!")
        print(f"📂 Master JSON saved to: {os.path.abspath(output_filename)}")
        print(f"📊 Total Issues Found: {result['summary']['total_issues']}")
        print("="*40)
        
    except Exception as e:
        print(f"❌ PIPELINE CRASHED: {e}")
        import traceback
        traceback.print_exc()

def run_full_analysis(repo_url: str):
    clone_path, repo_name = clone_repo(repo_url)
    
    try:
        # 1. Build the graph first to get blast radius scores
        graph_data, blast_scores = build_dependency_graph(clone_path, repo_name)
        
        # 2. Run static analysis using those scores
        analysis_payload = run_static_analysis(clone_path, repo_name, blast_scores)
        
        # 3. Return the consolidated "Requests-style" JSON
        return {
            "repo_url": repo_url,
            "summary": analysis_payload["summary"],
            "issues": analysis_payload["issues"],
            "heatmap": analysis_payload["heatmap"],
            "graph": graph_data,
            "categories": analysis_payload["categories"],
            "status": "Ready for Fingerprinting"
        }
    finally:
        cleanup_workspace(clone_path)



def cleanup_workspace(temp_path: str):
    def readonly_handler(func, path, execinfo):
        """Force deletes read-only files (common in .git folders)"""
        os.chmod(path, stat.S_IWRITE)
        func(path)

    try:
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path, onerror=readonly_handler)
            print(f"🧹 Successfully cleaned up: {temp_path}")
    except Exception as e:
        print(f"⚠️ Cleanup failed for {temp_path}: {e}")