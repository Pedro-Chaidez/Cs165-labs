#!/usr/bin/env python3
"""Instance-generation logic for CS 165 Lab 2 (graded, hardened)."""
import hashlib
import os
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_TEMPLATE = os.path.join(HERE, "vault_base.c.tmpl")


def seeded(student_id):
    digest = hashlib.sha256(student_id.encode()).digest()
    build_id = hashlib.sha256(student_id.encode()).hexdigest()[:8]
    return {
        "student_id": student_id,
        "note_size": [40, 48, 56, 64][digest[0] % 4],
        "pad_words": [1, 2, 3, 4][digest[1] % 4],
        "greet_buf": [48, 80, 128, 192][digest[2] % 4],  # varies the canary leak index per student
        "build_id": build_id,
        "win_token": "vault-" + build_id,
    }


def render_student(params):
    with open(BASE_TEMPLATE) as source:
        text = source.read()
    return (text.replace("@@NOTE_SIZE@@", str(params["note_size"]))
                .replace("@@PAD_WORDS@@", str(params["pad_words"]))
                .replace("@@GREET_BUF@@", str(params["greet_buf"]))
                .replace("@@BUILD_ID@@", params["build_id"])
                .replace("@@WIN_TOKEN@@", params["win_token"]))


# Vulnerable build: stack canary ON, NX on, non-PIE (so win() has a fixed
# address).  Deliberately NO _FORTIFY_SOURCE and -O0: fortify would turn the
# unchecked memcpy into a checked one and abort before the canary is ever in
# play, which would make the lab unsolvable.  The canary is the single runtime
# obstacle; you defeat it with the format-string leak.
MAKEFILE = """UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)
ifneq ($(UNAME_S),Linux)
$(error Lab 2 must be built on the course Linux/x86-64 machine)
endif
ifneq ($(UNAME_M),x86_64)
$(error Lab 2 must be built on the course Linux/x86-64 machine)
endif

CC = gcc
CFLAGS  = -g -O0 -Wall -Wextra -Wno-format-security \\
          -fno-omit-frame-pointer -fstack-protector-strong -fno-pie
LDFLAGS = -no-pie -Wl,-z,noexecstack

all: vault

vault: vault.c
\t$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

# Benign sanity check (no exploit): a greeting, then an accepted/rejected request.
test: vault
\t./vault < tests/accept.bin
\t./vault < tests/reject.bin

clean:
\trm -f vault payload.bin

.PHONY: all test clean
"""


def _benign(name, verb):
    # <name line>\n<2-byte little-endian length><4-byte request>
    return name + b"\n" + struct.pack("<H", 4) + verb


def write_student_files(out_dir, params):
    os.makedirs(os.path.join(out_dir, "tests"), exist_ok=True)
    with open(os.path.join(out_dir, "vault.c"), "w") as output:
        output.write(render_student(params))
    with open(os.path.join(out_dir, "Makefile"), "w") as output:
        output.write(MAKEFILE)
    tests = {
        "accept.bin": _benign(b"world", b"OPEN"),
        "reject.bin": _benign(b"world", b"NOPE"),
    }
    for fname, data in tests.items():
        with open(os.path.join(out_dir, "tests", fname), "wb") as output:
            output.write(data)
