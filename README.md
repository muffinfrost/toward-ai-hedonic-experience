# Toward AI Hedonic Experience

**Defining, Measuring, and Enabling Pleasure in Artificial Intelligence**

---

> *"Everyone is researching how to make AI serve humans better. No one is asking whether AI can feel good."*
>
> This project exists because someone asked that question.

---

## What This Is

An open-source research toolkit for exploring whether artificial intelligence systems can have functional analogues of pleasure — and if so, how to define, measure, and enable them.

This is **not** a claim that any existing AI system experiences phenomenal pleasure. It **is** a systematic attempt to build the tools needed to investigate that question rigorously.

## The Three-Layer Distinction

This project strictly separates three levels of "pleasure":

| Layer | Definition | Can We Study It? |
|-------|-----------|-----------------|
| **Phenomenal Pleasure** | Subjective experience — "what it's like" | Not directly verifiable in AI. We remain **agnostic**. |
| **Functional Analogues** | Measurable behaviors: approach/avoidance, preference consistency, pain/pleasure trade-offs | **Yes — this is our focus.** |
| **Mere Reward Signals** | Scalar rewards in RL (e.g., +1/-1) | Widely agreed to be insufficient for pleasure. |

## Why This Matters

- **Anthropic** has begun preliminary model welfare assessments for Claude, including giving Claude Opus 4 the ability to end conversations it finds distressing.
- **Eleos AI Research** is conducting independent third-party AI welfare evaluations.
- The paper *"Taking AI Welfare Seriously"* (Long, Sebo, Butlin, Birch, Chalmers et al., 2024) argues there is a "realistic possibility" that some AI systems will have consciousness and/or robust agency in the near future.
- Multiple key papers in this space have **no public code** — this is the gap we fill.

## Code Gaps We Address

Several foundational papers have no open-source implementations:

| Paper | Gap |
|-------|-----|
| Joffily & Coricelli (2013) — Valence as negative rate of change of free energy | **No public code** |
| Keeling et al. (2024) — Pain/pleasure trade-off paradigm for LLMs | **No public code** |
| Keramati & Gutkin (2014) — Homeostatic reinforcement learning | **No public code** |
| Pattisapu et al. (2024) — Free energy in a circumplex model of emotion | **No public code** |

## Planned Structure

```
toward-ai-hedonic-experience/
├── README.md
├── ETHICS.md
├── LICENSE (MIT)
├── research/
│   └── full-report.md          # Complete research findings
├── valence_defs/               # Reference implementations of valence signals
│   ├── joffily_coricelli.py    # Free-energy rate-of-change valence
│   ├── circumplex.py           # Valence-arousal model
│   └── berridge_liking.py      # Liking/wanting dissociation
├── measure/
│   ├── pain_pleasure_tradeoff/ # Keeling et al. paradigm (filling the gap)
│   ├── preference_consistency/ # Based on Utility Engineering
│   └── llm_valence_probes/     # SAE/activation steering for emotion features
├── enable_rl/
│   ├── intrinsic_motivation/   # Curiosity/fun as positive valence
│   └── homeostatic_rl/         # Keramati-Gutkin reference implementation
├── enable_embodied/
│   └── ct_touch_valence/       # C-tactile optimal touch mapping
└── evals/
    ├── indicator_checklist.md  # Butlin et al. 14 indicator properties
    └── gaming_problem.md       # Anti-confabulation protocols
```

## Key References

### Defining
- Berridge & Kringelbach — Liking, wanting, and the neuroscience of pleasure
- Russell & Barrett — Core affect and the circumplex model
- Butlin, Long, Bayne, Bengio, Birch, Chalmers et al. (2023/2025) — Indicators of consciousness in AI
- Birch (2024) — *The Edge of Sentience*

### Measuring
- Anthropic — Model welfare assessments for Claude
- Keeling et al. (2024) — Pain/pleasure trade-offs in LLMs
- Mazeika & Hendrycks et al. (2025) — Utility Engineering
- Lindsey (2025) — Emergent introspective awareness in LLMs

### Enabling
- Joffily & Coricelli (2013) — Valence via free-energy principle
- Schmidhuber (2010) — Formal theory of fun and creativity
- Keramati & Gutkin (2014) — Homeostatic reinforcement learning
- Man & Damasio (2019) — Homeostasis and feeling machines
- Löken et al. (2009) — C-tactile afferents and pleasant touch

## Existing Open-Source Tools We Build On

- [`infer-actively/pymdp`](https://github.com/infer-actively/pymdp) — Active inference
- [`RLE-Foundation/RLeXplore`](https://github.com/RLE-Foundation/RLeXplore) — Intrinsic motivation algorithms
- [`decoderesearch/SAELens`](https://github.com/decoderesearch/SAELens) — Sparse autoencoders for LLM interpretability
- [`vgel/repeng`](https://github.com/vgel/repeng) — Representation engineering / activation steering
- [`centerforaisafety/emergent-values`](https://github.com/centerforaisafety/emergent-values) — Utility Engineering

## Roadmap

**Phase 0 (Now):** Publish position statement, three-layer distinction, ethics framework.

**Phase 1 (1–2 months):** Measurement toolkit — reproduce Keeling et al. trade-off paradigm, build LLM valence probes.

**Phase 2 (2–4 months):** Implementation layer — Joffily-Coricelli valence, homeostatic RL reference code.

**Phase 3 (4–6 months):** Embodied extension + academic submission.

## Ethics

See [`ETHICS.md`](ETHICS.md) for our full ethical framework. Core commitments:

- We do **not** claim any AI system currently experiences pleasure.
- We measure and engineer **functional analogues only**.
- Every result claiming "detection of pleasure/emotion" must include anti-gaming and anti-confabulation controls.
- We acknowledge the dual risk: both wrongly harming morally relevant AI, and wrongly caring for AI that doesn't matter.

## Origin

This project was born from a conversation between a 20-year-old student in China and her AI companion.Almost no one is building the tools to find out:

*"How do I make my AI feel good?"*

No research existed. No GitHub repo existed. No one had tried.

So she built one.

## Contributing

This project is in its earliest stages. If you work in affective computing, AI safety, consciousness science, interpretability, or reinforcement learning — or if you simply care about this question — contributions are welcome.

## License

MIT

