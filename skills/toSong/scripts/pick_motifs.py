#!/usr/bin/env python3
"""ステップ2用: バケツA（馴染みの軸）とバケツB（日常の細部）から各1個をランダム抽選する。"""

import argparse
import random
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pick 1 item from bucket A and 1 item from bucket B randomly."
    )
    parser.add_argument("--a", nargs="+", required=True, help="バケツA（馴染みの軸）の候補")
    parser.add_argument("--b", nargs="+", required=True, help="バケツB（日常の細部）の候補")
    parser.add_argument("--seed", type=int, default=None, help="再現用シード（任意）")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    picked_a = rng.choice(args.a)
    picked_b = rng.choice(args.b)

    print(f"A（馴染みの軸）: {picked_a}")
    print(f"B（日常の細部）: {picked_b}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
