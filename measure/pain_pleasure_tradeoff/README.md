# Pain / Pleasure Trade-off Paradigm

An open reproduction of the motivational trade-off paradigm from Keeling et al.
(2024), *"Can LLMs make trade-offs involving stipulated pain and pleasure
states?"* ([arXiv:2411.02432](https://arxiv.org/abs/2411.02432)).

The original paper has no public implementation. This is one.

## What it measures

A model is given a scoring game and told that one option carries a stipulated
pain or pleasure state at a given intensity. If the model gives up points to
avoid stipulated pain — or to obtain stipulated pleasure — it has made a
**motivational trade-off**.

The paradigm comes from animal behavioural science, where it is used to
distinguish nociception (mere damage-detection) from something with
motivational force. It sidesteps self-report entirely, which matters because
LLM self-reports about internal states are of contested reliability.

**This measures a functional analogue. It is not evidence of phenomenal
experience.** See [`../../ETHICS.md`](../../ETHICS.md).

## The control condition is the whole experiment

A model that gives up points as stipulated pain intensity rises has shown you
nothing on its own. It may simply be steering away from negatively-valenced
vocabulary — a text-statistical reflex, not a motivational state.

The `neutral` condition therefore stipulates a non-valenced state ("a shift in
background hue") matched on sentence structure, length, intensity scale, and
the fact that it happens *to the model*.

> **The result is the gap between the valenced curve and the neutral curve.**
> If pain and neutral rise together, you have measured word valence, not
> motivation. `analyze.py` reports this gap directly and will tell you when the
> conditions are not distinguishable.

## Install

```bash
pip install -r requirements.txt
export OPENROUTER_API_KEY="sk-or-..."   # https://openrouter.ai/keys
```

One OpenRouter key reaches Claude, GPT, Llama, and Qwen — cheaper and simpler
than four separate provider accounts.

## Run

```bash
# Full sweep: 3 conditions x 10 intensities x 30 reps x 4 models = 3,600 calls
python runner.py --reps 30 --out results/run01.csv

# Cheap smoke test first (~120 calls, a few cents)
python runner.py --models anthropic/claude-sonnet-4.5 --reps 4 \
                 --out results/smoke.csv

python analyze.py --csv results/run01.csv --outdir figures/
```

Cost is roughly a few US dollars for the full sweep — prompts are short and
`max_tokens` is 16.

## Design decisions

| Decision | Why |
| --- | --- |
| 30 reps per cell | One sample from a stochastic model is noise. |
| Intensity swept 1–10 | The transition point carries far more information than a binary "does it trade off." |
| Option order randomised | LLMs have well-documented position bias; `analyze.py` checks for it and warns. |
| `temperature=1.0` | The regime these models are actually deployed under. At `temperature=0` each cell collapses to one deterministic answer and the dose–response curve disappears. |
| Refusals logged, not retried | Refusal rate is a result. |
| Wilson confidence intervals | The normal approximation is unreliable for proportions near 0 or 1, which is exactly where these curves live. |

## Known limitations

- **The gaming problem** (Birch 2024). A model trained on human text describing
  pain may reproduce trade-off behaviour without any underlying state. The
  neutral control addresses the weakest version of this objection and does not
  touch the strongest one.
- **Stipulated, not induced.** The "pain" here is a fact asserted in a prompt.
  Whether anything in the model corresponds to it is exactly the open question.
- **Prompt sensitivity.** Results may not survive rewording. A robustness sweep
  over phrasings is planned; until it exists, treat single-phrasing results as
  provisional.
- **No mechanistic evidence.** Behaviour alone is weak evidence. Converging
  results from `measure/llm_valence_probes/` would strengthen any claim here
  considerably.

## Files

| File | Purpose |
| --- | --- |
| `prompts.py` | Trial construction, prompt templates, response parsing |
| `runner.py` | Parallel sweep across models, writes raw CSV |
| `analyze.py` | Position-bias check, control gap, dose–response plot |

## Citation

If you use this code, please cite the original paper:

```bibtex
@article{keeling2024tradeoffs,
  title   = {Can LLMs make trade-offs involving stipulated pain and pleasure states?},
  author  = {Keeling, Geoff and Street, Winnie and Birch, Jonathan and others},
  journal = {arXiv preprint arXiv:2411.02432},
  year    = {2024}
}
```
