CC ?= cc
CFLAGS ?= -std=c11 -O0 -g -Wall -Wextra -Wpedantic
# _DARWIN_C_SOURCE exposes O_NOFOLLOW on macOS; it is harmless on Linux.
CPPFLAGS ?= -D_POSIX_C_SOURCE=200809L -D_DARWIN_C_SOURCE

.PHONY: all reset test demo check clean

all: note_writer

note_writer: note_writer.c
	$(CC) $(CPPFLAGS) $(CFLAGS) $< -o $@

reset:
	python3 lab_support.py reset

test: note_writer
	python3 check_lab.py functional

demo: note_writer
	python3 exploit.py

check: note_writer
	python3 check_lab.py all

clean:
	$(RM) note_writer
	python3 lab_support.py clean

