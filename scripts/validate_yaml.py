import yaml, sys, glob, os

errors = []
for yaml_file in glob.glob("**/*.yaml", recursive=True) + glob.glob("**/*.yml", recursive=True):
    try:
        with open(yaml_file, "r") as f:
            yaml.safe_load(f)
    except yaml.YAMLError as e:
        errors.append(f"{yaml_file}: {e}")

if errors:
    for e in errors:
        print(f"::error::{e}")
    sys.exit(1)

print("All YAML files valid")