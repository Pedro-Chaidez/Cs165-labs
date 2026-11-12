CC = clang
COMMON_FLAGS = -std=c11 -O1 -g -Wall -Wextra -Wpedantic -fno-omit-frame-pointer

.PHONY: all test reset clean

all: image image-asan fuzz_target

image: image.c image_cli.c image.h
	$(CC) $(COMMON_FLAGS) image.c image_cli.c -o $@

image-asan: image.c image_cli.c image.h
	$(CC) $(COMMON_FLAGS) -fsanitize=address,undefined image.c image_cli.c -o $@

fuzz_target: image.c fuzz_target.c image.h
	$(CC) $(COMMON_FLAGS) -fsanitize=fuzzer,address,undefined \
		image.c fuzz_target.c -o $@

test: image
	./image < tests/info.img | grep -qx accepted
	./image < tests/gray-check.img | grep -qx accepted
	./image < tests/meta-check.img | grep -qx accepted
	./image < tests/invalid.img | grep -qx rejected
	@echo "normal-input tests passed"

reset:
	rm -rf work
	mkdir -p work/no-dict-corpus work/no-dict-artifacts
	mkdir -p work/dict-corpus work/dict-artifacts work/min-corpus

clean:
	rm -rf image image-asan fuzz_target work __pycache__ \
		image.dSYM image-asan.dSYM fuzz_target.dSYM
