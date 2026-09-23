# AGENTS.md

ABES is active in this repository.

## Read first

1. `.abes/project/brief.md`
2. `.abes/project/inventory.md`
3. `.abes/state/current.md`

Then read only the memory and artifact files relevant to the current task.

## Working rules

- Keep `AGENTS.md` small.
- Treat `.abes/project/brief.md` as durable intent/context and `.abes/project/inventory.md` as bootstrap-generated repository observations that should be verified before relying on them.
- Treat `.abes/state/current.md` as active working state.
- Treat `.abes/memory/*` as long-lived memory only for durable decisions and conventions.
- Treat `.abes/artifacts/*` as generated plans, specs, research, and implementation support.
- Distinguish explicitly between `observation`, `inference`, `hypothesis`, and `recommendation`.
- Do not silently promote guesses into facts.
- If sources disagree: user statements win for goals and priorities, code/runtime evidence wins for current behavior, and stale ABES notes must be corrected.
- Keep autonomous suggestions evidence-backed and easy to ignore until the user cares.
- Update ABES files yourself when durable context changes.
