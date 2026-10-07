from fastapi import APIRouter, HTTPException

from app.services.github_service import (
    get_pull_request,
    get_pull_request_files
)
from app.services.risk_service import analyze_risk
from app.services.test_recommendation_service import recommend_tests
from app.services.dependency_service import analyze_dependency_impact
from app.services.combined_risk_service import calculate_combined_risk
from app.services.ml_risk_service import predict_risk
from app.services.database_service import save_complete_analysis


router = APIRouter()


@router.get("/analyze/{owner}/{repo}/{pr_number}")
def analyze_pull_request(owner: str, repo: str, pr_number: int):

    try:
        pr_data = get_pull_request(owner, repo, pr_number)

        files = get_pull_request_files(
            owner,
            repo,
            pr_number
        )

        risk_analysis = analyze_risk(files)

        test_recommendations = recommend_tests(files)

        dependency_analysis = analyze_dependency_impact(
            files,
            project_directory="app"
        )

        combined_risk = calculate_combined_risk(
            risk_analysis,
            dependency_analysis
        )

        ml_prediction = predict_risk(
            risk_analysis,
            dependency_analysis
        )

        database_result = save_complete_analysis(
            owner=owner,
            repo=repo,
            pr_number=pr_number,
            pr_data=pr_data,
            files=files,
            risk_analysis=risk_analysis,
            combined_risk=combined_risk,
            ml_prediction=ml_prediction,
            test_recommendations=test_recommendations
        )

        return {
            "repository": f"{owner}/{repo}",
            "pr_number": pr_number,
            "title": pr_data["title"],
            "state": pr_data["state"],
            "url": pr_data["html_url"],
            "changed_files": len(files),

            "files": files,

            "risk_analysis": risk_analysis,

            "test_recommendations": test_recommendations,

            "dependency_analysis": dependency_analysis,

            "combined_risk": combined_risk,

            "ml_prediction": ml_prediction,

            "database": {
                "saved": True,
                "repository_id": database_result["repository_id"],
                "pull_request_id": database_result["pull_request_id"]
            }
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )