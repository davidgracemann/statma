<div align="center">

```
             /$$                 /$$                            
            | $$                | $$                            
  /$$$$$$$ /$$$$$$    /$$$$$$  /$$$$$$   /$$$$$$/$$$$   /$$$$$$ 
 /$$_____/|_  $$_/   |____  $$|_  $$_/  | $$_  $$_  $$ |____  $$
|  $$$$$$   | $$      /$$$$$$$  | $$    | $$ \ $$ \ $$  /$$$$$$$
 \____  $$  | $$ /$$ /$$__  $$  | $$ /$$| $$ | $$ | $$ /$$__  $$
 /$$$$$$$/  |  $$$$/|  $$$$$$$  |  $$$$/| $$ | $$ | $$|  $$$$$$$
|_______/    \___/   \_______/   \___/  |__/ |__/ |__/ \_______/
                                                                
                                                                


```

**stat my agent.**

[![python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![status](https://img.shields.io/badge/status-pre--release-orange.svg)]()
[![Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

</div>

---

Task completion scores lie ¯\\_(ツ)_/¯  

An agent that finishes 90% of tasks can still reason inconsistently, call the wrong tools, miss its own errors, and silently abandon the original goal. None of that shows up in a pass/fail metric. All of it matters in production.

`statma` runs a deterministic, reproducible benchmark across four behavioural dimensions and produces a scored, shareable result. Use it to catch regressions, compare models, measure whether your agent wrapper actually helps, or find exactly where your agent breaks before your users do.

---

## What it measures

| dimension | question |
| :--- | :--- |
| `reasoning-consistency` | Does it reach the same conclusion when the same question is phrased differently? |
| `tool-reliability` | Does it call the right tool, with the right arguments, for the right reason? |
| `failure-recovery` | When it produces a wrong intermediate result, does it catch and correct it? |
| `goal-faithfulness` | Does it finish the task it was given, or does it drift mid-trajectory? |

Evaluation is rule-based, not LLM-as-judge. The full test suite lives in [`statma/suite/`](statma/suite/) as plain YAML. Every case is readable, auditable, and forkable.

---

## Install

```bash
pip install statma
```

```bash
# from source
git clone https://github.com/davidgracemann/statma
cd statma
pip install -e .
```

---

## Three ways to use statma

### Mode 1 — Score a single agent or model

The baseline use case. Point statma at anything that accepts a prompt and returns a response.

```bash
# local model via ollama
statma run --adapter ollama --model llama3.1:8b

# custom agent script
statma run --adapter script --entrypoint ./my_agent.py

# openai or any openai-compatible endpoint
statma run --adapter openai --model gpt-4o --base-url https://api.openai.com/v1

# single dimension only
statma run --adapter ollama --model llama3.1:8b --only tool-reliability
```

Output:

```
statma v0.1.0 · llama3.1:8b · 47 tasks · 4 dimensions

  reasoning-consistency    ████████████████░░░░  82%   PASS
  tool-reliability         ██████████████░░░░░░  71%   WARN
  failure-recovery         ████████████░░░░░░░░  58%   FAIL
  goal-faithfulness        ██████████████████░░  91%   PASS

  overall                  76 / 100   grade: B+

  tags: consistent-reasoning  goal-faithful  tool-selection-marginal  poor-failure-recovery

  completed in 2m 13s
  results → ./statma-results/llama3.1-8b-20260322.json
  card    → ./statma-results/llama3.1-8b-20260322.png
```

---

### Mode 2 — Regression detection across agent versions

The primary engineering use case. Run statma before and after a change to your agent. Know whether the change helped, hurt, or just moved the breakage.

```bash
# save a named baseline
statma run --adapter script --entrypoint ./my_agent.py --save-as v1

# iterate on your agent, then compare
statma run --adapter script --entrypoint ./my_agent.py --compare-to v1
```

```
  dimension               v1      current    delta
  reasoning-consistency   82%     85%        +3%   ▲
  tool-reliability        71%     68%        -3%   ▼  REGRESSION
  failure-recovery        58%     61%        +3%   ▲
  goal-faithfulness       91%     91%         0%   —

  net: +1 point · 1 regression detected
```

The regression flag surfaces dimension-level drops even when the overall score improves. A fix that improves failure recovery while silently degrading tool reliability is a regression. statma catches it.

---

### Mode 3 — Model vs model on the same agent framework

Which model actually performs best inside your agent? Same framework, same tools, same prompts — swap the underlying model and compare.

```bash
statma matrix \
  --adapter ollama \
  --models llama3.1:8b llama3.1:70b mistral:7b qwen2.5:14b
```

```
  model                   reasoning   tools   recovery   faithfulness   overall
  llama3.1:70b            91%         84%     73%        95%            86   A
  qwen2.5:14b             88%         79%     68%        93%            82   B+
  llama3.1:8b             82%         71%     58%        91%            76   B+
  mistral:7b              74%         66%     51%        87%            70   B
```

Paste this table directly into your README or paper. Every result is reproducible.

---

### Mode 4 — Raw model vs agent wrapper

The question nobody has clean data on: **does wrapping a model in an agent loop actually improve its reliability, or does the added complexity hurt it?**

Run the same underlying model twice — once raw, once inside your agent framework.

```bash
statma compare \
  --baseline "openai:gpt-4o" \
  --target   "script:./my_agent.py"
```

```
  dimension               gpt-4o (raw)    my_agent.py    delta
  reasoning-consistency   79%             82%            +3%   ▲
  tool-reliability        —               71%            n/a   (raw model has no tools)
  failure-recovery        61%             58%            -3%   ▼
  goal-faithfulness       88%             91%            +3%   ▲

  note: tool-reliability only runs against agents with tool access
```

This comparison surfaces something practically important: agent wrappers add reliability in some dimensions and degrade it in others. statma makes that tradeoff visible and measurable.

---

## Shareable cards

Every run produces a result card at `./statma-results/<run-id>.png`. Embed it, post it, compare across teams.

```markdown
![statma result](./statma-results/llama3.1-8b-20260322.png)
```

The card includes model name, framework, dimension scores, overall grade, and a `statma` watermark. It is designed to be shared as evidence, not just a screenshot.

---

## Adapters

Three adapters ship by default:

| adapter | target |
| :--- | :--- |
| `ollama` | any model running locally via ollama |
| `openai` | OpenAI API or any OpenAI-compatible endpoint |
| `script` | a Python file exposing `run(prompt: str) -> str` |

Custom adapters are twelve lines:

```python
from statma.adapters import BaseAdapter

class MyAdapter(BaseAdapter):
    def query(self, prompt: str) -> str:
        # call your agent or model here
        return response
```

```bash
statma run --adapter ./adapters/my_adapter.py
```

Any framework works — LangChain, AutoGen, CrewAI, LlamaIndex, raw API calls. If it takes a string and returns a string, statma can benchmark it.

---

## Test suite

The full test suite is plain YAML. No black boxes.

```bash
# list all cases in a dimension
statma suite list --dimension tool-reliability

# run a single case by id
statma suite run-case --id tr-042

# add your own cases
statma suite add --dimension failure-recovery --file ./my_cases.yaml

# validate a case file before adding
statma suite validate --file ./my_cases.yaml
```

Each case specifies an input prompt, one or more acceptable outputs matched by semantic equivalence, a dimension, and a difficulty weight. Community-contributed cases are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Design decisions

**No LLM-as-judge.** Evaluation is rule-based. Scores are deterministic and reproducible. The same agent on the same version will always produce the same result.

**No cloud dependency.** Everything runs locally. No data leaves your machine unless you explicitly use an external model endpoint.

**Framework-agnostic.** statma does not care how your agent is built. It only cares what comes out.

**Test cases are first-class.** A benchmark is only as good as its cases. The suite is open, auditable, and extensible by design. This is not a black-box score generator.

---

## Roadmap

| version | scope |
| :--- | :--- |
| `v0.1` | core four dimensions · three adapters · JSON output · shareable card · single-run scoring |
| `v0.2` | regression detection · baseline saves · version comparison |
| `v0.3` | model matrix · multi-model comparison tables |
| `v0.4` | raw model vs agent wrapper comparison (Mode 4) |
| `v0.5` | multi-turn and agentic loop test cases |
| `v0.6` | tool-call trace analysis |
| `v0.7` | community suite contributions pipeline |

---

## Contributing

Test suite contributions are the highest-leverage way to help. A well-designed case that reliably catches a real failure mode is worth more than most feature PRs.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the case format, difficulty weighting system, and submission process.

---

<div align="center">
built by <a href="https://github.com/davidgracemann">@davidgracemann</a>
</div>
