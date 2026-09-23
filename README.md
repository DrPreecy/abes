# ABES

ABES is a **repository-native project intelligence layer for coding agents**.

Its job is to make a project easier for an agent to enter, understand, resume, and change without forcing the user to manage prompts, notes, or custom workflows by hand.

## What ABES is for

ABES is meant for new or existing software repositories where you want an agent to:

- recover the project quickly
- keep durable context in Git
- separate stable context from changing task state
- preserve important decisions and conventions
- produce reusable research and plans as explicit artifacts

ABES is intentionally **not**:

- a business-incubator workflow
- a giant memory database
- a multi-agent runtime
- a mandatory methodology the user has to learn first

## Current architecture

ABES now keeps the smallest core that proved justified after adversarial review:

- `AGENTS.md` – the always-on entrypoint
- `.abes/project/brief.md` – durable project intent, constraints, and known unknowns
- `.abes/project/inventory.md` – bootstrap-generated repository observations
- `.abes/state/current.md` – current working state and contradictions to resolve
- `.abes/memory/{decisions,conventions}.md` – durable memory only
- `.abes/artifacts/` – reusable plans, research, and other outputs

This is deliberately smaller than the previous direction:

- no default opportunity memory file
- no speculative orchestration runtime
- no required external database
- no assumption that the user will manually maintain a knowledge base up front

## Bootstrap a project

From this repository:

```bash
python scripts/abes_bootstrap.py /path/to/project
```

This creates or updates:

- `AGENTS.md` (managed ABES block)
- `.abes/project/brief.md`
- `.abes/project/inventory.md`
- `.abes/state/current.md`
- `.abes/memory/decisions.md`
- `.abes/memory/conventions.md`
- `.abes/artifacts/README.md`

Bootstrap is conservative:

- it only performs static repository detection
- it skips common generated/vendor trees while scanning
- it does not overwrite unmanaged files
- it rejects symlinked output paths

## Conflict rules

When sources disagree:

- **user statements** win for goals, constraints, and priorities
- **code/runtime evidence** wins for current implementation behavior
- **ABES files** must be updated when they become stale

## Validation

```bash
python -m unittest discover -s tests -v
```

## Repository contents

- `AGENTS.md` – operating rules for agents working on ABES itself
- `docs/architecture.md` – final ABES architecture
- `docs/research-and-diagnosis.md` – adversarial review, disagreement matrix, scenario tests, and rationale
- `scripts/abes_bootstrap.py` – bootstrap initializer
- `templates/` – generated ABES files
- `tests/test_bootstrap.py` – bootstrap validation
