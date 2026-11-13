# CS 165 Graded Lab 3 Report

- Student name: Pedro Chaidez
- Net ID: 862443697

## 1. Program understanding

- The parser (parse_image_message in image.c) accepts byte sequences starting with the 5-byte header IMG2; followed by semicolon-terminated KEY=VALUE; fields (FMT, OP, AUTH, W, H, and DATA) in any order.
- Format validation (format_channels): Requires FMT to be GRAY (1 channel), RGB (3 channels), or META (1 channel).
- Dimension validation (parse_dimension and multiply_size): Requires W and H to be non-empty decimal strings representing integers from 1 through 64, and computes pixel_count = width * height and bytes_needed = pixel_count * channels.
- Operation branch OP=INFO: Succeeds immediately (return 1) once format and dimensions are valid.
- Operation branch OP=CHECK: If FMT=META, requires DATA to start with the prefix CS165:; otherwise (GRAY or RGB), requires DATA to be present with exact length payload.len == bytes_needed.
- Operation branch OP=THUMB: Requires AUTH=YES and FMT not equal to META (GRAY or RGB), then calls create_thumbnail, which verifies that DATA has at least bytes_needed bytes (payload.len >= bytes_needed), allocates a buffer, copies bytes_needed bytes from DATA, touches the first and last bytes via observation_sink, frees the buffer, and returns 1.

## 2. Harness

- In fuzz_target.c, LLVMFuzzerTestOneInput passes the fuzzer-supplied buffer data and byte length size directly to parse_image_message(data, size) once per iteration and returns 0.
- The harness is suitable for repeated in-process execution because it performs no file or console I/O and does not call exit() or abort().
- It frees any dynamically allocated heap memory inside create_thumbnail before returning.
- It relies on no persistent per-input state that alters control flow across invocations (observation_sink is only written to prevent dead-code elimination).

## 3. Seed corpus

- Command to create seeds/info-rgb.img: printf 'IMG2;FMT=RGB;OP=INFO;AUTH=NO;W=2;H=3;DATA=;' > seeds/info-rgb.img
- Purpose of seeds/info-rgb.img: Targets the FMT=RGB (3-channel) path and the OP=INFO operation branch.
- Command to create seeds/check-gray.img: printf 'IMG2;FMT=GRAY;OP=CHECK;AUTH=NO;W=2;H=3;DATA=abcdef;' > seeds/check-gray.img
- Purpose of seeds/check-gray.img: Targets the FMT=GRAY (1-channel) path and the OP=CHECK branch where payload.len == bytes_needed.
- Command to create seeds/check-meta.img: printf 'IMG2;FMT=META;OP=CHECK;AUTH=NO;W=1;H=1;DATA=CS165:lab;' > seeds/check-meta.img
- Purpose of seeds/check-meta.img: Targets the FMT=META path and the OP=CHECK branch requiring the CS165: prefix in DATA.
- Command to create seeds/thumb-gray.img: python3 -c 'import sys; sys.stdout.write("IMG2;FMT=RGB;OP=THUMB;AUTH=YES;W=5;H=17;DATA=" + "A"*300 + ";")' > seeds/thumb-gray.img
- Purpose of seeds/thumb-gray.img: Targets the authorized thumbnail path (OP=THUMB, AUTH=YES, non-META format) and exercises normal execution inside create_thumbnail near the 255-byte allocation boundary (bytes_needed = 255).

## 4. Fuzzing without a dictionary

- Command to populate work/no-dict-corpus: cp seeds/*.img work/no-dict-corpus/
- Command to run without dictionary: ./fuzz_target -max_total_time=30 -artifact_prefix=work/no-dict-artifacts/ work/no-dict-corpus
- Run duration: 31s (2,875,711 runs)
- Final cov: 89
- Final ft: 274
- Final corpus size: 81 (5214 bytes)
- Crash artifacts produced: 0

## 5. Fuzzing with a dictionary

- Command to reset work directories: make reset
- Command to populate work/dict-corpus from seeds: cp seeds/*.img work/dict-corpus/
- First dictionary command tried (with default input reduction): ./fuzz_target -dict=tokens.dict -max_total_time=30 -artifact_prefix=work/dict-artifacts/ work/dict-corpus
- Final dictionary command used to generate the crash artifact and evolve work/dict-corpus: ./fuzz_target -reduce_inputs=0 -dict=tokens.dict -max_total_time=30 -artifact_prefix=work/dict-artifacts/ work/dict-corpus
- Run duration: <1s (16,000 runs until crash)
- Final cov: 89
- Final ft: 220
- Final corpus size: 61 (8873 bytes)
- Crash artifacts produced: 1 (work/dict-artifacts/crash-6b4ffb0ae96c525bdf517589c9ba3d7f57222c3a)

## 6. Crash investigation

- Sanitizer finding: AddressSanitizer: heap-buffer-overflow (WRITE of size 306 at 0 bytes after a 50-byte heap region allocated via (uint8_t)bytes_needed).
- Relevant function: create_thumbnail in image.c (specifically the memcpy(thumbnail, payload.ptr, bytes_needed) call on line 124 after malloc(allocation_size) on line 121).
- Command to reproduce crash with image-asan: ./image-asan < work/dict-artifacts/crash-6b4ffb0ae96c525bdf517589c9ba3d7f57222c3a
- Command to reproduce crash with fuzz_target: ./fuzz_target work/dict-artifacts/crash-6b4ffb0ae96c525bdf517589c9ba3d7f57222c3a
- Reproduction result: Both commands deterministically reproduced the identical AddressSanitizer heap-buffer-overflow report in create_thumbnail outside of a fuzzing campaign.

## 7. Crash minimization

- Command used to minimize the crash artifact: ./fuzz_target -minimize_crash=1 -exact_artifact_path=minimized-crash.img -max_total_time=30 work/dict-artifacts/crash-6b4ffb0ae96c525bdf517589c9ba3d7f57222c3a
- Command to check byte counts: wc -c work/dict-artifacts/crash-6b4ffb0ae96c525bdf517589c9ba3d7f57222c3a minimized-crash.img
- Original crash size: 358 bytes
- Minimized crash size: 351 bytes
- Required part 1: The IMG2; header at the start of the message.
- Required part 2: A non-META format (FMT=RGB;, 3 channels).
- Required part 3: OP=THUMB; and AUTH=YES; to pass the operation and authorization checks.
- Required part 4: Valid dimensions W=6; and H=17; (between 1 and 64) whose product with channels yields bytes_needed = 6 * 17 * 3 = 306 >= 256, causing (uint8_t)bytes_needed to truncate to a 50-byte allocation (306 % 256 = 50).
- Required part 5: A DATA= field containing at least 306 bytes prior to ; so the payload.len < bytes_needed check passes and memcpy writes 306 bytes into the 50-byte heap buffer (306 payload bytes + 45 header/field bytes = 351 bytes minimum).

## 8. Corpus minimization

- Command used to minimize work/dict-corpus into work/min-corpus: ./fuzz_target -merge=1 work/min-corpus work/dict-corpus
- Command to count corpus files before and after minimization: ls -1 work/dict-corpus | wc -l && ls -1 work/min-corpus | wc -l
- Corpus size before minimization: 61 files
- Corpus size after minimization: 48 files (6125 bytes)
- What the minimized corpus preserves: Corpus minimization (-merge=1) preserves the union of all coverage edges and coverage features (cov: 89 and ft: 220) discovered across the original 61-file corpus while selecting a smaller subset of 48 files that achieve that exact same coverage.
- Difference from crash minimization: Unlike crash minimization, which shrinks a single failing input while preserving a specific sanitizer error, corpus minimization reduces a collection of non-crashing inputs while preserving overall code coverage across the parser.

## 9. Program fix

- Code change: In create_thumbnail (image.c), removed the narrowing cast uint8_t allocation_size = (uint8_t)bytes_needed; and passed bytes_needed (type size_t) directly to malloc(bytes_needed).
- Why it prevents the error: width and height can each be up to 64 and channels can be up to 3, so bytes_needed can reach 12,288 bytes; casting bytes_needed to uint8_t truncated any value >= 256 modulo 256, causing malloc to allocate a buffer smaller than bytes_needed before memcpy copied bytes_needed bytes into it, whereas malloc(bytes_needed) ensures the heap buffer always matches the exact number of bytes copied by memcpy.
- Commands to rebuild and run regression tests: make all && make test
- Commands to verify crash artifacts after fix: ./image-asan < work/dict-artifacts/crash-6b4ffb0ae96c525bdf517589c9ba3d7f57222c3a && ./image-asan < minimized-crash.img && ./fuzz_target work/dict-artifacts/crash-6b4ffb0ae96c525bdf517589c9ba3d7f57222c3a minimized-crash.img
- Command for final sanitizer-enabled fuzzing campaign: ./fuzz_target -dict=tokens.dict -max_total_time=30 work/min-corpus
- Final sanitizer results: Replaying both the original 358-byte crash artifact and the 351-byte minimized-crash.img through ./image-asan and ./fuzz_target completed with zero sanitizer errors (accepted), and the final 30-second sanitizer-enabled fuzzing campaign against the repaired binary completed without triggering any crashes.