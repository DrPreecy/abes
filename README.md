# ABES

ABES should not be a one-off business-idea workflow.

ABES should be a **repository-native project intelligence layer for coding agents**: a small operating layer you can drop into a new or existing project so the agent can discover the project, maintain durable context, distinguish fact from inference, and keep work moving across sessions without forcing the user to manage prompt machinery.

## Why this repo changed

The original scaffold in this repository was a business-discovery pipeline hidden behind a zip archive. It was narrowly optimized for one founder workflow, assumed fixed phases, and did not actually solve the stated problem of reusable project understanding for arbitrary repositories.

That architecture has been replaced with a smaller and more general foundation:

- **chat-first interaction**
- **durable project context** stored in-repo
- **lightweight persistent memory** with explicit evidence and status
- **artifact folders for plans/specs/analysis**
- **bootstrap workflow** for bringing ABES into a new project
- **strict fact / inference / hypothesis / recommendation separation**

## What ABES is now

ABES is a **project-aware context operating layer** for coding agents.

It is intentionally not:

- a full autonomous software factory
- a giant vector-memory system
- a single massive instruction file
- a business incubator workflow
- a multi-agent framework for its own sake

Instead, it gives any agent a stable place to find:

1. **project identity**
2. **current goals and constraints**
3. **durable decisions and conventions**
4. **active working state**
5. **generated artifacts**
6. **candidate opportunities worth proposing**

## Repository contents

- `AGENTS.md` – operating rules for agents working on ABES itself
- `docs/architecture.md` – proposed ABES architecture
- `docs/research-and-diagnosis.md` – critical review, research findings, MVP, risks, and recommendation
- `scripts/abes_bootstrap.py` – bootstrap command to initialize ABES inside a project
- `templates/` – files copied into target repositories during bootstrap
- `tests/test_bootstrap.py` – focused validation for bootstrap behavior

## Bootstrap a project

From this repository:

```bash
python scripts/abes_bootstrap.py /path/to/project
```

This creates or updates:

- `AGENTS.md` (managed ABES block)
- `.abes/project/identity.md`
- `.abes/project/architecture.md`
- `.abes/project/goals.md`
- `.abes/state/current.md`
- `.abes/memory/decisions.md`
- `.abes/memory/conventions.md`
- `.abes/memory/opportunities.md`
- `.abes/artifacts/README.md`

## Validation

```bash
python -m unittest discover -s tests -v
```

## MVP stance

The MVP is deliberately small.

ABES v1 should:

- initialize itself inside a project
- leave behind durable, readable context files
- help future agents know what to read first
- support memory promotion only for durable information
- keep current-task state separate from long-lived memory

ABES v1 should **not** yet attempt:

- autonomous background idea generation loops
- database-backed memory infrastructure
- generalized multi-agent orchestration runtime
- heavy indexing or retrieval infrastructure
- complex path-scoped rule engines

Those may become useful later, but they are not required to make ABES valuable now.
