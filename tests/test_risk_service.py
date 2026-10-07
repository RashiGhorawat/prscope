from app.services.risk_service import analyze_risk


def test_low_risk_pull_request():
    files = [
        {
            "filename": "app/example.py",
            "additions": 5,
            "deletions": 3,
            "changes": 8
        }
    ]

    result = analyze_risk(files)

    assert result["risk_level"] == "Low"
    assert result["total_files_changed"] == 1
    assert result["total_additions"] == 5
    assert result["total_deletions"] == 3
    assert result["total_changes"] == 8


def test_high_risk_pull_request():
    files = []

    for i in range(20):
        files.append(
            {
                "filename": f"app/file_{i}.py",
                "additions": 50,
                "deletions": 10,
                "changes": 60
            }
        )

    result = analyze_risk(files)

    assert result["risk_level"] == "High"
    assert result["total_files_changed"] == 20