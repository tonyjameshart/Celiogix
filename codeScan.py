import os
import subprocess


def run_linter(tool, filepath):
    try:
        result = subprocess.run(
            ["python", "-m", tool, filepath], capture_output=True, text=True, check=False
        )
        return result.stdout.strip() if result.returncode != 0 else ""
    except Exception as e:
        return f"[{tool}] Error: {e}"


def review_python_tree(root_dir, exclude_dirs=None, output_file="results.txt"):
    exclude_dirs = set(exclude_dirs or [])
    with open(output_file, "w", encoding="utf-8") as out:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Skip excluded directories
            if any(excluded in dirpath for excluded in exclude_dirs):
                continue

            for file in filenames:
                if file.endswith(".py"):
                    full_path = os.path.join(dirpath, file)
                    out.write(f"\n🔍 Reviewing: {full_path}\n")

                    for tool in ["ruff", "flake8", "pylint"]:
                        output = run_linter(tool, full_path)
                        if output:
                            out.write(f"\n[{tool}]\n{output}\n")


if __name__ == "__main__":
    review_python_tree(
        root_dir=r"D:\GitHub\Celiogix",
        exclude_dirs=["venv", "__pycache__"],
        output_file="results.txt",
    )
