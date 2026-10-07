import os

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
from sklearn.model_selection import train_test_split


DATASET_PATH = "ml/pr_risk_training_data.csv"
MODEL_PATH = "ml/model/pr_risk_model.joblib"


FEATURES = [
    "total_files_changed",
    "total_additions",
    "total_deletions",
    "total_changes",
    "large_files_changed",
    "high_risk_files",
    "affected_file_count"
]

TARGET = "risk_level"


def main():

    # --------------------------------------------------
    # Load dataset
    # --------------------------------------------------

    print("Loading training dataset...")

    dataset = pd.read_csv(
        DATASET_PATH
    )

    print(
        f"Dataset shape: {dataset.shape}"
    )

    # --------------------------------------------------
    # Separate features and target
    # --------------------------------------------------

    X = dataset[FEATURES]

    y = dataset[TARGET]

    # --------------------------------------------------
    # Train/test split
    # --------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    print(
        f"Training samples: {len(X_train)}"
    )

    print(
        f"Testing samples: {len(X_test)}"
    )

    # --------------------------------------------------
    # Create Random Forest model
    # --------------------------------------------------

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=42,
        class_weight="balanced"
    )

    # --------------------------------------------------
    # Train model
    # --------------------------------------------------

    print("\nTraining Random Forest...")

    model.fit(
        X_train,
        y_train
    )

    print("Training complete.")

    # --------------------------------------------------
    # Predictions
    # --------------------------------------------------

    y_pred = model.predict(
        X_test
    )

    # --------------------------------------------------
    # Accuracy
    # --------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    print(
        f"\nAccuracy: {accuracy:.4f}"
    )

    # --------------------------------------------------
    # Classification report
    # --------------------------------------------------

    print(
        "\nClassification Report:"
    )

    print(
        classification_report(
            y_test,
            y_pred
        )
    )

    # --------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------

    print(
        "Confusion Matrix:"
    )

    print(
        confusion_matrix(
            y_test,
            y_pred,
            labels=[
                "Low",
                "Medium",
                "High"
            ]
        )
    )

    # --------------------------------------------------
    # Feature importance
    # --------------------------------------------------

    print(
        "\nFeature Importance:"
    )

    feature_importance = pd.DataFrame(
        {
            "feature": FEATURES,
            "importance": model.feature_importances_
        }
    ).sort_values(
        by="importance",
        ascending=False
    )

    print(
        feature_importance.to_string(
            index=False
        )
    )

    # --------------------------------------------------
    # Save model
    # --------------------------------------------------

    os.makedirs(
        "ml/model",
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_PATH
    )

    print(
        f"\nModel saved to: {MODEL_PATH}"
    )


if __name__ == "__main__":
    main()
