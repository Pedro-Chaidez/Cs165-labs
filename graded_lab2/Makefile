UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)
ifneq ($(UNAME_S),Linux)
$(error Lab 2 must be built on the course Linux/x86-64 machine)
endif
ifneq ($(UNAME_M),x86_64)
$(error Lab 2 must be built on the course Linux/x86-64 machine)
endif

CC = gcc
CFLAGS  = -g -O0 -Wall -Wextra -Wno-format-security \
          -fno-omit-frame-pointer -fstack-protector-strong -fno-pie
LDFLAGS = -no-pie -Wl,-z,noexecstack

all: vault

vault: vault.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

# Benign sanity check (no exploit): a greeting, then an accepted/rejected request.
test: vault
	./vault < tests/accept.bin
	./vault < tests/reject.bin

clean:
	rm -f vault payload.bin
tar:
	tar czf lab2-submission.tgz vault.c exploit.py writeup.md

.PHONY: all test clean
