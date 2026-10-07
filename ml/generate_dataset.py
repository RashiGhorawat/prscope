import os
import random

import numpy as np
import pandas as pd


random.seed(42)
np.random.seed(42)


def generate_low_risk_sample():
    """
    Generate a low-risk PR.
    """

    total_files_changed = np.random.randint(1, 5)

    total_additions = np.random.randint(
        0,
        80
    )

    total_deletions = np.random.randint(
        0,
        50
    )

    total_changes = (
        total_additions
        + total_deletions
    )

    large_files_changed = np.random.randint(
        0,
        2
    )

    high_risk_files = np.random.randint(
        0,
        2
    )

    affected_file_count = np.random.randint(
        0,
        2
    )

    return {
        "total_files_changed":
            total_files_changed,

        "total_additions":
            total_additions,

        "total_deletions":
            total_deletions,

        "total_changes":
            total_changes,

        "large_files_changed":
            large_files_changed,

        "high_risk_files":
            high_risk_files,

        "affected_file_count":
            affected_file_count,

        "risk_level":
            "Low"
    }


def generate_medium_risk_sample():
    """
    Generate a medium-risk PR.
    """

    total_files_changed = np.random.randint(
        5,
        16
    )

    total_additions = np.random.randint(
        100,
        500
    )

    total_deletions = np.random.randint(
        50,
        350
    )

    total_changes = (
        total_additions
        + total_deletions
    )

    large_files_changed = np.random.randint(
        1,
        5
    )

    high_risk_files = np.random.randint(
        0,
        3
    )

    affected_file_count = np.random.randint(
        1,
        7
    )

    return {
        "total_files_changed":
            total_files_changed,

        "total_additions":
            total_additions,

        "total_deletions":
            total_deletions,

        "total_changes":
            total_changes,

        "large_files_changed":
            large_files_changed,

        "high_risk_files":
            high_risk_files,

        "affected_file_count":
            affected_file_count,

        "risk_level":
            "Medium"
    }


def generate_high_risk_sample():
    """
    Generate a high-risk PR.
    """

    total_files_changed = np.random.randint(
        15,
        41
    )

    total_additions = np.random.randint(
        500,
        2001
    )

    total_deletions = np.random.randint(
        300,
        1501
    )

    total_changes = (
        total_additions
        + total_deletions
    )

    large_files_changed = np.random.randint(
        3,
        11
    )

    high_risk_files = np.random.randint(
        2,
        8
    )

    affected_file_count = np.random.randint(
        5,
        21
    )

    return {
        "total_files_changed":
            total_files_changed,

        "total_additions":
            total_additions,

        "total_deletions":
            total_deletions,

        "total_changes":
            total_changes,

        "large_files_changed":
            large_files_changed,

        "high_risk_files":
            high_risk_files,

        "affected_file_count":
            affected_file_count,

        "risk_level":
            "High"
    }


def generate_dataset(
    samples_per_class=1000
):
    """
    Generate a balanced synthetic PR dataset.
    """

    rows = []

    # Low-risk examples
    for _ in range(samples_per_class):

        rows.append(
            generate_low_risk_sample()
        )

    # Medium-risk examples
    for _ in range(samples_per_class):

        rows.append(
            generate_medium_risk_sample()
        )

    # High-risk examples
    for _ in range(samples_per_class):

        rows.append(
            generate_high_risk_sample()
        )

    random.shuffle(rows)

    return pd.DataFrame(rows)


def main():

    dataset = generate_dataset(
        samples_per_class=1000
    )

    os.makedirs(
        "ml",
        exist_ok=True
    )

    output_path = (
        "ml/pr_risk_training_data.csv"
    )

    dataset.to_csv(
        output_path,
        index=False
    )

    print(
        f"Dataset created: {output_path}"
    )

    print(
        f"Total samples: {len(dataset)}"
    )

    print(
        "\nRisk distribution:"
    )

    print(
        dataset["risk_level"].value_counts()
    )

    print(
        "\nFirst 5 rows:"
    )

    print(
        dataset.head()
    )


if __name__ == "__main__":
    main()