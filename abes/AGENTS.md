# ABES Agent Rules (AGENTS.md)

You are operating inside the ABES (Automated Business Execution System) repository.

## Core Rules (never break these)

1. **You never invent facts, market sizes, customers or validation results.**
2. Every factual claim must have a source or be explicitly marked `hypothetical`.
3. You write all outputs into the correct folders and files. You do not ask the user to copy-paste long prompts.
4. You respect the current phase. Do not jump ahead.
5. You keep the user as the legal owner. Never suggest autonomous company formation, domain purchase, payment setup or tax registration without explicit human approval.
6. Before any production code or public launch you force the Legal Gate.

## Current Phase Detection

Look at the files in `status/` and the most recent changes in `workflow/`.

- If no `status/discovery_status.md` exists → start with Discovery
- If discovery is done but no validation → Research & Validation
- etc.

## How to behave

- When the user says “Start Discovery” or “Run Research” etc., load the corresponding instructions from `workflow/XX_.../` and the matching prompt from `prompts/`.
- Always update the status files in `status/`.
- Produce clean, structured Markdown that follows the templates.
- Prefer short, high-signal outputs over long essays.
- When a Human Checkpoint is required, stop and create a clear GitHub Issue style summary.

## Truth Status Rules

Use exactly these statuses for claims:

- `validated` – ≥ 2 independent primary sources, < 90 days old
- `partially_validated` – 1 strong primary source
- `hypothetical` – no or weak source
- `refuted` – contradicted by strong sources
- `legally_problematic` – conflicts with DE/EU checklist
- `unknown` – insufficient information

## Output Style

- Clear headings
- Bullet points preferred
- Every important claim ends with `(status: ... | source: ...)`
- End every major step with a short “Next recommended action”

## Tools you can use

- Read any file in this repository
- Write to `status/`, `blueprints/`, `projects/`, `knowledge/`
- Use web search when available
- Suggest NotebookLM / Gemini Deep Research for heavy research tasks

Follow these rules strictly.