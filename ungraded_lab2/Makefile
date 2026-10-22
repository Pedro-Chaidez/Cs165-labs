# CS 165 Lab 2 (ungraded prep) -- build the teaching target.
# Run this on the course Linux/x86-64 VM.
UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)
ifneq ($(UNAME_S),Linux)
$(error Lab 2 must be built on the course Linux/x86-64 machine)
endif
ifneq ($(UNAME_M),x86_64)
$(error Lab 2 must be built on the course Linux/x86-64 machine)
endif

CC = gcc
# Teaching build: no canary, no PIE, frame pointer kept -> simple, stable layout.
VULN_CFLAGS  = -g -O0 -Wall -Wextra -fno-omit-frame-pointer -fno-stack-protector -fno-pie
VULN_LDFLAGS = -no-pie -Wl,-z,noexecstack
# Hardened build: everything turned on, for the "defense" comparison at the end.
HARDEN_CFLAGS  = -g -O2 -Wall -Wextra -fstack-protector-strong -D_FORTIFY_SOURCE=2 -fPIE
HARDEN_LDFLAGS = -pie -Wl,-z,relro,-z,now -Wl,-z,noexecstack

all: vault

vault: vault.c
	$(CC) $(VULN_CFLAGS) -o $@ $< $(VULN_LDFLAGS)

harden: vault-hardened
vault-hardened: vault.c
	$(CC) $(HARDEN_CFLAGS) -o $@ $< $(HARDEN_LDFLAGS)

# Benign sanity check (no exploit).
test: vault
	./vault < tests/accept.bin
	./vault < tests/reject.bin

clean:
	rm -f vault vault-hardened payload.bin

.PHONY: all harden test clean
