import os

import joblib
import pandas as pd


MODEL_PATH = os.path.join(
    "ml",
    "model",
    "pr_risk_model.joblib"
)


FEATURES = [
    "total_files_changed",
    "total_additions",
    "total_deletions",
    "total_changes",
    "large_files_changed",
    "high_risk_files",
    "affected_file_count"
]


def load_model():
    """
    Load the trained PR risk model.
    """

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"ML model not found at: {MODEL_PATH}"
        )

    return joblib.load(
        MODEL_PATH
    )


def predict_risk(
    risk_analysis,
    dependency_analysis
):
    """
    Predict PR risk using the trained ML model.
    """

    model = load_model()

    affected_files = set()

    for dependency in dependency_analysis:

        for file in dependency.get(
            "affected_files",
            []
        ):
            affected_files.add(file)

    affected_file_count = len(
        affected_files
    )

    features = {
        "total_files_changed":
            risk_analysis.get(
                "total_files_changed",
                0
            ),

        "total_additions":
            risk_analysis.get(
                "total_additions",
                0
            ),

        "total_deletions":
            risk_analysis.get(
                "total_deletions",
                0
            ),

        "total_changes":
            risk_analysis.get(
                "total_changes",
                0
            ),

        "large_files_changed":
            risk_analysis.get(
                "large_files_changed",
                0
            ),

        "high_risk_files":
            len(
                risk_analysis.get(
                    "high_risk_files",
                    []
                )
            ),

        "affected_file_count":
            affected_file_count
    }

    input_data = pd.DataFrame(
        [features],
        columns=FEATURES
    )

    prediction = model.predict(
        input_data
    )[0]

    probabilities = model.predict_proba(
        input_data
    )[0]

    class_names = model.classes_

    confidence = float(
        max(probabilities)
    )

    probability_map = {
        class_name: float(probability)
        for class_name, probability
        in zip(
            class_names,
            probabilities
        )
    }

    return {
        "predicted_risk": prediction,
        "confidence": round(
            confidence,
            4
        ),
        "class_probabilities": probability_map,
        "features_used": features
    }
