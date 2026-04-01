def build_summary(issues):
    summary = {
        "total_issues": len(issues),
        "high": 0,
        "medium": 0,
        "low": 0,
        "debt_score": 0
    }

    total_score = 0

    for issue in issues:
        severity = issue["severity"]
        summary[severity] += 1

        # weighted scoring
        if severity == "high":
            total_score += issue["value"] * 2
        elif severity == "medium":
            total_score += issue["value"] * 1.5
        else:
            total_score += issue["value"]

    summary["debt_score"] = min(100, int(total_score / max(1, len(issues))))

    return summary

def build_categories(issues):
    categories = {}

    for issue in issues:
        cat = issue["category"]
        categories[cat] = categories.get(cat, 0) + 1

    return categories