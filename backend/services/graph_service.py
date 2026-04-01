import ast
import os

def get_file_imports(file_path, repo_root):
    """Finds all internal imports within a specific python file."""
    internal_imports = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            tree = ast.parse(f.read())
            
        for node in ast.walk(tree):
            # Case 1: import requests
            if isinstance(node, ast.Import):
                for alias in node.names:
                    internal_imports.append(alias.name)
            # Case 2: from requests import get
            elif isinstance(node, ast.ImportFrom) and node.module:
                internal_imports.append(node.module)
                
    except Exception as e:
        print(f"Skipping {file_path} due to error: {e}")
        
    return internal_imports

def build_repo_graph(repo_path):
    # Map of { "file_path": [list_of_imports] }
    adj_list = {}
    # Count of { "file_path": number_of_times_imported }
    blast_radius = {}

    # 1. Walk through the repo to find all .py files
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, repo_path).replace("\\", "/")
                
                # Initialize
                adj_list[rel_path] = get_file_imports(full_path, repo_path)
                blast_radius[rel_path] = 0

    # 2. Calculate Blast Radius (In-degree)
    # Check if an import matches one of our internal files
    for source_file, imports in adj_list.items():
        for imp in imports:
            # Convert import style 'requests.models' to path 'requests/models.py'
            potential_path = imp.replace(".", "/") + ".py"
            
            for internal_file in blast_radius.keys():
                if internal_file.endswith(potential_path) or potential_path in internal_file:
                    blast_radius[internal_file] += 1
                    
    return adj_list, blast_radius

def format_graph_data(adj_list, blast_radius):
    nodes = []
    edges = []

    for file_path, radius in blast_radius.items():
        nodes.append({
            "id": file_path,
            "label": os.path.basename(file_path),
            "blast_radius": radius
        })

    for source, targets in adj_list.items():
        for target_module in targets:
            # Simple heuristic to match module to file path
            target_file = next((f for f in blast_radius.keys() if target_module.replace('.', '/') in f), None)
            if target_file:
                edges.append({
                    "source": source,
                    "target": target_file,
                    "relationship": "imports"
                })

    return {"nodes": nodes, "edges": edges, "blast_radius_map": blast_radius}

if __name__ == "__main__":
    import os
    
    # 1. Path Setup
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Since 'repos' is inside 'backend' (based on your VS Code image)
    backend_dir = os.path.abspath(os.path.join(script_dir, ".."))
    test_path = os.path.join(backend_dir, "repos", "requests")
    
    print(f"\n--- Scanning Repository: {test_path} ---")
    
    if not os.path.exists(test_path):
        print(f"❌ ERROR: Could not find 'requests' folder at {test_path}")
    else:
        # 2. Execute the Logic
        adj, blast = build_repo_graph(test_path)
        
        # 3. Print Results for Verification
        print("\n" + "="*40)
        print(f"{'FILE PATH':<45} | {'BLAST RADIUS'}")
        print("-" * 60)
        
        # Sort to see the most important files first
        sorted_blast = sorted(blast.items(), key=lambda x: x[1], reverse=True)
        
        for file, count in sorted_blast[:10]: # Show top 10
            print(f"{file:<45} | {count}")
            
        print("="*40)
        print(f"Total Files Scanned: {len(blast)}")