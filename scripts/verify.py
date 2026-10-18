# verify.py: runs every project check (ruff, mypy, pytest) and prints one table.
# Each row says PASS, FAIL or NO TESTS with its time; only PASS counts as a pass.
# Exits 0 only if every row is PASS, so a human and CI read the same answer.
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PYTEST_NO_TESTS_EXIT_CODE = 5

CHECKS = [
    ("ruff", [sys.executable, "-m", "ruff", "check", "."]),
    ("mypy", [sys.executable, "-m", "mypy", "src", "scripts", "tests"]),
    ("pytest", [sys.executable, "-m", "pytest", "-q"]),
]


def run_check(name: str, command: list[str]) -> tuple[str, float]:
    start = time.perf_counter()
    result = subprocess.run(
        command, check=False, cwd=REPO_ROOT, capture_output=True, text=True
    )
    seconds = time.perf_counter() - start
    if result.returncode == 0:
        return "PASS", seconds
    if name == "pytest" and result.returncode == PYTEST_NO_TESTS_EXIT_CODE:
        return "NO TESTS", seconds
    print(f"--- {name} output ---\n{result.stdout}{result.stderr}")
    return "FAIL", seconds


def main() -> int:
    rows = []
    for name, command in CHECKS:
        status, seconds = run_check(name, command)
        rows.append((name, status, seconds))

    print(f"{'check':<8} {'result':<9} {'seconds':>7}")
    for name, status, seconds in rows:
        print(f"{name:<8} {status:<9} {seconds:>7.2f}")
    all_passed = all(status == "PASS" for _, status, _ in rows)
    overall = "PASS" if all_passed else "FAIL"
    total = sum(seconds for _, _, seconds in rows)
    print(f"{'overall':<8} {overall:<9} {total:>7.2f}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
