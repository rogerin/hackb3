import subprocess
import os

build_dir = "vendor/tree-sitter-python/build"
os.makedirs(build_dir, exist_ok=True)

subprocess.run(
    ["tree-sitter", "build", "--output", os.path.join(build_dir, "my-languages.so")],
    cwd="vendor/tree-sitter-python"
)
