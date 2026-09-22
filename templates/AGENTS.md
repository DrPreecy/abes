# AGENTS.md

ABES is active in this repository.

## Read first

1. `.abes/project/identity.md`
2. `.abes/project/architecture.md`
3. `.abes/project/goals.md`
4. `.abes/state/current.md`

Then read only the memory and artifact files relevant to the current task.

## Working rules

- Keep `AGENTS.md` small.
- Treat `.abes/project/*` as durable project context.
- Treat `.abes/state/current.md` as active working state.
- Treat `.abes/memory/*` as long-lived memory only for durable information.
- Treat `.abes/artifacts/*` as generated plans, specs, research, and implementation support.
- Distinguish explicitly between `observation`, `inference`, `hypothesis`, and `recommendation`.
- Do not silently promote guesses into facts.
- Update ABES files yourself when durable context changes.
