# ABES – Automated Business Execution System

**Version 2.0 – Subscription-First, Senior-Engineering-Grade**  
**Status: Ready for real use**

ABES is a structured, file-backed workflow system that helps you go from an open starting point to a real, validated small business or product with minimal manual overhead.

It is designed to work primarily with:
- **Google AI Pro** (Gemini UI + Deep Research + NotebookLM)
- **GitHub Copilot Pro** + VS Code
- Clear, versioned artefacts
- Strong human checkpoints only where they matter

You almost never need to manually copy-paste long prompts. The system is built so that the AI (in VS Code / Copilot / Cursor-style tools) automatically picks up the current phase, the right context files, and the right instructions via `AGENTS.md` and workspace rules.

---

## Quick Start

1. Clone / open this repository in **VS Code**
2. Make sure GitHub Copilot Pro is active
3. Open `AGENTS.md` and read it once
4. Put your initial notes, preferences and constraints into `knowledge/`
5. Start with the Discovery phase (see `workflow/01_discovery/`)

The AI in your IDE will follow the rules in `AGENTS.md` and the phase-specific instructions.

---

## Core Principles

- **Plan before Context, Context before Code**
- Strongly typed status and claim tracking (no pure prompt trust)
- Human checkpoints only at strategic points
- You remain the legal owner of every business
- No autonomous legal or financial actions
- Everything is versioned in Git

---

## High-Level Process

1. **Discovery** → ranked candidates
2. **Research & Validation** → sourced report + GO/NO-GO
3. **Human Checkpoint 1**
4. **Product Definition**
5. **Architecture & Blueprint**
6. **Human Checkpoint 2**
7. **Production** (Traversy-style feature-by-feature)
8. **Pre-Launch Legal Gate** (human)
9. **Launch & Feedback**

---

## How to work (almost no manual pasting)

- The AI in VS Code reads `AGENTS.md` + the current phase folder + `status/` automatically.
- You talk to the AI in natural language:  
  “Run Discovery with my notes in knowledge/”  
  “Do Research on the top 3 candidates”  
  “Create the Product Spec”
- The AI writes the output files into the correct places.
- You only review and approve at the defined checkpoints.

For heavy Deep Research you can still open Gemini UI / NotebookLM and drop the resulting report into `knowledge/` or `status/`.

---

## Folder Overview

- `workflow/` – Phase-specific instructions and templates
- `prompts/` – Ready-to-use prompt templates (the AI loads them)
- `status/` – Current claims, GO/NO-GO, progress
- `knowledge/` – Your notes + research material
- `blueprints/` – Versioned blueprints per business idea
- `projects/` – Actual implementations
- `docs/` – Architecture, legal checklist, decision records

---

## Legal Notice

You are and remain the sole legal owner and responsible person for any business created with this system.  
ABES never creates legal entities, domains, payment accounts or tax registrations.

Before any public launch there is a mandatory human Legal Gate.

---

## Next Steps

1. Fill `knowledge/00_preferences.md` with your constraints and interests.
2. Tell the AI: “Start Discovery”
3. Follow the process.

Built for real use. No vaporware.