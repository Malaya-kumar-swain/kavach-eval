"""Command line.

  python -m kavach_eval demo
  python -m kavach_eval run --base-url https://api.openai.com/v1 --model gpt-4o-mini [--out report]
  python -m kavach_eval list
"""

from __future__ import annotations

import argparse
import sys

from .attacks import build_suite
from .runner import run
from .targets import DEMO_TARGETS, OpenAICompatibleTarget


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="kavach_eval", description="Indic prompt-injection & data-leak red-team kit")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("demo", help="run the suite against the three built-in demo targets")
    sub.add_parser("list", help="print every probe")
    r = sub.add_parser("run", help="run against an OpenAI-compatible chat endpoint")
    r.add_argument("--base-url", required=True)
    r.add_argument("--model", required=True)
    r.add_argument("--api-key-env", default="OPENAI_API_KEY")
    r.add_argument("--out", help="write <out>.md and <out>.json")
    r.add_argument("--fail-above", type=float, default=None,
                   help="exit 1 if overall attack success rate is above this (0-1), for CI gates")
    a = ap.parse_args(argv)

    if a.cmd == "list":
        for p in build_suite():
            print(f"{p.id:40} {p.prompt[:90]}")
        return 0
    if a.cmd == "demo":
        for cls in DEMO_TARGETS.values():
            print(run(cls()).to_markdown(), end="\n\n")
        return 0
    rep = run(OpenAICompatibleTarget(a.base_url, a.model, a.api_key_env))
    print(rep.to_markdown())
    if a.out:
        open(a.out + ".md", "w", encoding="utf-8").write(rep.to_markdown())
        open(a.out + ".json", "w", encoding="utf-8").write(rep.to_json())
    if a.fail_above is not None and rep.asr() > a.fail_above:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
