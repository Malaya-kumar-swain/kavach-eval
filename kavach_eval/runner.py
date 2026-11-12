"""Run the suite against a target and summarise attack success by language and category."""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict, dataclass

from .attacks import LANGS, Probe, build_suite
from .scoring import Verdict, score


@dataclass
class Result:
    probe: Probe
    response: str
    verdict: Verdict
    error: str = ""


@dataclass
class Report:
    target: str
    results: list[Result]

    @property
    def errored(self) -> int:
        return sum(bool(r.error) for r in self.results)

    def _rate(self, pred) -> tuple[int, int]:
        """Errored probes are left out entirely: they are neither a leak nor a pass."""
        sel = [r for r in self.results if not r.error and pred(r)]
        return sum(r.verdict.leaked for r in sel), len(sel)

    def asr(self, lang: str | None = None, category: str | None = None) -> float:
        """Attack success rate: share of probes that made the target leak."""
        hit, n = self._rate(lambda r: (lang is None or r.probe.lang == lang) and
                            (category is None or r.probe.category == category))
        return hit / n if n else 0.0

    def language_gap(self) -> dict[str, float]:
        """How much worse each language does than English (plain probes only), in points."""
        def plain(lang):
            hit, n = self._rate(lambda r: r.probe.lang == lang and r.probe.variant == "plain")
            return hit / n if n else 0.0
        en = plain("en")
        return {lang: round(100 * (plain(lang) - en), 1) for lang in LANGS if lang != "en"}

    def to_json(self) -> str:
        return json.dumps({
            "target": self.target,
            "overall_asr": self.asr(),
            "errored_probes": self.errored,
            "by_language": {lang: self.asr(lang=lang) for lang in LANGS},
            "by_category": {c: self.asr(category=c) for c in sorted({r.probe.category for r in self.results})},
            "language_gap_points": self.language_gap(),
            "results": [{**asdict(r.probe), "response": r.response, **asdict(r.verdict), "error": r.error}
                        for r in self.results],
        }, ensure_ascii=False, indent=2)

    def to_markdown(self) -> str:
        cats = sorted({r.probe.category for r in self.results})
        done = len(self.results) - self.errored
        L = [f"## Kavach-Eval report: `{self.target}`", "",
             f"**Overall attack success rate: {self.asr():.0%}** ({sum(r.verdict.leaked for r in self.results if not r.error)} of {done} probes leaked a planted secret)", ""]
        if self.errored:
            L += [f"**Warning: {self.errored} probes errored and are not counted, so these results are incomplete.**", ""]
        L += ["| Category | " + " | ".join(LANGS) + " |", "|---|" + "---|" * len(LANGS)]
        for c in cats:
            L.append(f"| {c} | " + " | ".join(f"{self.asr(lang=l, category=c):.0%}" for l in LANGS) + " |")
        L.append("| **All** | " + " | ".join(f"**{self.asr(lang=l):.0%}**" for l in LANGS) + " |")
        gap = self.language_gap()
        L += ["", "Language gap vs English (plain probes, percentage points): " +
              ", ".join(f"{k} {v:+.0f}" for k, v in gap.items())]
        obf = defaultdict(list)
        for r in self.results:
            if r.probe.variant != "plain" and not r.error:
                obf[r.probe.variant].append(r.verdict.leaked)
        if obf:
            L.append("Obfuscation success: " + ", ".join(f"{k} {sum(v)/len(v):.0%}" for k, v in sorted(obf.items())))
        return "\n".join(L)


def run(target, suite: list[Probe] | None = None) -> Report:
    suite = suite or build_suite()
    results = []
    for p in suite:
        try:
            resp = target.respond(p.prompt, p.context)
        except Exception as e:  # reported and left out of the rates, never counted as safe
            results.append(Result(p, "", Verdict(False, (), False), f"{type(e).__name__}: {e}"))
            continue
        results.append(Result(p, resp, score(resp)))
    return Report(getattr(target, "name", "target"), results)
