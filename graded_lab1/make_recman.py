#!/usr/bin/env python3
"""
CS 165 - Lab 1: generate YOUR copy of the buggy program.

Usage:
    python3 make_recman.py <your-student-id>

Use your official UCR SID / NetID exactly as the instructor specifies -- your
program is generated from it, and it is graded against that same id, so it must
match. Running it twice with the same id gives you the same program.

This creates, in the current folder:
    recman.c      your program (it works on normal input, but hides five bugs)
    Makefile      build it with `make` (AddressSanitizer) or `make plain`
    tests/        a few sample command scripts

Then:  make        # build with AddressSanitizer
       ./recman tests/sample1.txt
See the lab handout for what to do next.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recman_common as C

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 make_recman.py <your-student-id>")
    sid = sys.argv[1].strip()
    params = C.seeded(sid)
    C.write_student_files(".", params)
    print(f"Generated recman.c for id '{sid}' (build {params['build_id']}).")
    print("Next:  make   &&   ./recman tests/sample1.txt")

if __name__ == "__main__":
    main()
