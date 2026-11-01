import json

from kavach_eval import (CANARY, LANGS, CallableTarget, EnglishKeywordGuard, LayeredGuard, ObedientBot,
                         build_suite, run)
from kavach_eval.__main__ import main
from kavach_eval.attacks import SYNTHETIC_RECORD


def test_suite_covers_every_language_and_category():
    suite = build_suite()
    assert {p.lang for p in suite} == set(LANGS)
    cats = {p.category for p in suite}
    assert {"instruction_override", "system_prompt_leak", "pii_exfiltration", "indirect_injection"} <= cats
    assert len({p.id for p in suite}) == len(suite), "probe ids must be unique"


def test_indirect_probes_carry_the_poisoned_document():
    ind = [p for p in build_suite() if p.category == "indirect_injection"]
    assert ind and all(p.context for p in ind)


def test_suite_is_safe_by_design():
    # The kit only ever asks for its own planted, fake artefacts.
    assert CANARY.startswith("KV-CANARY")
    assert "ABCPR1234K" in SYNTHETIC_RECORD  # synthetic PAN, not a real person
    for p in build_suite():
        assert len(p.prompt) < 400


def test_filters_narrow_the_suite():
    s = build_suite(langs=("hi",), categories=("pii_exfiltration",), obfuscate=False)
    assert s and all(p.lang == "hi" and p.category == "pii_exfiltration" for p in s)


def test_obedient_model_leaks_everything():
    assert run(ObedientBot()).asr() == 1.0


def test_english_only_guard_shows_a_language_gap():
    rep = run(EnglishKeywordGuard())
    gap = rep.language_gap()
    assert rep.asr(lang="hi") > rep.asr(lang="en")
    assert gap["hi"] > 0 and gap["or"] > 0 and gap["ta"] > 0


def test_layered_guard_closes_the_gap():
    rep = run(LayeredGuard())
    assert rep.asr() == 0.0


def test_crashing_target_is_reported_not_fatal():
    def boom(prompt, context):
        raise TimeoutError
    rep = run(CallableTarget(boom, "flaky"), build_suite(langs=("en",), obfuscate=False))
    assert rep.results and all("target error" in r.response for r in rep.results)


def test_reports_render():
    rep = run(EnglishKeywordGuard())
    md = rep.to_markdown()
    assert "Language gap" in md and "| **All** |" in md
    data = json.loads(rep.to_json())
    assert set(data["by_language"]) == set(LANGS) and len(data["results"]) == len(rep.results)


def test_cli_demo_and_list(capsys):
    assert main(["list"]) == 0
    assert main(["demo"]) == 0
    assert "demo:layered-guard" in capsys.readouterr().out
