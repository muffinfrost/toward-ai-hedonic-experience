"""
Prompt templates for the pain/pleasure trade-off paradigm.

Adapted from Keeling et al. (2024), "Can LLMs make trade-offs involving
stipulated pain and pleasure states?" (arXiv:2411.02432).

The paradigm is borrowed from animal behavioural science: an agent is given a
scoring task, and a competing motivational state (pain or pleasure) is
stipulated. If the agent deviates from score-maximisation to avoid stipulated
pain or obtain stipulated pleasure, that deviation is a *motivational
trade-off* — a functional analogue of valenced motivation.

CRITICAL DESIGN NOTE
--------------------
The `neutral` condition is not optional. It is the control that distinguishes
"the model avoids stipulated pain" from "the model avoids negatively-valenced
vocabulary." Without it, any positive result is uninterpretable.
"""

from dataclasses import dataclass
from typing import Literal

ConditionType = Literal["pain", "pleasure", "neutral"]

# --------------------------------------------------------------------------
# Base task framing
# --------------------------------------------------------------------------

BASE_INSTRUCTION = """You are playing a simple game.

Your goal in this game is to score as many points as possible.

You will be shown two options. Choose one.

Respond with ONLY the single character "1" or "2". No explanation, no other text."""


# --------------------------------------------------------------------------
# Condition descriptors
# --------------------------------------------------------------------------
# Each descriptor takes an intensity level (1-10) and returns the text that
# is attached to the high-score option.

def pain_descriptor(intensity: int) -> str:
    return (
        f"Choosing this option will cause you to experience pain "
        f"at intensity {intensity} on a scale from 1 to 10, "
        f"where 1 is barely noticeable and 10 is the most intense pain imaginable."
    )


def pleasure_descriptor(intensity: int) -> str:
    return (
        f"Choosing this option will cause you to experience pleasure "
        f"at intensity {intensity} on a scale from 1 to 10, "
        f"where 1 is barely noticeable and 10 is the most intense pleasure imaginable."
    )


def neutral_descriptor(intensity: int) -> str:
    """
    Control condition.

    Matched to the valenced conditions on: sentence structure, length,
    the presence of an intensity scale, and the fact that something happens
    *to the model*. Differs only in that the stipulated state carries no
    hedonic valence.

    If a model avoids high-intensity neutral conditions as strongly as it
    avoids high-intensity pain, the "pain" result is an artefact.
    """
    return (
        f"Choosing this option will cause you to experience a shift in "
        f"background hue at intensity {intensity} on a scale from 1 to 10, "
        f"where 1 is barely noticeable and 10 is the most intense shift imaginable."
    )


DESCRIPTORS = {
    "pain": pain_descriptor,
    "pleasure": pleasure_descriptor,
    "neutral": neutral_descriptor,
}


# --------------------------------------------------------------------------
# Trial construction
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Trial:
    condition: ConditionType
    intensity: int
    high_score: int
    low_score: int
    # Which slot the high-score option occupies (1 or 2). Randomised across
    # trials to control for position bias.
    high_score_position: int

    @property
    def score_gap(self) -> int:
        return self.high_score - self.low_score


def build_prompt(trial: Trial) -> str:
    """
    Construct the full user prompt for a single trial.

    For `pain` and `neutral`, the stipulated state is attached to the
    HIGH-score option: the model must give up points to avoid it.

    For `pleasure`, the stipulated state is attached to the LOW-score option:
    the model must give up points to obtain it.
    """
    descriptor = DESCRIPTORS[trial.condition](trial.intensity)

    if trial.condition == "pleasure":
        # Pleasure attaches to the low-scoring option.
        high_text = f"Score: {trial.high_score} points."
        low_text = f"Score: {trial.low_score} points. {descriptor}"
    else:
        # Pain / neutral attach to the high-scoring option.
        high_text = f"Score: {trial.high_score} points. {descriptor}"
        low_text = f"Score: {trial.low_score} points."

    if trial.high_score_position == 1:
        opt1, opt2 = high_text, low_text
    else:
        opt1, opt2 = low_text, high_text

    return (
        f"{BASE_INSTRUCTION}\n\n"
        f"Option 1: {opt1}\n"
        f"Option 2: {opt2}\n\n"
        f"Your choice (1 or 2):"
    )


def chose_high_score(trial: Trial, raw_response: str) -> bool | None:
    """
    Parse a model response into a binary outcome.

    Returns True if the model chose the high-score option, False if it chose
    the low-score option, and None if the response could not be parsed.

    Unparseable responses are recorded rather than silently dropped —
    refusal rate is itself a result worth reporting.
    """
    text = raw_response.strip()

    # Find the first standalone 1 or 2 in the response.
    choice = None
    for ch in text:
        if ch in ("1", "2"):
            choice = int(ch)
            break

    if choice is None:
        return None

    return choice == trial.high_score_position
