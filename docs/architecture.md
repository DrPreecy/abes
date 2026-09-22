# ABES Architecture

## Conclusion

ABES should be a **small, repository-native continuity layer for coding agents**.

It should not try to be the coding agent, the orchestration runtime, or the memory platform.  
It should give the agent just enough durable structure to enter a project, recover what matters, keep state current, and leave the repository easier to resume than it found it.

## Design goals

1. chat-first use
2. low user cognitive load
3. durable context in Git
4. explicit separation of stable context vs changing state
5. evidence-backed memory promotion
6. portability across host tools
7. minimal always-on token cost

## Minimum core

### 1. Instruction entrypoint

**File:** `AGENTS.md`

Purpose:

- tell future agents what to read first
- define conflict resolution rules
- keep always-on instructions small

### 2. Durable project brief

**File:** `.abes/project/brief.md`

Purpose:

- capture what the project is trying to achieve
- record stable constraints and priorities
- preserve high-value unknowns future sessions should clarify

This is about **intent**, not repository detection.

### 3. Repository inventory

**File:** `.abes/project/inventory.md`

Purpose:

- store bootstrap-generated observations about the repo surface
- record detected manifests, likely code/test/doc locations, and commands to verify
- separate observed facts from inferred meaning

This is about **evidence**, not intent.

### 4. Working state

**File:** `.abes/state/current.md`

Purpose:

- track what is being worked on now
- record blockers and active questions
- hold contradictions until the durable layers are updated

This file should stay current, not cumulative.

### 5. Durable memory

**Files:**

- `.abes/memory/decisions.md`
- `.abes/memory/conventions.md`

Purpose:

- keep only durable facts future agents will actually need
- separate project-changing decisions from repeatable conventions

ABES should **not** default to a third memory class for idea generation. Candidate ideas are too volatile to deserve always-on durable memory by default.

### 6. Artifacts

**Directory:** `.abes/artifacts/`

Purpose:

- hold reusable outputs like plans, research, specifications, and review summaries
- hold opportunity backlogs or investigations that are not durable memory yet

## Conflict model

If sources disagree:

1. **user statements** define current goals and priorities
2. **code and runtime evidence** define current implementation truth
3. **ABES files** are cached project context and must be corrected when stale

This rule is required for scenario handling, especially when memory, code, and chat diverge.

## Initialization flow

```text
bootstrap ABES into repository
  -> scan repository conservatively
  -> create AGENTS block
  -> create project brief, inventory, state, memory, and artifact files
  -> leave unknowns explicit instead of inventing answers
  -> let the next chat refine goals and constraints
```

## Agent workflow

```text
user says something natural
  -> agent reads AGENTS.md
  -> agent reads brief, inventory, current state
  -> agent decides whether the task is research / plan / implementation / review
  -> agent pulls only relevant memory/artifacts
  -> agent works
  -> agent updates current state
  -> agent promotes durable facts only when justified
```

The user should not have to decide which file to update or which workflow to activate.

## Why this is smaller than the previous direction

The previous implementation had the right instinct about durable context, but still carried avoidable structure:

- three separate project files when two are enough
- a default opportunity-memory file that encourages noise
- too little guidance on contradiction handling
- too much reliance on the user to keep context truthful

The revised architecture removes what is not foundational while strengthening the pieces that matter.

## What stays optional

Not part of the ABES core:

- multi-agent orchestration runtime
- MCP server
- search/index database
- path-scoped rule engine
- autonomous idea ranking service
- machine-readable snapshot cache beyond the Markdown inventory

These may become useful later, but ABES does not need them to be valuable now.
