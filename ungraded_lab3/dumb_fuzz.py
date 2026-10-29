#!/usr/bin/env python3
"""Small mutation-based baseline with no coverage feedback."""

import argparse
import pathlib
import random
import subprocess
import sys


ALPHABET = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789=;_-"


def mutate(source, rng, max_len=128):
    data = bytearray(source)
    operation = rng.choice(("replace", "insert", "delete", "flip"))

    if operation == "replace" and data:
        data[rng.randrange(len(data))] = rng.choice(ALPHABET)
    elif operation == "insert" and len(data) < max_len:
        position = rng.randrange(len(data) + 1)
        count = rng.randint(1, min(4, max_len - len(data)))
        data[position:position] = bytes(rng.choice(ALPHABET) for _ in range(count))
    elif operation == "delete" and data:
        position = rng.randrange(len(data))
        del data[position:position + rng.randint(1, min(4, len(data) - position))]
    elif operation == "flip" and data:
        position = rng.randrange(len(data))
        data[position] ^= 1 << rng.randrange(8)

    return bytes(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=250)
    parser.add_argument("--rng-seed", type=int, default=165)
    parser.add_argument("--input", default="seeds/basic.pkt")
    parser.add_argument("--target", default="./packet-asan")
    parser.add_argument("--save", default="work/dumb-crash.pkt")
    args = parser.parse_args()

    seed = pathlib.Path(args.input).read_bytes()
    rng = random.Random(args.rng_seed)
    save_path = pathlib.Path(args.save)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    for run in range(1, args.runs + 1):
        candidate = seed
        for _ in range(rng.randint(1, 6)):
            candidate = mutate(candidate, rng)

        try:
            result = subprocess.run(
                [args.target],
                input=candidate,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=1,
                check=False,
            )
        except subprocess.TimeoutExpired:
            save_path.write_bytes(candidate)
            print(f"hang found at run {run}; saved to {save_path}")
            return 0

        if result.returncode != 0:
            save_path.write_bytes(candidate)
            print(f"crash found at run {run}; saved to {save_path}")
            return 0

        if run % 50 == 0:
            print(f"completed {run} executions; no failure found")

    print(f"completed {args.runs} executions; no failure found")
    print("This fuzzer mutates inputs, but it cannot tell which inputs reach new code.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
