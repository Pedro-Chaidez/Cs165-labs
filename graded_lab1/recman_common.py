#!/usr/bin/env python3
"""
recman_common.py -- shared, NON-SENSITIVE logic for CS 165 Lab 1.

Both the instructor generator (gen_instance.py) and the student generator
(student_kit/make_recman.py) import this so they produce the byte-identical
recman.c for a given id. It contains NOTHING about the bugs, fixes, triggers,
or answer key -- only how the program's surface details (buffer sizes, table
size, line-number filler, build id) are derived from an id, plus the Makefile
and sample scripts. It is therefore safe to hand to students.
"""
import os, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))

# The base template is the vulnerable program with the instructor's bug tags
# already stripped. It still contains @@TOKENS@@ that get substituted per id.
# Look for it next to this module (student kit) or under reference/src (repo).
def _find_base():
    for c in (os.path.join(HERE, "recman_base.c.tmpl"),
              os.path.join(HERE, "reference", "src", "recman_base.c.tmpl")):
        if os.path.exists(c):
            return c
    return os.path.join(HERE, "recman_base.c.tmpl")
BASE_TMPL = _find_base()

def seeded(student_id):
    """Deterministically derive an instance's surface parameters from an id."""
    h = hashlib.sha256(student_id.encode()).digest()
    namelen = [24, 28, 32, 40, 48][h[0] % 5]
    maxrec  = [32, 48, 64][h[1] % 3]
    filler  = h[2] % 7            # comment lines inserted -> shifts line numbers
    build   = hashlib.sha256(student_id.encode()).hexdigest()[:8]
    return dict(student_id=student_id, namelen=namelen, maxrec=maxrec,
                filler=filler, build_id=build)

def render_student(params, base_path=None):
    """Substitute the per-id tokens into the base template -> the student's recman.c text."""
    src = open(base_path or BASE_TMPL).read()
    filler = "\n".join(
        ["// ------------------------------------------------------------"] * params["filler"])
    return (src.replace("@@NAMELEN@@", str(params["namelen"]))
               .replace("@@MAXREC@@",  str(params["maxrec"]))
               .replace("@@LINELEN@@", "256")
               .replace("@@BUILD_ID@@", params["build_id"])
               .replace("@@FILLER@@",  filler))

MAKEFILE = """CC      = gcc
CFLAGS  = -g -O0 -fsanitize=address -fno-omit-frame-pointer -Wall
TARGET  = recman
SRC     = recman.c

all: $(TARGET)

$(TARGET): $(SRC)
\t$(CC) $(CFLAGS) -o $(TARGET) $(SRC)

# build without the sanitizer (closer to the course VM's default build)
plain: $(SRC)
\t$(CC) -g -O0 -Wall -o $(TARGET) $(SRC)

clean:
\trm -f $(TARGET)

# bundle your submission: patched source, triggers, and writeup
tar:
\ttar czf lab1-submission.tgz recman.c triggers writeup.md
.PHONY: all plain clean tar
"""

SAMPLE_TESTS = {
    "sample1.txt": "add 1\nname 1 alice\nstr 1 hello\nshow 1\n",
    "sample2.txt": "add 2\nstr 2 abc\ngrow 2 4\nshow 2\ndel 2\n",
    "sample3.txt": "add 3\nadd 4\nname 3 bob\nlink 3 4\nshow 4\n",
}

def write_student_files(out_dir, params, base_path=None):
    """Write recman.c + Makefile + tests/ into out_dir. Returns the recman.c text."""
    os.makedirs(os.path.join(out_dir, "tests"), exist_ok=True)
    src = render_student(params, base_path)
    open(os.path.join(out_dir, "recman.c"), "w").write(src)
    open(os.path.join(out_dir, "Makefile"), "w").write(MAKEFILE)
    for name, body in SAMPLE_TESTS.items():
        open(os.path.join(out_dir, "tests", name), "w").write(body)
    return src
