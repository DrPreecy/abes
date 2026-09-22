# ABES Architecture

## Thesis

ABES should be a **repository-native context operating layer for coding agents**.

Its job is not to replace the coding agent, the editor, or the task tracker.
Its job is to make project context durable, structured, and recoverable across sessions so the user can mostly say:

> I want to do X.

and the agent can determine the relevant workflow with minimal manual prompting.

## What ABES must do

1. enter a new project with little prior context
2. inspect the repository and detect the technology surface
3. establish a durable context layer inside the repository
4. separate long-lived memory from current-session state
5. store plans and research as explicit artifacts
6. keep facts separate from guesses and recommendations
7. surface high-value opportunities without pretending they are requirements

## Core model

ABES has five layers.

### 1. Normative instruction layer

Purpose: small, stable guidance that should be available early.

Mechanism:

- root `AGENTS.md`
- optional existing project instructions preserved around an ABES-managed block

Contents:

- what to read first
- memory discipline
- fact / inference / hypothesis / recommendation distinction
- update responsibilities

### 2. Project context layer

Purpose: durable project identity and architecture facts.

Files:

- `.abes/project/identity.md`
- `.abes/project/architecture.md`
- `.abes/project/goals.md`

Contents:

- detected stack and manifests
- likely source and test locations
- observed commands and entrypoints
- user goals and constraints
- known unknowns

### 3. Working state layer

Purpose: active state that changes frequently.

Files:

- `.abes/state/current.md`

Contents:

- current objective
- active questions
- near-term next steps
- temporary risks/blockers

Rule: this layer is allowed to change often and does not need long-term historical completeness.

### 4. Durable memory layer

Purpose: information worth keeping across sessions.

Files:

- `.abes/memory/decisions.md`
- `.abes/memory/conventions.md`
- `.abes/memory/opportunities.md`

Memory classes:

- **decisions**: choices that changed the project direction
- **conventions**: repeatable repo habits and constraints
- **opportunities**: candidate improvements or ideas, always tagged with evidence and confidence

Rule: memory should only contain durable information that a future agent would reasonably need.

### 5. Artifact layer

Purpose: generated outputs for plans, specs, research, and implementation support.

Files:

- `.abes/artifacts/*`

Artifacts are not baseline memory. They are reusable outputs that may later promote facts into durable memory.

## Data flow

```text
user request
  -> agent reads AGENTS.md
  -> agent reads .abes/project/*
  -> agent reads .abes/state/current.md
  -> agent selectively reads memory/artifacts
  -> agent plans / researches / implements
  -> agent updates state
  -> agent promotes only durable learnings into memory
```

## Initialization flow

```text
bring ABES into repo
  -> bootstrap scans repository surface
  -> bootstrap writes AGENTS block and .abes structure
  -> first agent reviews generated identity/architecture/goals
  -> user corrects missing intent through chat
  -> future sessions start from durable context instead of zero
```

## Controlled idea discovery

ABES should propose ideas only when triggered by evidence.

### Allowed triggers

- repeated failures or recurring TODO classes
- explicit review/audit requests
- architecture contradictions discovered during work
- repeated manual work that suggests automation
- bootstrap findings that reveal missing fundamentals

### Evidence requirement

Every idea should record:

- type: technical / product / workflow / research
- evidence
- confidence
- why it matters now
- why it is not already a requirement

Store those in `.abes/memory/opportunities.md`, not as facts.

## Multi-agent stance

ABES should support multiple agent roles, but only conceptually in MVP.

Useful roles:

- researcher
- planner
- implementer
- reviewer
- critic
- verifier

MVP does not need an orchestration runtime. It only needs a shared context substrate those agents can all read.

## Why this is smaller than the original concept

A giant autonomous system is not the shortest path to value.

The smallest useful ABES is:

- bootstrap
- context files
- memory discipline
- artifact discipline
- clear instruction entrypoint

Anything beyond that must justify its cost.
