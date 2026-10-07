import os

import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not configured.")

    return psycopg2.connect(DATABASE_URL)


def get_or_create_repository(owner, name):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            full_name = f"{owner}/{name}"

            cursor.execute(
                """
                INSERT INTO repositories (owner, name, full_name)
                VALUES (%s, %s, %s)
                ON CONFLICT (full_name)
                DO UPDATE SET owner = EXCLUDED.owner,
                              name = EXCLUDED.name
                RETURNING id
                """,
                (owner, name, full_name)
            )

            repository_id = cursor.fetchone()[0]

        connection.commit()
        return repository_id

    finally:
        connection.close()


def save_pull_request(
    repository_id,
    pr_number,
    pr_data,
    risk_analysis
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO pull_requests (
                    repository_id,
                    pr_number,
                    title,
                    state,
                    github_url,
                    total_files_changed,
                    total_additions,
                    total_deletions,
                    total_changes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (repository_id, pr_number)
                DO UPDATE SET
                    title = EXCLUDED.title,
                    state = EXCLUDED.state,
                    github_url = EXCLUDED.github_url,
                    total_files_changed = EXCLUDED.total_files_changed,
                    total_additions = EXCLUDED.total_additions,
                    total_deletions = EXCLUDED.total_deletions,
                    total_changes = EXCLUDED.total_changes,
                    analyzed_at = CURRENT_TIMESTAMP
                RETURNING id
                """,
                (
                    repository_id,
                    pr_number,
                    pr_data["title"],
                    pr_data["state"],
                    pr_data["html_url"],
                    risk_analysis.get("total_files_changed", 0),
                    risk_analysis.get("total_additions", 0),
                    risk_analysis.get("total_deletions", 0),
                    risk_analysis.get("total_changes", 0)
                )
            )

            pull_request_id = cursor.fetchone()[0]

        connection.commit()
        return pull_request_id

    finally:
        connection.close()


def save_pr_files(pull_request_id, files, risk_analysis):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM pr_files
                WHERE pull_request_id = %s
                """,
                (pull_request_id,)
            )

            file_analysis_map = {
                item["filename"]: item
                for item in risk_analysis.get("file_analysis", [])
            }

            for file in files:
                filename = file.get("filename", "")
                analysis = file_analysis_map.get(filename, {})

                cursor.execute(
                    """
                    INSERT INTO pr_files (
                        pull_request_id,
                        filename,
                        status,
                        additions,
                        deletions,
                        changes,
                        risk_level
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        pull_request_id,
                        filename,
                        file.get("status", "modified"),
                        file.get("additions", 0),
                        file.get("deletions", 0),
                        file.get("changes", 0),
                        analysis.get("risk_level", "Low")
                    )
                )

        connection.commit()

    finally:
        connection.close()


def save_risk_analysis(
    pull_request_id,
    risk_analysis,
    combined_risk,
    ml_prediction,
    test_recommendations
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM risk_analyses
                WHERE pull_request_id = %s
                """,
                (pull_request_id,)
            )

            cursor.execute(
                """
                INSERT INTO risk_analyses (
                    pull_request_id,
                    base_risk_level,
                    dependency_impact,
                    combined_risk_level,
                    ml_predicted_risk,
                    ml_confidence,
                    affected_file_count,
                    high_risk_file_count,
                    test_recommendations,
                    ml_class_probabilities,
                    risk_reasons,
                    affected_files
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    pull_request_id,
                    combined_risk.get("base_risk_level", "Low"),
                    combined_risk.get("dependency_impact", "Low"),
                    combined_risk.get("combined_risk_level", "Low"),
                    ml_prediction.get("predicted_risk", "Low"),
                    ml_prediction.get("confidence", 0),
                    combined_risk.get("affected_file_count", 0),
                    combined_risk.get("high_risk_file_count", 0),
                    Json(test_recommendations),
                    Json(ml_prediction.get("class_probabilities", {})),
                    Json(combined_risk.get("reasons", [])),
                    Json(combined_risk.get("affected_files", []))
                )
            )

        connection.commit()

    finally:
        connection.close()


def save_complete_analysis(
    owner,
    repo,
    pr_number,
    pr_data,
    files,
    risk_analysis,
    combined_risk,
    ml_prediction,
    test_recommendations
):
    repository_id = get_or_create_repository(owner, repo)

    pull_request_id = save_pull_request(
        repository_id=repository_id,
        pr_number=pr_number,
        pr_data=pr_data,
        risk_analysis=risk_analysis
    )

    save_pr_files(
        pull_request_id=pull_request_id,
        files=files,
        risk_analysis=risk_analysis
    )

    save_risk_analysis(
        pull_request_id=pull_request_id,
        risk_analysis=risk_analysis,
        combined_risk=combined_risk,
        ml_prediction=ml_prediction,
        test_recommendations=test_recommendations
    )

    return {
        "repository_id": repository_id,
        "pull_request_id": pull_request_id
    }