from fastapi import APIRouter, HTTPException

from app.services.database_service import get_connection


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/repositories")
def get_repositories():

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    owner,
                    name,
                    full_name,
                    created_at
                FROM repositories
                ORDER BY created_at DESC
                """
            )

            rows = cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "owner": row[1],
                    "name": row[2],
                    "full_name": row[3],
                    "created_at": row[4]
                }
                for row in rows
            ]

    finally:
        connection.close()


@router.get("/prs")
def get_pull_requests():

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    pr.id,
                    r.full_name,
                    pr.pr_number,
                    pr.title,
                    pr.state,
                    pr.total_files_changed,
                    pr.total_additions,
                    pr.total_deletions,
                    pr.total_changes,
                    pr.analyzed_at
                FROM pull_requests pr
                JOIN repositories r
                    ON pr.repository_id = r.id
                ORDER BY pr.analyzed_at DESC
                """
            )

            rows = cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "repository": row[1],
                    "pr_number": row[2],
                    "title": row[3],
                    "state": row[4],
                    "total_files_changed": row[5],
                    "total_additions": row[6],
                    "total_deletions": row[7],
                    "total_changes": row[8],
                    "analyzed_at": row[9]
                }
                for row in rows
            ]

    finally:
        connection.close()


@router.get("/pr/{pull_request_id}")
def get_pr_analysis(pull_request_id: int):

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    pr.id,
                    r.full_name,
                    pr.pr_number,
                    pr.title,
                    pr.state,
                    pr.github_url,
                    pr.total_files_changed,
                    pr.total_additions,
                    pr.total_deletions,
                    pr.total_changes,
                    pr.analyzed_at
                FROM pull_requests pr
                JOIN repositories r
                    ON pr.repository_id = r.id
                WHERE pr.id = %s
                """,
                (pull_request_id,)
            )

            pr = cursor.fetchone()

            if not pr:
                raise HTTPException(
                    status_code=404,
                    detail="Pull request not found"
                )

            cursor.execute(
                """
                SELECT
                    filename,
                    status,
                    additions,
                    deletions,
                    changes,
                    risk_level
                FROM pr_files
                WHERE pull_request_id = %s
                ORDER BY changes DESC
                """,
                (pull_request_id,)
            )

            file_rows = cursor.fetchall()

            files = [
                {
                    "filename": row[0],
                    "status": row[1],
                    "additions": row[2],
                    "deletions": row[3],
                    "changes": row[4],
                    "risk_level": row[5]
                }
                for row in file_rows
            ]

            cursor.execute(
                """
                SELECT
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
                    affected_files,
                    analyzed_at
                FROM risk_analyses
                WHERE pull_request_id = %s
                ORDER BY analyzed_at DESC
                LIMIT 1
                """,
                (pull_request_id,)
            )

            risk = cursor.fetchone()

            risk_analysis = None

            if risk:

                risk_analysis = {
                    "base_risk_level": risk[0],
                    "dependency_impact": risk[1],
                    "combined_risk_level": risk[2],
                    "ml_predicted_risk": risk[3],
                    "ml_confidence": (
                        float(risk[4])
                        if risk[4] is not None
                        else None
                    ),
                    "affected_file_count": risk[5],
                    "high_risk_file_count": risk[6],
                    "test_recommendations": risk[7] or [],
                    "ml_class_probabilities": risk[8] or {},
                    "risk_reasons": risk[9] or [],
                    "affected_files": risk[10] or [],
                    "analyzed_at": risk[11]
                }

            return {
                "id": pr[0],
                "repository": pr[1],
                "pr_number": pr[2],
                "title": pr[3],
                "state": pr[4],
                "github_url": pr[5],
                "total_files_changed": pr[6],
                "total_additions": pr[7],
                "total_deletions": pr[8],
                "total_changes": pr[9],
                "analyzed_at": pr[10],
                "files": files,
                "risk_analysis": risk_analysis
            }

    finally:
        connection.close()


@router.get("/risk-summary")
def get_risk_summary():

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                "SELECT COUNT(*) FROM pull_requests"
            )

            total_prs = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT
                    combined_risk_level,
                    COUNT(*)
                FROM risk_analyses
                GROUP BY combined_risk_level
                """
            )

            risk_rows = cursor.fetchall()

            combined_risk_distribution = {
                row[0]: row[1]
                for row in risk_rows
            }

            cursor.execute(
                """
                SELECT
                    ml_predicted_risk,
                    COUNT(*)
                FROM risk_analyses
                GROUP BY ml_predicted_risk
                """
            )

            ml_rows = cursor.fetchall()

            ml_risk_distribution = {
                row[0]: row[1]
                for row in ml_rows
            }

            cursor.execute(
                "SELECT COUNT(*) FROM repositories"
            )

            total_repositories = cursor.fetchone()[0]

            return {
                "total_repositories": total_repositories,
                "total_pull_requests": total_prs,
                "combined_risk_distribution": combined_risk_distribution,
                "ml_risk_distribution": ml_risk_distribution
            }

    finally:
        connection.close()