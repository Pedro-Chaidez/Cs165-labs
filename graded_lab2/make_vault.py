#!/usr/bin/env python3
"""Generate your personal CS 165 Lab 2 (graded) instance.

    python3 make_vault.py <your-student-id>

This writes vault.c, Makefile, and tests/ into the current directory, seeded
from your student ID.  Your note size, padding, and win() token are unique to
you, so your offsets differ from everyone else's.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stacklab_common as C


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 make_vault.py <your-student-id>")
    student_id = sys.argv[1].strip()
    params = C.seeded(student_id)
    C.write_student_files(".", params)
    print(f"Generated vault.c for '{student_id}' (build {params['build_id']}).")
    print("Next:  make  &&  make test")


if __name__ == "__main__":
    main()
