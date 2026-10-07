def calculate_combined_risk(
    risk_analysis,
    dependency_analysis
):
    """
    Generate a combined rule-based PR risk summary.

    Combines:
    1. Change-based risk
    2. Dependency impact

    This is rule-based logic, NOT ML.
    """

    base_risk = risk_analysis.get(
        "risk_level",
        "Low"
    )

    total_files_changed = risk_analysis.get(
        "total_files_changed",
        0
    )

    total_changes = risk_analysis.get(
        "total_changes",
        0
    )

    high_risk_files = risk_analysis.get(
        "high_risk_files",
        []
    )

    high_dependency_files = []
    medium_dependency_files = []
    all_affected_files = set()

    for dependency in dependency_analysis:

        impact = dependency.get(
            "dependency_impact",
            "Low"
        )

        affected_files = dependency.get(
            "affected_files",
            []
        )

        all_affected_files.update(
            affected_files
        )

        if impact == "High":
            high_dependency_files.append(
                dependency["file"]
            )

        elif impact == "Medium":
            medium_dependency_files.append(
                dependency["file"]
            )

    affected_file_count = len(
        all_affected_files
    )

    if high_dependency_files:
        dependency_impact = "High"

    elif medium_dependency_files:
        dependency_impact = "Medium"

    else:
        dependency_impact = "Low"

    combined_risk = base_risk

    if dependency_impact == "High":

        if base_risk == "Low":
            combined_risk = "Medium"

        elif base_risk == "Medium":
            combined_risk = "High"

    elif dependency_impact == "Medium":

        if base_risk == "Low":
            combined_risk = "Medium"

    reasons = []

    if total_files_changed == 1:
        reasons.append(
            "1 file changed."
        )
    else:
        reasons.append(
            f"{total_files_changed} files changed."
        )

    reasons.append(
        f"{total_changes} total lines were added or deleted."
    )

    reasons.append(
        f"Base change risk is {base_risk}."
    )

    if high_risk_files:
        reasons.append(
            f"{len(high_risk_files)} high-risk file(s) "
            "were identified."
        )

    if high_dependency_files:
        reasons.append(
            f"{len(high_dependency_files)} changed file(s) "
            "have high dependency impact."
        )

    elif medium_dependency_files:
        reasons.append(
            f"{len(medium_dependency_files)} changed file(s) "
            "have medium dependency impact."
        )

    else:
        reasons.append(
            "No significant dependency impact was detected."
        )

    if affected_file_count > 0:
        reasons.append(
            f"{affected_file_count} other project file(s) "
            "may be affected."
        )
    else:
        reasons.append(
            "No dependent project files were detected."
        )

    return {
        "combined_risk_level": combined_risk,
        "base_risk_level": base_risk,
        "dependency_impact": dependency_impact,
        "total_files_changed": total_files_changed,
        "total_changes": total_changes,
        "high_risk_file_count": len(high_risk_files),
        "affected_file_count": affected_file_count,
        "high_dependency_files": high_dependency_files,
        "medium_dependency_files": medium_dependency_files,
        "affected_files": sorted(all_affected_files),
        "reasons": reasons
    }
