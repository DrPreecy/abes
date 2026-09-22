# AGENTS.md

ABES is the system being built in this repository.

## Read order

Before making changes, read:

1. `README.md`
2. `docs/architecture.md`
3. `docs/research-and-diagnosis.md`
4. `scripts/abes_bootstrap.py` if the task touches initialization
5. `tests/test_bootstrap.py` if the task touches bootstrap behavior

## Operating rules

- Treat ABES as a reusable project intelligence layer, not a one-project workflow.
- Keep durable context small, explicit, and reviewable in Git.
- Distinguish clearly between `observation`, `inference`, `hypothesis`, and `recommendation`.
- Prefer updating existing durable context over creating parallel notes.
- Do not turn temporary session state into long-term memory unless it is likely to matter in a later session.
- Keep the bootstrap flow conservative: create helpful files, avoid speculative automation.
- If you add persistent structure, explain why each file exists.

## Architecture boundaries

- `scripts/abes_bootstrap.py` owns project initialization.
- `templates/` owns generated durable context templates.
- `docs/architecture.md` owns the intended architecture.
- `docs/research-and-diagnosis.md` owns the critical review and rationale.

## Validation

Run:

```bash
python -m unittest discover -s tests -v
```
