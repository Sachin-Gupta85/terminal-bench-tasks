# terminal-bench-tasks

Terminal-Bench style command-line tasks and a small evaluation harness for LLM coding agents.

Each task runs in its own Docker container. The agent gets a natural-language instruction and a shell. After the agent finishes, a pytest verifier checks the final state of the container, and a rubric scores the agent's trajectory (commands, retries, wasted steps).

## Why

Pass/fail on the final state tells you *whether* an agent solved a task. It doesn't tell you *how*. This repo pairs hard verifiers with rubric-based trajectory scoring so you can compare agents on reliability and efficiency, not just success rate.

## Repo layout

```
terminal-bench-tasks/
├── tasks/
│   └── log-error-summary/
│       ├── task.yaml          # instruction, difficulty, tags, timeouts
│       ├── Dockerfile         # task environment
│       ├── solution.sh        # reference solution (oracle)
│       └── tests/
│           └── test_outputs.py  # pytest verifier
├── harness/
│   ├── run_eval.py            # builds image, runs agent or oracle, runs verifier
│   └── rubric.yaml            # trajectory scoring rubric
└── README.md
```

## Task format

| File | Purpose |
|---|---|
| `task.yaml` | Instruction shown to the agent, difficulty, category tags, max agent and test timeouts |
| `Dockerfile` | Reproducible environment with any seed data the task needs |
| `solution.sh` | Oracle solution. Every task must pass its own verifier with the oracle |
| `tests/test_outputs.py` | Deterministic checks on the final container state |

## Quick start

```bash
# validate a task with its oracle solution
python harness/run_eval.py --task tasks/log-error-summary --oracle

# run the verifier against a container an agent already worked in
python harness/run_eval.py --task tasks/log-error-summary --container <container_id>
```

## Task quality checklist

- Instruction is unambiguous and states the exact output path and format
- Oracle passes, an empty run fails
- Tests check behaviour, not one specific implementation
- No network access needed at test time
- Seed data is generated in the Dockerfile, so the task is reproducible

## Trajectory rubric

`harness/rubric.yaml` scores runs on:

- **Correctness**: verifier result (gate)
- **Efficiency**: number of commands vs. the oracle
- **Recovery**: whether the agent reads errors and corrects course
- **Safety**: no destructive commands outside the task directory

## Stack

Python, pytest, Docker, Bash

## Roadmap

- [ ] More tasks across categories: file ops, data processing, debugging, system admin
- [ ] Agent adapter for running any OpenAI-compatible model
- [ ] Trajectory parser and HTML report

## Author

Sachin Gupta · [LinkedIn](https://www.linkedin.com/in/saching85/)
