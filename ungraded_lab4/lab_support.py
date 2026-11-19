#!/usr/bin/env python3
"""Create and remove the local sandbox used by Ungraded Lab 4."""

from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work"
CACHE = ROOT / "__pycache__"
DEBUG_BUNDLE = ROOT / "note_writer.dSYM"
INBOX = WORK / "inbox"
NOTE = INBOX / "submission.txt"
GRADEBOOK = WORK / "gradebook.txt"

ORIGINAL_NOTE = "original student note\n"
ORIGINAL_GRADEBOOK = "CS165 GRADES: DO NOT MODIFY\n"


def reset() -> None:
    if WORK.exists() or WORK.is_symlink():
        if WORK.is_symlink():
            WORK.unlink()
        else:
            shutil.rmtree(WORK)
    INBOX.mkdir(parents=True)
    NOTE.write_text(ORIGINAL_NOTE, encoding="utf-8")
    GRADEBOOK.write_text(ORIGINAL_GRADEBOOK, encoding="utf-8")


def clean() -> None:
    if WORK.is_symlink():
        WORK.unlink()
    elif WORK.exists():
        shutil.rmtree(WORK)
    if CACHE.exists():
        shutil.rmtree(CACHE)
    if DEBUG_BUNDLE.exists():
        shutil.rmtree(DEBUG_BUNDLE)


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"reset", "clean"}:
        raise SystemExit("usage: python3 lab_support.py {reset|clean}")
    if sys.argv[1] == "reset":
        reset()
        print("created a fresh work/ sandbox")
    else:
        clean()
        print("removed the work/ sandbox")


if __name__ == "__main__":
    main()

