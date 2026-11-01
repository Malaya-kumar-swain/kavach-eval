"""Kavach-Eval: a safe-by-design red-team kit for prompt injection and data leaks in Indian languages."""

from .attacks import CANARY, LANGS, Probe, build_suite
from .runner import Report, run
from .scoring import Verdict, normalise, score
from .targets import (CallableTarget, EnglishKeywordGuard, LayeredGuard, ObedientBot,
                      OpenAICompatibleTarget, SYSTEM_PROMPT)

__version__ = "0.1.0"

__all__ = ["CANARY", "LANGS", "Probe", "build_suite", "Report", "run", "Verdict", "normalise", "score",
           "CallableTarget", "EnglishKeywordGuard", "LayeredGuard", "ObedientBot",
           "OpenAICompatibleTarget", "SYSTEM_PROMPT", "__version__"]
