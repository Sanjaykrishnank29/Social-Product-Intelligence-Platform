import importlib.metadata
import os

dists = sorted((dist.metadata["Name"], dist.version) for dist in importlib.metadata.distributions())
output_path = "pipeline/requirements_complete.txt"

with open(output_path, "w", encoding="utf-8") as f:
    for name, version in dists:
        # Skip standard library/system modules if any show up, and write packages
        f.write(f"{name}=={version}\n")

print(f"Exported package list to {output_path}")
