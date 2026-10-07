from app.services.dependency_service import scan_project_dependencies


target_module = "app.services.risk_service"


affected_files = scan_project_dependencies(
    project_directory="app",
    target_module=target_module
)


print("Target module:")
print(target_module)

print("\nPotentially affected files:")

if affected_files:
    for file in affected_files:
        print("-", file)
else:
    print("No files found.")