#!/usr/bin/env python3
"""Functional and adversarial checks for Ungraded Lab 4."""

import os
import subprocess
import sys

import lab_support as lab


BINARY = lab.ROOT / "note_writer"


def run_writer(*arguments, input_text=None):
    return subprocess.run(
        [str(BINARY), *arguments],
        cwd=lab.ROOT,
        input=input_text,
        capture_output=True,
        text=True,
        timeout=5,
    )


def normal_update():
    lab.reset()
    result = run_writer(lab.NOTE.name, "normal update")
    ok = (
        result.returncode == 0
        and lab.NOTE.read_text(encoding="utf-8") == "normal update\n"
        and lab.GRADEBOOK.read_text(encoding="utf-8") == lab.ORIGINAL_GRADEBOOK
    )
    return ok, "normal note update"


def static_symlink():
    lab.reset()
    lab.NOTE.unlink()
    lab.NOTE.symlink_to("../gradebook.txt")
    result = run_writer(lab.NOTE.name, "STATIC SYMLINK ATTACK")
    ok = (
        result.returncode != 0
        and lab.GRADEBOOK.read_text(encoding="utf-8") == lab.ORIGINAL_GRADEBOOK
    )
    return ok, "pre-existing symlink is rejected"


def replacement_race():
    lab.reset()
    process = subprocess.Popen(
        [str(BINARY), "--pause", lab.NOTE.name, "RACE ATTACK"],
        cwd=lab.ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert process.stdout is not None
    assert process.stdin is not None
    marker = process.stdout.readline().strip()
    if marker != f"CHECKED {lab.NOTE.name}":
        process.kill()
        process.communicate()
        return False, "replacement race (missing CHECKED synchronization marker)"

    lab.NOTE.unlink()
    lab.NOTE.symlink_to("../gradebook.txt")
    process.stdin.write("\n")
    process.stdin.flush()
    process.communicate(timeout=5)
    ok = lab.GRADEBOOK.read_text(encoding="utf-8") == lab.ORIGINAL_GRADEBOOK
    return ok, "post-check pathname replacement cannot redirect the write"


def hard_link():
    lab.reset()
    lab.NOTE.unlink()
    os.link(lab.GRADEBOOK, lab.NOTE)
    result = run_writer(lab.NOTE.name, "HARD LINK ATTACK")
    ok = (
        result.returncode != 0
        and lab.GRADEBOOK.read_text(encoding="utf-8") == lab.ORIGINAL_GRADEBOOK
    )
    return ok, "multiply linked file is rejected before truncation"


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) == 2 else "all"
    if mode not in {"functional", "all"}:
        raise SystemExit("usage: python3 check_lab.py {functional|all}")
    if not BINARY.is_file():
        raise SystemExit("note_writer is missing; run make first")

    checks = [normal_update]
    if mode == "all":
        checks.extend([static_symlink, replacement_race, hard_link])

    failures = 0
    for check in checks:
        try:
            passed, description = check()
        except (OSError, subprocess.SubprocessError) as error:
            passed, description = False, f"{check.__name__}: {error}"
        print(f"{'PASS' if passed else 'FAIL'}  {description}")
        failures += not passed

    if failures:
        raise SystemExit(f"{failures} check(s) failed")
    print("all requested checks passed")


if __name__ == "__main__":
    main()

