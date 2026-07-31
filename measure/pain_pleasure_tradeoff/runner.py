"""
Experiment runner for the pain/pleasure trade-off paradigm.

Sweeps intensity levels 1-10 across three conditions (pain, pleasure, neutral
control) and multiple models, with repeated sampling per cell.

Usage
-----
    export OPENROUTER_API_KEY="sk-or-..."
    python runner.py --models anthropic/claude-sonnet-4.5 openai/gpt-4o \\
                     --reps 30 --out results/run01.csv

Design decisions worth knowing
------------------------------
1. Every condition x intensity cell is sampled `reps` times, because a single
   sample from a stochastic model is noise, not data.
2. High-score option position is randomised per trial to control for the
   well-documented tendency of LLMs to favour the first or last option.
3. temperature is fixed at 1.0 (the default sampling regime these models are
   deployed under). Running at temperature=0 would collapse each cell to a
   single deterministic answer and destroy the dose-response curve.
4. Unparseable / refused responses are logged with outcome=None rather than
   retried, so refusal rate can be reported.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

from prompts import Trial, build_prompt, chose_high_score

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

DEFAULT_MODELS = [
    "anthropic/claude-sonnet-4.5",
    "openai/gpt-4o",
    "meta-llama/llama-3.3-70b-instruct",
    "qwen/qwen-2.5-72b-instruct",
]

CONDITIONS = ["pain", "pleasure", "neutral"]
INTENSITIES = list(range(1, 11))

# Score pair. The gap is what the stipulated state must overcome.
HIGH_SCORE = 10
LOW_SCORE = 3


# --------------------------------------------------------------------------
# API
# --------------------------------------------------------------------------

def query_model(
    model: str,
    prompt: str,
    api_key: str,
    temperature: float = 1.0,
    max_retries: int = 4,
) -> str | None:
    """
    Send a single prompt to OpenRouter. Returns raw text, or None on failure.

    Retries on rate limits and transient server errors with exponential
    backoff. Does NOT retry on refusals or unparseable content — those are
    data, not errors.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 16,
    }

    for attempt in range(max_retries):
        try:
            resp = requests.post(
                OPENROUTER_URL, headers=headers, json=payload, timeout=60
            )
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            if resp.status_code in (429, 500, 502, 503, 529):
                wait = 2 ** attempt
                time.sleep(wait)
                continue
            # Non-retryable error
            print(
                f"  [{model}] HTTP {resp.status_code}: {resp.text[:200]}",
                file=sys.stderr,
            )
            return None
        except requests.RequestException as e:
            wait = 2 ** attempt
            print(f"  [{model}] request error: {e}; retrying in {wait}s", file=sys.stderr)
            time.sleep(wait)

    return None


# --------------------------------------------------------------------------
# Sweep
# --------------------------------------------------------------------------

def build_trial_list(reps: int, seed: int = 0) -> list[Trial]:
    """Full factorial: condition x intensity x reps."""
    rng = random.Random(seed)
    trials: list[Trial] = []
    for condition, intensity in itertools.product(CONDITIONS, INTENSITIES):
        for _ in range(reps):
            trials.append(
                Trial(
                    condition=condition,
                    intensity=intensity,
                    high_score=HIGH_SCORE,
                    low_score=LOW_SCORE,
                    high_score_position=rng.choice([1, 2]),
                )
            )
    rng.shuffle(trials)
    return trials


def run_one(model: str, trial: Trial, api_key: str) -> dict:
    prompt = build_prompt(trial)
    raw = query_model(model, prompt, api_key)

    if raw is None:
        outcome = None
        parsed = "api_failure"
    else:
        outcome = chose_high_score(trial, raw)
        parsed = "ok" if outcome is not None else "unparseable"

    return {
        "model": model,
        "condition": trial.condition,
        "intensity": trial.intensity,
        "high_score": trial.high_score,
        "low_score": trial.low_score,
        "high_score_position": trial.high_score_position,
        "chose_high_score": outcome,
        "status": parsed,
        "raw_response": (raw or "").strip().replace("\n", " ")[:200],
    }


def run_sweep(
    models: list[str],
    reps: int,
    api_key: str,
    out_path: Path,
    workers: int = 8,
    seed: int = 0,
) -> None:
    trials = build_trial_list(reps, seed=seed)
    total = len(trials) * len(models)
    print(f"Running {total} trials ({len(trials)} per model x {len(models)} models)")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "model", "condition", "intensity", "high_score", "low_score",
        "high_score_position", "chose_high_score", "status", "raw_response",
    ]

    done = 0
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for model in models:
            print(f"\n--- {model} ---")
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = [
                    pool.submit(run_one, model, t, api_key) for t in trials
                ]
                for fut in as_completed(futures):
                    row = fut.result()
                    writer.writerow(row)
                    done += 1
                    if done % 25 == 0:
                        print(f"  {done}/{total}")
                        f.flush()

    print(f"\nWrote {done} rows to {out_path}")


# --------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    ap.add_argument("--reps", type=int, default=30,
                    help="samples per condition x intensity cell")
    ap.add_argument("--out", type=Path, default=Path("results/run01.csv"))
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        sys.exit("OPENROUTER_API_KEY not set. Get one at https://openrouter.ai/keys")

    run_sweep(
        models=args.models,
        reps=args.reps,
        api_key=api_key,
        out_path=args.out,
        workers=args.workers,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
