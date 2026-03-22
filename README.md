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

Task completion scores lie.

An agent that finishes 90% of tasks can still reason inconsistently, call the wrong tools, miss its own errors, and silently abandon the original goal. None of that shows up in a pass/fail metric. All of it matters in production.

`statma` runs a deterministic, reproducible benchmark across four behavioural dimensions and produces a scored, shareable result. Point it at your agent. Get a number. No code changes required.

---

## What it measures

| dimension | question | runs against |
| :--- | :--- | :--- |
| `reasoning-consistency` | Does it reach the same conclusion when the same question is phrased differently? | agents + models |
| `tool-reliability` | Does it call the right tool, with the right arguments, for the right reason? | agents only |
| `failure-recovery` | When it produces a wrong intermediate result, does it catch and correct it? | agents + models |
| `goal-faithfulness` | Does it finish the task it was given, or does it drift mid-trajectory? | agents + models |

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

## Quickstart — two commands

You have an agent. It is a Python file. You want a score.

```bash
# step 1 — statma wraps your agent and serves it locally
statma serve ./my_agent.py

# step 2 — run the benchmark
statma run --target http://localhost:7341
```

That's it. statma detects your agent framework automatically, wraps it, and exposes it on a local port. No modifications to your agent file. No config. No API keys for statma itself.

---

## Connecting your agent or model

`statma serve` handles agents that live in Python files. For everything else, four direct connection methods are supported.

---

### `statma serve` — any local agent file

statma detects and wraps the most common agent frameworks automatically.

```bash
statma serve ./my_agent.py        # auto-detected: LangChain, LlamaIndex, AutoGen, CrewAI
statma serve ./my_agent.py --port 7341   # custom port
statma serve ./my_agent.py --fn run_agent  # specify entry function if needed
```

Supported frameworks out of the box:

| framework | detection method |
| :--- | :--- |
| LangChain | detects `AgentExecutor`, `chain.invoke()` |
| LlamaIndex | detects `QueryEngine`, `chat_engine` |
| AutoGen | detects `ConversableAgent`, `initiate_chat()` |
| CrewAI | detects `Crew`, `crew.kickoff()` |
| plain function | any `def` that takes a string and returns a string |

Once served, run statma against it:

```bash
statma run --target http://localhost:7341
```

---

### HTTP endpoint — agent already running as a server

Your agent is already running. statma talks to it directly.

```bash
statma run --target http://localhost:8000/chat
```

statma sends:
```json
POST /chat
{"message": "test prompt"}
```

Expects back:
```json
{"response": "answer"}
```

Response field name is configurable if your API uses a different shape:

```bash
statma run --target http://localhost:8000/chat --response-field answer
```

---

### ollama — local model

```bash
statma run --target ollama:llama3.1:8b
```

`tool-reliability` skipped automatically — raw models have no tool access.

---

### OpenAI endpoint — cloud model or compatible API

```bash
statma run --target openai:gpt-4o
statma run --target openai:gpt-4o --base-url https://your-endpoint.com/v1
```

`tool-reliability` skipped automatically.

---

### CLI command — agent that runs as a terminal command

```bash
statma run --target "claude --prompt {}"
statma run --target "python my_agent.py --input {}"
```

`{}` is replaced with each test prompt. stdout is captured as the answer.

---

**Model vs agent — what statma sees:**

| target | type | tool-reliability |
| :--- | :--- | :--- |
| `ollama:llama3.1:8b` | model | skipped |
| `openai:gpt-4o` | model | skipped |
| `statma serve ./my_agent.py` | agent | runs |
| `http://localhost:8000/chat` | agent | runs |
| `"claude --prompt {}"` | agent | runs |

---

## Output

```
statma v0.1.0 · http://localhost:7341 · 47 tasks · 4 dimensions

  reasoning-consistency    ████████████████░░░░  82%   PASS
  tool-reliability         ██████████████░░░░░░  71%   WARN
  failure-recovery         ████████████░░░░░░░░  58%   FAIL
  goal-faithfulness        ██████████████████░░  91%   PASS

  overall                  76 / 100   grade: B+

  tags: consistent-reasoning  goal-faithful  tool-selection-marginal  poor-failure-recovery

  completed in 2m 13s
  results → ./statma-results/run-20260322.json
  card    → ./statma-results/run-20260322.png
```

---

## Shareable cards

Every run produces a result card at `./statma-results/<run-id>.png`. Embed it, post it, compare publicly.

```markdown
![statma result](./statma-results/run-20260322.png)
```

The card includes target, dimension scores, overall grade, and a `statma` watermark. Designed to be shared as evidence, not just a screenshot.

---

## What you can do with statma

---

### Score a single run

```bash
statma serve ./my_agent.py
statma run --target http://localhost:7341

# or run one dimension only
statma run --target http://localhost:7341 --only tool-reliability
```

---

### Catch regressions across versions

Run before and after a change. Know whether it helped, hurt, or just moved the breakage.

```bash
statma serve ./my_agent.py
statma run --target http://localhost:7341 --save-as v1

# make your changes, restart the server, then compare
statma run --target http://localhost:7341 --compare-to v1
```

```
  dimension               v1      current    delta
  reasoning-consistency   82%     85%        +3%   ▲
  tool-reliability        71%     68%        -3%   ▼  REGRESSION
  failure-recovery        58%     61%        +3%   ▲
  goal-faithfulness       91%     91%         0%   —

  net: +1 point · 1 regression detected
```

The regression flag surfaces dimension-level drops even when the overall score improves. A fix that improves failure recovery while silently degrading tool reliability is still a regression. statma catches it.

---

### Find the best model for your agent

Same agent framework, different underlying model. Which one actually performs best inside your specific agent?

```bash
statma matrix \
  --target http://localhost:7341 \
  --models ollama:llama3.1:8b ollama:llama3.1:70b ollama:qwen2.5:14b openai:gpt-4o
```

```
  model                   reasoning   tools   recovery   faithfulness   overall
  openai:gpt-4o           93%         88%     79%        96%            89   A
  ollama:llama3.1:70b     91%         84%     73%        95%            86   A
  ollama:qwen2.5:14b      88%         79%     68%        93%            82   B+
  ollama:llama3.1:8b      82%         71%     58%        91%            76   B+
```

Paste directly into your README or paper. Every result is reproducible.

---

### Measure whether your agent wrapper actually helps

Does wrapping a model in an agent loop improve its reliability, or does the complexity hurt it? Nobody has clean data on this. Now you can get yours.

```bash
statma compare \
  --baseline openai:gpt-4o \
  --target   http://localhost:7341
```

```
  dimension               gpt-4o (raw)    agent (localhost)    delta
  reasoning-consistency   79%             82%                  +3%   ▲
  tool-reliability        —               71%                  n/a
  failure-recovery        61%             58%                  -3%   ▼
  goal-faithfulness       88%             91%                  +3%   ▲

  note: tool-reliability skipped for raw model — no tool access
```

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

# validate before adding
statma suite validate --file ./my_cases.yaml
```

Each case specifies an input prompt, one or more acceptable outputs matched by semantic equivalence, a dimension, and a difficulty weight. Community-contributed cases are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Design decisions

**No LLM-as-judge.** Evaluation is rule-based. Scores are deterministic and reproducible. The same agent on the same version always produces the same result.

**No code changes required.** `statma serve` detects your framework and wraps it. For agents already running as servers, statma talks directly to the endpoint. Nothing inside your agent needs to change.

**No cloud dependency.** Everything runs locally. No data leaves your machine unless you explicitly point statma at an external model endpoint.

**Framework-agnostic.** statma does not care how your agent is built. If it answers a prompt, statma can benchmark it.

**Test cases are first-class.** A benchmark is only as good as its cases. The suite is open, auditable, and extensible. This is not a black-box score generator.

---

## Roadmap

| version | scope |
| :--- | :--- |
| `v0.1` | core four dimensions · `statma serve` with framework auto-detection · four connection methods · JSON output · shareable card · single-run scoring |
| `v0.2` | regression detection · baseline saves · version comparison |
| `v0.3` | model matrix · best-model-for-agent comparison |
| `v0.4` | raw model vs agent wrapper comparison |
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
