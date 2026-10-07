def analyze_risk(files):
    total_files = len(files)

    total_additions = sum(
        file["additions"] for file in files
    )

    total_deletions = sum(
        file["deletions"] for file in files
    )

    total_changes = total_additions + total_deletions

    large_files = sum(
        1 for file in files
        if file["additions"] + file["deletions"] >= 100
    )

    analyzed_files = []

    for file in files:
        file_changes = file["additions"] + file["deletions"]

        if file_changes >= 300:
            file_risk = "High"
        elif file_changes >= 100:
            file_risk = "Medium"
        else:
            file_risk = "Low"

        analyzed_files.append({
            "filename": file["filename"],
            "additions": file["additions"],
            "deletions": file["deletions"],
            "total_changes": file_changes,
            "risk_level": file_risk,
        })

    high_risk_files = [
        file for file in analyzed_files
        if file["risk_level"] == "High"
    ]

    if total_files >= 20 or total_changes >= 1000:
        risk_level = "High"
        explanation = (
            "High risk due to a large number of files "
            "or extensive code changes."
        )
    elif total_files >= 10 or total_changes >= 300 or large_files >= 3:
        risk_level = "Medium"
        explanation = (
            "Medium risk due to a moderate number of "
            "files, substantial code changes, or "
            "multiple large files."
        )
    else:
        risk_level = "Low"
        explanation = (
            "Low risk based on the current rules: "
            "the number of changed files and code "
            "modifications are below the defined "
            "risk thresholds."
        )

    return {
        "risk_level": risk_level,
        "explanation": explanation,
        "total_files_changed": total_files,
        "total_additions": total_additions,
        "total_deletions": total_deletions,
        "total_changes": total_changes,
        "large_files_changed": large_files,
        "high_risk_files": high_risk_files,
        "file_analysis": analyzed_files,
    }