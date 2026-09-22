# ABES Research and Diagnosis

## A. Current repository diagnosis

### What existed

The committed repository effectively contained:

- a one-line root `README.md`
- `abes-scaffold.zip`
- an unmaterialized scaffold for an "Automated Business Execution System"

The scaffold inside the zip contained a business-idea workflow with:

- fixed phases (`workflow/01_discovery` ... `05_production`)
- prompt templates
- a legal checklist
- a root `AGENTS.md`
- status and knowledge templates

### What was wrong

1. **The real product was hidden in a zip.** The repository itself was not the system.
2. **The architecture was domain-specific.** It optimized for founder/business discovery, not arbitrary software projects.
3. **Initialization was weak.** It assumed the user would fill templates before ABES became useful.
4. **Context handling was shallow.** It had phase files, but not a durable project intelligence model.
5. **The instruction model was monolithic.** It relied on one broad agent instruction file and phase prompts.
6. **Autonomy was inconsistent.** It wanted durable context, but still expected the user to manage file workflows.
7. **The system had no reusable bootstrap mechanism.** It could not truly be "brought into a new project".

### What was merely scaffolded

Almost everything. There was no executable bootstrap, no real repository ingestion path, no testable initialization behavior, and no architecture for ongoing project memory.

## B. Requirement model

Converted from the problem statement, ABES needs these concrete requirements.

### Product requirements

- chat-first interaction
- durable context without repeated prompt setup
- useful from a cold start in a new project
- capable of surfacing evidence-backed opportunities
- explicit distinction between fact and inference

### Architecture requirements

- repo-native persistence
- small always-on context
- selective loading of project/task/history context
- durable memory separate from working state
- artifacts separate from memory
- conservative initialization with reviewable output

### Maintainability requirements

- readable in Git
- no required external database for MVP
- no giant prompt monolith
- no speculative multi-agent runtime
- easy for future agents to inspect and continue

## C. Research findings

Below are the most relevant systems and what they imply for ABES.

| Repository / system | Relevant architecture | Useful pattern | Weakness | ABES implication |
| --- | --- | --- | --- | --- |
| [Aider-AI/aider](https://github.com/Aider-AI/aider) | terminal coding agent with codebase mapping, git integration, lint/test loops | repository mapping and conservative developer control | optimized for active coding sessions, not durable project memory | ABES should not try to replace the coding agent; it should complement one with better long-lived context |
| [cline/cline](https://github.com/cline/cline) | IDE/CLI/desktop agent with rules, skills, checkpoints, MCP/plugins, multi-agent teams | explicit plan/act split, rules+skills layering, checkpoints | broad surface area and rising complexity | ABES should copy the idea of small persistent rules, but avoid inheriting a heavyweight platform scope |
| [continuedev/continue](https://github.com/continuedev/continue) | coding agent across editor surfaces, source-controlled checks | repo-level configuration and source-controlled agent behavior | archived/read-only; not a durable memory system | ABES should favor source-controlled agent context, but not depend on a single host product |
| [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands) | agent control center connected to agent server backends and automations | separate control plane from execution backends | much heavier than ABES needs for MVP | ABES can later integrate with orchestration systems, but should not become one first |
| [sst/opencode](https://github.com/sst/opencode) | coding-agent runtime with layered context, session state, AGENTS/CLAUDE loading, overflow compaction | explicit separation of system context, session history, context sources, and instruction discovery | more runtime sophistication than ABES needs on day one | ABES should copy its context admission model and session/state separation, not its full runtime |
| [mem0ai/mem0](https://github.com/mem0ai/mem0) | externalized long-term memory infrastructure with retrieval/search APIs | memory as a distinct subsystem | service/platform complexity and additive memory bias | ABES should treat memory as a disciplined layer, but keep MVP repo-native and reviewable |
| [tigerless-labs/agent-memory](https://github.com/tigerless-labs/agent-memory) | markdown truth + SQLite cache + local retrieval | files as truth, index as cache, retrieve-by-path | still more runtime than needed for day one | ABES should adopt file-first truth and selective reading, but skip advanced indexing in MVP |
| [okf-memory/okf-agent-memory](https://github.com/okf-memory/okf-agent-memory) | dual-memory model: small push instructions + pull knowledge bundle | explicit split between small always-on codex and on-demand knowledge | spec-heavy and larger than necessary for MVP | ABES should adopt the small-instruction / larger-knowledge split without copying the full spec stack |
| [alioshr/memory-bank-mcp](https://github.com/alioshr/memory-bank-mcp) | file-based MCP memory server with per-project isolation | portable MCP interoperability over plain project memory files | very simple; no ranking, compaction, or memory discipline by itself | ABES can expose its repo-native memory through MCP later, but MCP is a transport, not the architecture |
| [Claude Code memory docs](https://code.claude.com/docs/en/memory) | layered instruction hierarchy with project/user/local memory and rules/skills/hooks | layered context and keeping always-on instructions small | host-specific | ABES should mirror the layering concept in repo-native files |
| [Cursor rules docs](https://cursor.com/docs/rules) | path-scoped project rules with selective loading | selective rule loading by relevance/path | host-specific behavior | ABES should design for selective context, but not assume a single editor's rule engine |
| [OpenAI Codex AGENTS.md docs](https://github.com/openai/codex/blob/main/docs/agents_md.md) | hierarchical AGENTS loading from global to local directories | repo-local instructions as a durable control plane | limited to instruction files alone | ABES should use AGENTS as the entrypoint, but not as the whole memory system |
| [Model Context Protocol](https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro) | host/client/server protocol for external tools/resources/prompts | standardized capability attachment | does not itself solve durable project memory | ABES can integrate with MCP later, but MCP is not ABES's core identity |

## D. Competitive / architectural landscape

ABES overlaps with:

- AGENTS/CLAUDE/Cursor rule systems for instructions
- memory systems for durable facts
- coding agents for implementation workflows
- orchestration systems for multi-agent coordination

ABES differs if it stays focused on one job:

> make project context durable, inspectable, and agent-usable across sessions and across host tools.

If ABES becomes "yet another memory database" it loses differentiation.
If ABES becomes "yet another coding agent" it competes in the wrong layer.
If ABES becomes "yet another orchestration engine" it becomes too heavy too early.

## E. Proposed ABES architecture

### Components

1. **Instruction entrypoint** – root `AGENTS.md`
2. **Project context** – `.abes/project/*`
3. **Working state** – `.abes/state/current.md`
4. **Durable memory** – `.abes/memory/*`
5. **Artifacts** – `.abes/artifacts/*`
6. **Bootstrap utility** – `scripts/abes_bootstrap.py`
7. **Templates** – `templates/`

This architecture deliberately borrows:

- Aider's bounded repository understanding
- OpenCode's explicit separation of session context from baseline context
- Continue/Codex/Claude-style file-based instruction loading
- OKF/agent-memory's small push layer plus larger pull layer
- MCP only as a future interoperability boundary

### Responsibilities

- `AGENTS.md`: tell future agents what to read and how to behave
- project context: store identity, architecture, goals, unknowns
- state: capture active work without polluting long-term memory
- memory: keep durable decisions, conventions, and opportunities
- artifacts: store plans/specs/research outputs
- bootstrap: initialize ABES in a new repository safely

### Context flow

- always-on: `AGENTS.md`
- small project baseline: `.abes/project/identity.md`
- task baseline: `.abes/state/current.md`
- pull-on-demand: `.abes/memory/*`, `.abes/artifacts/*`

### Memory flow

observation -> state or artifact -> promote durable items into memory -> revise when contradicted

### Agent flow

user request -> read entrypoint -> read project context -> pull needed memory/artifacts -> act -> update state -> promote durable learnings

### Initialization flow

scan repo -> generate project summary and file structure -> install AGENTS block -> create `.abes/` directories/files -> leave explicit unknowns for chat-based correction

### User interaction flow

user speaks in chat -> agent reads ABES context -> agent updates files itself when durable state must change

### Implementation flow

bootstrap first -> first analysis pass -> ongoing work updates state/artifacts/memory

## F. Proposed repository structure

```text
.
├── AGENTS.md
├── README.md
├── docs/
│   ├── architecture.md
│   └── research-and-diagnosis.md
├── scripts/
│   └── abes_bootstrap.py
├── templates/
│   ├── AGENTS.md
│   └── .abes/
│       ├── artifacts/README.md
│       ├── memory/{conventions.md,decisions.md,opportunities.md}
│       ├── project/{architecture.md,goals.md,identity.md}
│       └── state/current.md
└── tests/
    └── test_bootstrap.py
```

Every folder now has a direct reason tied to initialization or durable continuation.

## G. MVP

The smallest useful ABES is:

- a bootstrap command
- a managed AGENTS block
- generated project identity / architecture / goals files
- generated state and durable memory files
- a clear architecture and diagnosis document

That is enough to make future agents materially better at starting work in a new repository.

## H. V2 / later

Possible later additions:

- selective/path-scoped rule loading
- memory indexing/search helpers
- artifact promotion tooling
- evidence freshness/expiry workflow
- opportunity ranking and interruption controls
- optional MCP server for ABES resources
- multi-agent coordination on top of shared ABES state

## I. Failure modes

- memory rot from never pruning durable files
- giant instruction files recreating prompt monoliths
- treating opportunities as requirements
- over-automated initialization that invents architecture facts
- parallel note systems that drift out of sync
- turning ABES into an orchestration platform before the substrate is stable

## J. Final recommendation

ABES should be built as a **project intelligence substrate**, not a business incubator and not a full agent platform.

That means:

- small always-on instructions
- repo-native durable project context
- durable memory with explicit classes
- separate working state
- explicit artifacts
- a conservative bootstrap path

This repository now implements that smallest coherent version.

## What changed in this implementation

- removed the zip-wrapped business-workflow scaffold from the active repository shape
- rewrote the repo around a reusable ABES foundation
- added a concrete bootstrap script
- added templates for durable context and memory
- added focused bootstrap tests

## What remains

- stronger project detection heuristics
- pruning/promotion workflows for memory
- optional path-scoped rules
- richer validation against real foreign repositories
- host integrations beyond plain files

## Uncertain assumptions

- the best long-term memory granularity may eventually need splitting beyond simple markdown files
- different host tools may prefer different instruction injection patterns
- the right opportunity review cadence likely depends on repo size and team style

## What the next independent agent should challenge

1. whether the `.abes/` file taxonomy is the right minimum set
2. whether `AGENTS.md` should stay as the only always-on entrypoint
3. whether opportunities belong in memory or a separate backlog artifact
4. whether bootstrap should emit nested/path-scoped rules next
5. whether MVP needs machine-readable metadata alongside markdown
