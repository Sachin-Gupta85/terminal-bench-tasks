"""Minimal Terminal-Bench style runner.

Builds a task image, starts a container, optionally runs the oracle
solution, then runs the pytest verifier inside the container.

Usage:
    python harness/run_eval.py --task tasks/log-error-summary --oracle
    python harness/run_eval.py --task tasks/log-error-summary --container <id>
"""
import argparse
import re
import subprocess
import sys
import uuid
from pathlib import Path


def sh(cmd, check=True):
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, check=check, text=True)


def read_timeout(task: Path, key: str, default: int) -> int:
    text = (task / "task.yaml").read_text()
    m = re.search(rf"^{key}:\s*(\d+)", text, re.MULTILINE)
    return int(m.group(1)) if m else default


def build_image(task: Path) -> str:
    tag = f"tb-{task.name}:latest"
    sh(["docker", "build", "-t", tag, str(task)])
    return tag


def start_container(tag: str) -> str:
    name = f"tb-{uuid.uuid4().hex[:8]}"
    sh(["docker", "run", "-d", "--name", name, tag, "sleep", "infinity"])
    return name


def run_oracle(task: Path, container: str, timeout: int) -> None:
    sh(["docker", "cp", str(task / "solution.sh"), f"{container}:/tmp/solution.sh"])
    subprocess.run(
        ["docker", "exec", container, "bash", "/tmp/solution.sh"],
        check=True, timeout=timeout,
    )


def run_tests(task: Path, container: str, timeout: int) -> bool:
    # tests are copied in only after the agent is done, so the agent never sees them
    sh(["docker", "cp", str(task / "tests"), f"{container}:/tests"])
    sh(["docker", "exec", container, "pip", "install", "-q", "pytest"])
    result = subprocess.run(
        ["docker", "exec", container, "python", "-m", "pytest", "-q", "/tests"],
        text=True, capture_output=True, timeout=timeout,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--task", required=True, type=Path)
    p.add_argument("--oracle", action="store_true", help="run solution.sh before testing")
    p.add_argument("--container", help="verify an existing container instead of starting one")
    p.add_argument("--keep", action="store_true", help="do not remove the container")
    args = p.parse_args()

    agent_timeout = read_timeout(args.task, "max_agent_timeout_sec", 300)
    test_timeout = read_timeout(args.task, "max_test_timeout_sec", 60)

    container = args.container
    started = False
    if not container:
        container = start_container(build_image(args.task))
        started = True

    try:
        if args.oracle:
            run_oracle(args.task, container, agent_timeout)
        passed = run_tests(args.task, container, test_timeout)
    finally:
        if started and not args.keep:
            sh(["docker", "rm", "-f", container], check=False)

    print("RESULT:", "PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
