CC = clang
COMMON_FLAGS = -std=c11 -O1 -g -Wall -Wextra -Wpedantic -fno-omit-frame-pointer

.PHONY: all test demo-reset clean

all: packet packet-asan fuzz_target

packet: packet.c packet_cli.c packet.h
	$(CC) $(COMMON_FLAGS) packet.c packet_cli.c -o $@

packet-asan: packet.c packet_cli.c packet.h
	$(CC) $(COMMON_FLAGS) -fsanitize=address packet.c packet_cli.c -o $@

fuzz_target: packet.c fuzz_target.c packet.h
	$(CC) $(COMMON_FLAGS) -fsanitize=fuzzer,address packet.c fuzz_target.c -o $@

test: packet
	./packet < tests/show.pkt | grep -qx accepted
	./packet < tests/store-safe.pkt | grep -qx accepted
	./packet < tests/invalid.pkt | grep -qx rejected
	@echo "normal-input tests passed"

demo-reset:
	rm -rf work
	mkdir -p work/no-dict-corpus work/no-dict-artifacts
	mkdir -p work/dict-corpus work/dict-artifacts work/min-corpus
	cp seeds/*.pkt work/no-dict-corpus/
	cp seeds/*.pkt work/dict-corpus/

clean:
	rm -rf packet packet-asan fuzz_target work __pycache__ \
		packet.dSYM packet-asan.dSYM fuzz_target.dSYM
