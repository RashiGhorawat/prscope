def recommend_tests(files):
    recommendations = []

    for file in files:
        filename = file.get("filename", "")
        filename_lower = filename.lower()

        tests = []
        reasons = []

        # --------------------------------------------------
        # Test files
        # --------------------------------------------------
        if (
            filename_lower.startswith("tests/")
            or "/tests/" in filename_lower
            or filename_lower.startswith("test_")
            or "/test_" in filename_lower
        ):
            tests.append("Run the modified test file and validate the test suite.")
            reasons.append(
                "The changed file is itself a test file, so the modified tests should be executed."
            )

        # --------------------------------------------------
        # Python files
        # --------------------------------------------------
        if filename_lower.endswith(".py"):

            # API / route files
            if (
                "/routes/" in filename_lower
                or filename_lower.startswith("routes/")
                or "/api/" in filename_lower
                or filename_lower.startswith("api/")
            ):
                tests.append("Run API endpoint tests.")
                tests.append("Run integration tests for affected endpoints.")
                reasons.append(
                    "The file contains API or route logic that can affect endpoint behavior."
                )

            # Service-layer files
            elif (
                "/services/" in filename_lower
                or filename_lower.startswith("services/")
            ):
                tests.append("Run unit tests for the modified service.")
                tests.append("Run integration tests for dependent components.")
                reasons.append(
                    "The file contains service-layer logic that may affect application behavior."
                )

            # Model-related files
            elif (
                "model" in filename_lower
                or "/models/" in filename_lower
                or filename_lower.startswith("models/")
            ):
                tests.append("Run model validation tests.")
                tests.append("Run prediction or data-processing tests if applicable.")
                reasons.append(
                    "The file appears to contain model or model-related logic."
                )

            # Database-related Python files
            elif (
                "database" in filename_lower
                or "db_" in filename_lower
                or filename_lower.startswith("db")
            ):
                tests.append("Run database integration tests.")
                tests.append("Validate database operations and queries.")
                reasons.append(
                    "The file appears to interact with database functionality."
                )

            # Generic Python
            else:
                tests.append("Run Python unit tests for the modified module.")
                reasons.append(
                    "The changed file is a Python module and may affect application logic."
                )

        # --------------------------------------------------
        # JavaScript / TypeScript / React
        # --------------------------------------------------
        elif filename_lower.endswith(
            (".js", ".jsx", ".ts", ".tsx")
        ):
            tests.append("Run frontend unit tests.")
            tests.append("Run component or integration tests for affected components.")
            reasons.append(
                "The file contains frontend JavaScript or TypeScript code."
            )

        # --------------------------------------------------
        # SQL
        # --------------------------------------------------
        elif filename_lower.endswith(".sql"):
            tests.append("Run database schema and query tests.")
            tests.append("Validate affected SQL queries or migrations.")
            reasons.append(
                "The file contains SQL that can affect database behavior."
            )

        # --------------------------------------------------
        # CI/CD configuration
        # --------------------------------------------------
        elif (
            ".github/workflows/" in filename_lower
            or filename_lower.endswith((".yml", ".yaml"))
        ):
            tests.append("Validate the configuration file.")
            tests.append("Run the affected CI/CD workflow.")
            reasons.append(
                "The changed file may affect application configuration or CI/CD execution."
            )

        # --------------------------------------------------
        # Configuration files
        # --------------------------------------------------
        elif filename_lower.endswith(
            (".json", ".toml", ".ini", ".cfg", ".conf")
        ):
            tests.append("Validate the configuration format.")
            tests.append("Run tests affected by the configuration change.")
            reasons.append(
                "The file contains configuration that may change application behavior."
            )

        # --------------------------------------------------
        # Documentation
        # --------------------------------------------------
        elif filename_lower.endswith((".md", ".txt")):
            tests.append("Check documentation formatting and links.")
            reasons.append(
                "The changed file contains documentation rather than application logic."
            )

        # --------------------------------------------------
        # Unknown file type
        # --------------------------------------------------
        else:
            tests.append(
                "Review the changed file and identify relevant tests."
            )
            reasons.append(
                "The file type does not match a known test recommendation rule."
            )

        recommendations.append(
            {
                "file": filename,
                "recommended_tests": tests,
                "reason": " ".join(reasons)
            }
        )

    return recommendations