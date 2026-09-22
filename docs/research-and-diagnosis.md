# ABES Research and Diagnosis

## Independent conclusion

ABES should be a **small project-intelligence substrate for coding agents**:

- one small always-on instruction entrypoint
- one durable intent brief
- one observed repository inventory
- one current-state file
- a narrow durable memory layer
- artifacts for everything else

That is enough to make a new or existing repository materially easier for future agents to enter without turning ABES into a framework that demands its own workflow.

## What the earlier architecture got wrong

The earlier reset moved ABES in the right general direction, but it still missed several important points.

### 1. It kept too many top-level context buckets

Splitting durable project context into `identity.md`, `architecture.md`, and `goals.md` looks tidy, but for a tiny bootstrap foundation it creates unnecessary routing overhead. Most sessions need one place for intent and one place for repository evidence, not three semi-overlapping files.

### 2. It treated opportunities as default durable memory

Ideas are usually the noisiest class of information. Making `opportunities.md` a default durable memory file biases the system toward accumulating speculative backlog instead of preserving only what repeatedly proves useful.

### 3. It did not define contradiction handling strongly enough

The first architecture talked about durable context, but not clearly enough about what happens when code, memory, and user instructions disagree. Without an explicit precedence model, context rot is guaranteed.

### 4. It bootstrap-scanned too naively

The initial bootstrap walked the entire tree through repeated globbing, followed symlinked write targets implicitly, and inferred commands too optimistically. That is fragile in real repositories.

### 5. It still left too much context maintenance burden on the user

The docs argued for chat-first usage, but the generated file set was still generic enough that future agents would often need the user to manually clarify what belongs where.

## What the earlier architecture got right

### 1. ABES should be repo-native

Keeping context in Git-visible files is correct for portability, inspection, and multi-tool use.

### 2. State and durable memory should be separate

This is the single strongest decision in the earlier architecture and should remain.

### 3. Bootstrap should be conservative

The idea that bootstrap should create helpful files without inventing deep architecture is correct.

### 4. ABES should complement, not replace, the coding agent

Trying to compete with the host agent or editor would push ABES into the wrong product layer.

## Research that changed the final position

The following patterns materially influenced the revised architecture:

| Source | Relevant pattern | Impact on ABES |
| --- | --- | --- |
| [Session Briefing](https://github.com/CaptCanadaMan/session-briefing) | persistent context and current state should be split cleanly, and current state should stay small rather than grow into a log | reinforced keeping a single current-state file separate from durable context |
| [Awesome Progress Tracker](https://github.com/AndriiLavrekha/awesome-progress-tracker) | one compact resume file plus lightweight automation often beats a large knowledge base | pushed ABES toward a smaller state model and away from default idea-memory sprawl |
| [Agent Kit](https://github.com/Mapl6/agent-kit) | bootstrap/indexing should be conservative, local-first, and explicit about safety limits | reinforced pruning generated/vendor trees and rejecting unsafe file targets |
| [codecricket](https://github.com/fransjorden/codecricket) | always-on instructions must stay small, memory can leak secrets, and cross-tool context needs clear boundaries | reinforced keeping ABES file-first, small, and cautious about what becomes durable memory |

These patterns argue against a larger architecture more strongly than they argue for new subsystems.

## Disagreement matrix

| Topic | Previous approach | Independent view | Evidence | Decision |
| --- | --- | --- | --- | --- |
| Core architecture | five layers with three project files plus opportunities memory | keep the layered idea but collapse project context to `brief + inventory` and remove default opportunity memory | current docs over-separate intent/evidence; external systems succeed with fewer high-signal files | simplify |
| Context | `identity.md`, `architecture.md`, `goals.md` | `brief.md` for intent, `inventory.md` for observed repo facts | most sessions need intent + evidence, not three documents | merge |
| Memory | decisions, conventions, opportunities | decisions + conventions only; opportunities belong in artifacts until justified | opportunity lists create noise faster than durable value | reduce |
| Instructions | read multiple project files first | read three files first: `AGENTS.md`, `brief`, `inventory`, then state | always-on context should stay small | tighten |
| Initialization | repeated glob scans over full tree | single conservative directory walk with pruning | large repos and generated trees break naive globbing | replace |
| Agents | conceptual multi-agent roles | keep roles conceptual only; no runtime | no evidence that ABES needs orchestration before context quality | keep small |
| Research | architecture doc referenced external systems broadly | use external systems mainly as negative pressure against complexity | the best examples succeed by staying focused | narrow |
| Autonomous ideas | default opportunities memory file | evidence-backed idea artifacts only when useful | not every repo needs a standing idea backlog | demote |
| Artifacts | explicit artifact layer | keep it | reusable outputs need a home separate from memory | keep |
| State | one current state file | keep it, but add contradiction handling | current truth drifts without an explicit conflict section | strengthen |
| User interaction | chat-first claimed in docs | enforce chat-first by reducing file-routing burden | user should not need to remember ABES workflow details | strengthen |
| Persistence | repo-native markdown only | keep markdown-first persistence | portability and reviewability matter more than clever storage | keep |
| Extensibility | optional future MCP/rules/search later | keep optional only | premature extensibility is still overhead | defer |
| Security | force protected by managed marker only | also reject symlinked destinations and prune unsafe traversal | current review findings expose concrete safety gaps | harden |
| Complexity | minimal compared with original zip scaffold | still too large for the actual minimum core | scenario testing shows smaller structure works better | reduce |

## Scenario tests

### Scenario A — Empty / new software project

ABES should bootstrap a brief with explicit unknowns and an inventory showing little detected structure. The next chat should clarify goals, not force the user to fill templates before work can begin.

### Scenario B — Existing mature codebase

ABES should generate a conservative inventory, capture likely commands and key locations, and then let future agents refine durable conventions and decisions as they verify them.

### Scenario C — Messy prototype

The brief should capture unstable goals and constraints, the inventory should expose where code actually lives, and the current-state file should track contradictions until they are resolved.

### Scenario D — Product idea with little code

The brief becomes more important than the inventory. ABES should capture the idea, unknowns, and decision points without pretending the repo already contains validated architecture.

### Scenario E — User has no idea what to do next

ABES may propose next actions, but only from evidence: missing tests, contradictory docs, absent deployment path, or obvious repo gaps. Suggestions belong in artifacts or current state until accepted or repeatedly justified.

### Scenario F — Conflicting information

When memory says one thing, code says another, and the user says something else:

- user intent wins for what should happen next
- code wins for what exists now
- memory becomes stale until updated

Without this rule, ABES turns into a drift amplifier.

## Final architecture

```text
AGENTS.md
  -> .abes/project/brief.md
  -> .abes/project/inventory.md
  -> .abes/state/current.md
  -> relevant memory/artifacts only when needed
```

Generated structure:

```text
.abes/
├── artifacts/
│   └── README.md
├── memory/
│   ├── conventions.md
│   └── decisions.md
├── project/
│   ├── brief.md
│   └── inventory.md
└── state/
    └── current.md
```

## Implementation implications

The repository should implement:

1. a safer bootstrap
2. the reduced file structure above
3. conflict handling guidance in generated instructions
4. tests covering traversal, parsing, and unsafe write cases

Anything beyond that is not required for ABES to be useful today.
