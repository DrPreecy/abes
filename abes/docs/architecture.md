# ABES Architecture

## Philosophy

Subscription-First + File-backed Control System.

The system maximises the value of Google AI Pro (UI + Deep Research + NotebookLM) and GitHub Copilot Pro while keeping the human in strategic control and eliminating pure vibe-coding.

## Key Design Decisions

- Artefacts over shared mutable state
- Explicit phases with clear entry/exit criteria
- Truth status is enforced by rules, not just prompts
- Legal ownership stays with the human
- Production follows Traversy AI Blueprint style (plan → feature → implement → check → audit → complete)

## Data Flow

User notes (knowledge/) 
→ Discovery 
→ Research & Validation (with sources + status)
→ Human Checkpoint 1
→ Product Spec
→ Blueprint (including legal checklist)
→ Human Checkpoint 2
→ Production (feature-by-feature)
→ Pre-Launch Legal Gate
→ Launch

## Why this works with the subscription

Heavy reasoning and research happen in the Gemini UI / NotebookLM (full Abo power).  
Coding and iterative implementation happen in VS Code with Copilot Pro.  
The repository acts as the durable memory and control plane so the AI always knows the current context without the user pasting large prompts.