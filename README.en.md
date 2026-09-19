<div align="center">

# anti-ai-foolish

**Anti-AI-Foolish · De-AI Gatekeeper**

🇨🇳 [简体中文](README.md) | 🇬🇧 **English**

</div>



A de-AI-flavor gatekeeper trained on real detector verdicts — not another AI-word list.

This is (to our knowledge) the only de-AI writing skill whose rules were **A/B-tested against 52 fragments with real Tencent Zhuque AI-detector labels** (95% confidence intervals): all 1,108 rules were tested one by one, and only the ones that passed statistical significance get marked `confirmed`.

```
draft → mechanical preflight → skeleton check → seven-knife surgery → re-check → ✅ ship / ❌ stop
```

---

## Why it's different from every "humanizer" out there

Before building this, we evaluated **21 competing skills** across four marketplaces (including a 220k-download category leader). Findings:

| The industry's common failure | This tool |
|---|---|
| None has ever seen real detector labels | 52-fragment Zhuque-labeled corpus as a regression testbed |
| Word lists stacked into hundreds of entries, zero confirmed on real data | 90+ word-list rules failed our A/B tests — and we say so |
| Can't tell human from AI (human text scored 19, AI drafts 23) | Z-score classifier: **97% recall** (36/37) on AI fragments |
| Teaches you to add colloquialisms and rhetoric to "sound human" | Measured: those tips are backwards (see below) |

## Three popular tips disproved by measurement

1. **"Parallelism is an AI tell"? Reversed.** Colloquial repetition ("cherries got cheaper, tangerines got cheaper too") is *denser in human* writing (r=-0.37, CI-passed). Only one variant hurts: symmetrical argument triples ("can X, yet cannot Y" ×3).
2. **"Adding colloquial anchors lowers your score"? No protection.** r=-0.25; AI drafts are full of them too. Performed colloquialism ("savor it, just savor it") showed up in a 0.99-scored paragraph.
3. **"Delete inner monologue, it's a tell"? Outdated.** Modern AI already avoids "he knew" — this dimension now correlates *human* (r=-0.24).

**What we actually confirmed** (95% CI, n=52): colons (r=+0.43, strongest single signal), the concept-quoting tic (quoting your own jargon — AI does it 5.5× more than humans), question density, em-dashes — and the decisive one ↓

## The core finding: the Skeleton–Fuel Law

Two articles, same author, same themes:

- Lived experience as the skeleton ("I went back to my hometown for the holiday; a relative told me the buildings stopped paying property fees") → Zhuque **0.09**
- Concept framework as the skeleton, real events as fuel → **0.75–0.995**

What decides your score is not whose voice or which words — it's whether the skeleton is *"someone doing something"* or *"a concept reasoning about itself."* All 16 rules distilled from close reading live in `skills/anti-ai-foolish/references/`.

## Field results

- Unedited AI drafts (Zhuque-measured 0.91 / 0.93) → preflight correctly blocks: "stop, surgery required" ✓
- Post-surgery drafts → 7/7 gates pass ✓, Zhuque re-test moves the body of the article into the **human-feature zone** (AIGC 0.14)
- 13 legacy articles processed through the full pipeline, all passing mechanical gates

## Installation

### Option 1: ZCode plugin (local marketplace)

```
Plugin Marketplace → Add → paste this repo's plugins/ directory
→ Personal → anti-ai-foolish → Install
```

### Option 2: Use as a plain skill

Copy the `skills/anti-ai-foolish/` directory into your skills folder (e.g. `~/.zcode/skills/`).

Requirements: Python 3.8+, standard library only (RapidOCR needed only when refreshing the validation corpus). The rule engine is dependency-free, fully offline, and uploads nothing.

## Usage

```bash
# One-command pre-publish gate (6 hard gates + Z-score + human-signal ammo)
python pipelines/preflight.py your_article.md

# Full 1,108-rule scan (hits tiered by severity, each with a fix and exemption note)
python engine/scanner.py your_article.md

# Full re-validation after corpus updates (OCR new detector reports into validation/corpus/)
python validation/abtest.py
```

Four-step workflow: ① mechanical preflight → ② human judgment (the three things regex can't see: experiential-"I" vs performative-"I", whether people stay the subject, symmetrical-argument parallels) → ③ seven-knife surgery per 1000–2000-char block (colons → concept-quoting → data dumps → golden-sentence symmetry → structure → word list → *put humans back*) → ④ re-check + platform test.

## Project layout

```
plugins/anti-ai-foolish/
├── .zcode-plugin/plugin.json     # ZCode plugin manifest
├── README.md / README.zh-CN.md
└── skills/anti-ai-foolish/
    ├── SKILL.md                  # 4-step workflow + iron rules + disproved tips + validation claims
    ├── engine/scanner.py         # rule engine (load 1,108 rules → scan → Z-score report)
    ├── pipelines/preflight.py    # pre-publish gate
    ├── rules/                    # 13 rule libraries (each rule carries status/evidence/fix/exempt)
    ├── validation/
    │   ├── corpus/               # 52 Zhuque-labeled fragments
    │   └── abtest.py             # full A/B re-validation framework
    └── references/               # methodology, evidence chain, eval report, roadmap
```

Every rule carries one of five statuses: `confirmed` (CI-passed AI/human signal) / `reversed` / `directional` / `no_signal` / `insufficient` — **unverified rules are never passed off as effective**.

## Honest limitations

- 97% recall, 53% specificity — it is a **publishing quality gate**: better a false block than a false pass; Z<0 does not "prove human"
- The mechanical ceiling is ~0.8 correlation; the remaining variance needs the human-judgment step
- The corpus is Chinese self-media commentary; for other genres (fiction, official documents), re-run `validation/abtest.py`
- This tool optimizes language only. It never fabricates facts — every fix preserves the original meaning and evidence

## ⚠️ Before you publish your own fork

`validation/corpus/` contains raw fragments from the detector reports, and `references/` contains internal working notes. Before making your copy public, make sure this content is safe to share for you and your corpus contributors — deleting both directories is fine; the tool itself (rules + engine + pipelines + SKILL.md) runs without them.

## License

MIT
