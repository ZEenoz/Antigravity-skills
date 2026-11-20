# Antigravity & Agent Skills

Collection of **160** curated skills for **Antigravity 2.0**, **Claude Code**, **Cursor**, **Codex**, **Gemini CLI**, and other AI coding agents.

---

## Automated Installation

### Option 1: Using `npx skills` CLI (Recommended for Selective or Multi-Agent Install)

Install all skills globally for **Antigravity 2.0** (and canonical `~/.agents/skills`):

```bash
npx skills add ZEenoz/Antigravity-skills -g -a antigravity -s '*' -y
```

Install all skills globally across **all detected agents** (`Claude Code`, `Cursor`, `Codex`, `Antigravity`, etc.):

```bash
npx skills add ZEenoz/Antigravity-skills -g --all
```

Install specific skills only:

```bash
npx skills add ZEenoz/Antigravity-skills -g -a antigravity -s using-superpowers brainstorming -y
```

List all available skills without installing:

```bash
npx skills add ZEenoz/Antigravity-skills --list
```

Update installed skills tracked in `.skill-lock.json`:

```bash
npx skills update -g -y
```

---

### Option 2: Automated Git Install & Sync (Full Mirror for `.agents/skills` & `.gemini/config/skills`)

Use these one-liners to install fresh or sync existing directories to the latest `main` commit.

#### Windows (PowerShell)

```powershell
$repo = "https://github.com/ZEenoz/Antigravity-skills.git"
foreach ($dir in @("$HOME\.agents\skills", "$HOME\.gemini\config\skills")) {
    if (Test-Path "$dir\.git") {
        git -C $dir fetch origin --quiet
        git -C $dir reset --hard origin/main
    } else {
        New-Item -ItemType Directory -Force -Path (Split-Path $dir) | Out-Null
        git clone $repo $dir
    }
}
```

#### macOS / Linux (Bash)

```bash
REPO="https://github.com/ZEenoz/Antigravity-skills.git"
for dir in "$HOME/.agents/skills" "$HOME/.gemini/config/skills"; do
  if [ -d "$dir/.git" ]; then
    git -C "$dir" fetch origin --quiet && git -C "$dir" reset --hard origin/main
  else
    mkdir -p "$(dirname "$dir")" && git clone "$REPO" "$dir"
  fi
done
```

> **Note:** On **Antigravity Legacy (`< 2.0`)**, clone to `~/.gemini/antigravity/skills` instead of `~/.gemini/config/skills`.

---

## Directory Paths

| Target | Path |
| --- | --- |
| **Antigravity 2.0** | `~/.gemini/config/skills` |
| **Antigravity (Legacy)** | `~/.gemini/antigravity/skills` |
| **Global Agents (Universal)** | `~/.agents/skills` |

---

## Skills Catalog (160 Skills)

### Superpowers & Execution Workflow (15)
- **`using-superpowers`**: Disciplined skill-first agent execution workflow.
- **`diagnosing-superpowers`**: Evidence-backed transcript diagnostics for superpowers sessions.
- **`brainstorming`**: Collaborative requirement exploration and design before implementation.
- **`writing-plans`**: Structural planning for multi-step implementation tasks.
- **`executing-plans`**: Step-by-step plan execution with verification checkpoints.
- **`subagent-driven-development`**: Parallel/isolated subagent execution with review loops.
- **`dispatching-parallel-agents`**: Fan-out coordination for independent tasks.
- **`requesting-code-review`**: Structured pre-merge code review request workflow.
- **`receiving-code-review`**: Rigorous verification when handling review feedback.
- **`systematic-debugging`**: Root-cause-first debugging protocol before proposing fixes.
- **`test-driven-development`**: Red-green-refactor TDD enforcement.
- **`using-git-worktrees`**: Isolated git worktree setup for feature branches.
- **`verification-before-completion`**: Mandatory command verification before claiming completion.
- **`finishing-a-development-branch`**: Clean merge, PR, or cleanup workflow after completion.
- **`writing-skills`**: Authoring, testing, and refining agent skills.

### Engineering, Architecture & Matt Pocock Suite (35)
- **`ask-matt`**: Router to pick the right engineering skill or workflow.
- **`code-review`**: Dual-axis code review (repo standards + originating spec).
- **`codebase-design`**: Deep-module design vocabulary and interface seam analysis.
- **`diagnosing-bugs`**: Diagnosis loop for hard bugs and performance regressions.
- **`domain-modeling`**: Sharpen domain vocabulary, `GLOSSARY.md`, and ADRs.
- **`grill-me` / `grilling` / `grill-with-docs`**: Interactive adversarial questioning to stress-test plans and specs.
- **`implement` / `implement-spec`**: High-precision feature implementation from specs.
- **`improve-codebase-architecture`**: Architecture refactoring and decoupling.
- **`prototype`**: Throwaway prototypes to validate design or state models.
- **`research`**: Primary-source investigation captured into Markdown findings.
- **`resolving-merge-conflicts`**: Conflict resolution assistant.
- **`retro`**: Session retrospective and improvement review.
- **`triage`**: Issue triage and prioritization workflow.
- **`wayfinder`**: Orientation and navigation across unfamiliar codebases.
- **`wizard`**: Generate interactive bash wizards for human-only setup steps.
- **`to-questionnaire` / `to-spec` / `to-tickets`**: Convert ideas into questionnaires, specs, and actionable tickets.
- **`handoff` / `claude-handoff`**: Structured session handoff summaries.
- **`loop-me` / `wait-what`**: Iterative loop execution and sanity-check pauses.
- **`git-guardrails-claude-code`**: Pre-commit/hook guardrails against destructive git commands.
- **`migrate-to-shoehorn`**: Replace `as` assertions in tests with `@total-typescript/shoehorn`.
- **`scaffold-exercises`**: Exercise directory scaffolding that passes linting.
- **`setup-matt-pocock-skills` / `setup-pre-commit` / `setup-ts-deep-modules`**: Project setup for Matt Pocock skills, Husky/Prettier hooks, and deep TS modules.
- **`writing-beats` / `writing-for-agents` / `writing-fragments` / `writing-shape`**: Technical and agent-facing writing guides.

### `pstack` Principles & Playbooks (58)
- **Workflow & Execution**: `architect`, `arena`, `automate-me`, `benchmark-checklist`, `blast-radius`, `bro`, `correct`, `create-formal-verification-skill`, `create-verification-skill`, `figure-it-out`, `how`, `in-your-own-words`, `interrogate`, `ketchup`, `ketchup-video`, `maintain-formal-verification-skill`, `maintain-verification-skill`, `make-bot-ui`, `no-comments`, `poteto-help`, `poteto-mode`, `recall`, `reflect`, `setup-pstack`, `sharpen`, `show-me-your-work`, `statechart`, `swarm`, `tdd`, `teach`, `technical-writing`, `typescript-best-practices`, `unslop`, `why`.
- **Engineering Principles (`principle-*`)**: `principle-attack-the-premise`, `principle-boundary-discipline`, `principle-build-the-lever`, `principle-encode-lessons-in-structure`, `principle-exhaust-the-design-space`, `principle-experience-first`, `principle-explain-the-number`, `principle-fix-root-causes`, `principle-foundational-thinking`, `principle-guard-the-context-window`, `principle-laziness-protocol`, `principle-make-operations-idempotent`, `principle-migrate-callers-then-delete-legacy-apis`, `principle-minimize-reader-load`, `principle-model-the-domain`, `principle-never-block-on-the-human`, `principle-outcome-oriented-execution`, `principle-prove-it-works`, `principle-redesign-from-first-principles`, `principle-separate-before-serializing-shared-state`, `principle-sequence-verifiable-units`, `principle-subtract-before-you-add`, `principle-test-behavior-not-implementation`, `principle-type-system-discipline`.

### Hybrid & Enterprise Precision Workflows (11)
- **`superpowers-ponytail`**: Disciplined skill-first process combined with minimalist YAGNI execution.
- **`stress-tested-architecture`**: Brainstorming combined with adversarial grilling for system design RFCs.
- **`precision-diagnostics`**: Multi-phase root-cause diagnosis with deterministic repros.
- **`precision-coding-agent`**: Precision coding workflow with strict verification.
- **`debug-precision`**: Strict step-by-step root-cause debugging (Thai/EN).
- **`intelligent-coding`**: Token-efficient, DRY/KISS, zero-hardcoding engineering standard.
- **`phase-implementation-planner`**: Phased multi-tech implementation planning.
- **`pattern-inversion` / `pattern-chained-inversion` / `pattern-generator`**: Requirement elicitation and standardized output generation.
- **`flowchart-designer`**: Business/action-based system flowchart design.

### Continuous Learning, Memory & Audits (7)
- **`continuous-learning` / `continuous-learning-v2`**: Instinct-based session observation and continuous learning.
- **`task-observer`**: Autonomous task observation, workflow reflection, and skill patch staging.
- **`hindsight-coding-agent`**: Long-term coding-agent memory configuration and retrieval guide.
- **`deep-research`**: Evidence-backed pre-execution reconnaissance dossier.
- **`deep-study`**: Exhaustive folder analysis and tree workflow generation.
- **`full-system-audit`**: Token-efficient full-project audit across architecture, security, and quality.

### Language & Framework Standards (6)
- **`python-testing-patterns`**: Comprehensive `pytest`, fixture, mocking, and TDD patterns.
- **`python-code-style`**: Python style, linting, formatting, and docstrings.
- **`java-coding-standards`**: Spring Boot and Quarkus coding conventions.
- **`java-junit`**: JUnit 5/6, AssertJ, Mockito, and mutation testing patterns.
- **`javafx-modern-ui`**: Modern JavaFX UI/UX and responsive layout design.
- **`javafx-precison-coding`**: Production-grade JavaFX development without hardcoded values.

### Efficiency, Simplicity & Prose (14)
- **`caveman` / `ultracave` / `megacave` / `caveman-th` / `caveman-coding` / `caveman-plan`**: Ultra-terse token-saving modes (including Thai & Wenyan variants).
- **`ponytail` / `ponytail-review` / `ponytail-audit` / `ponytail-debt` / `ponytail-gain` / `ponytail-help`**: Ruthless simplicity, YAGNI enforcement, and debt tracking.
- **`humanizer` / `humanizer-th`**: Remove AI-sounding prose patterns in English and Thai.

### Frontend, UI/UX, Diagrams & Documents (11)
- **`design-taste-frontend`**: Anti-slop, high-craft web frontend design and verification.
- **`ui-ux-pro-max`**: Searchable UI/UX design intelligence, palettes, typography, and stack guidance.
- **`impeccable`**: Design critique, polish, motion, theming, and visual craft.
- **`wshobson-responsive-design`**: Container queries, fluid typography, CSS Grid, and responsive layouts.
- **`web-artifacts-builder`**: Multi-component React/Tailwind/shadcn HTML artifacts.
- **`frontend-slides`**: Zero-dependency animation-rich HTML presentation decks.
- **`pptx-generator` / `elite-powerpoint-designer`**: PowerPoint generation, XML editing, and visual design.
- **`office-mcp`**: Word, Excel, PowerPoint, PDF, and OCR MCP workflows.
- **`thesis-report-writer`**: Thesis and co-op `.docx` report writer and style compliance checker.
- **`archify`**: Interactive HTML/SVG architecture, sequence, ERD, and workflow diagrams.

### Meta & Tooling (3)
- **`find-skills`**: Discover and install skills from the open agent skills ecosystem.
- **`skill-creator`**: Create, benchmark, evaluate, and package skills.
- **`omp-add-provider`**: Configure and extend model providers for Oh My Pi (`omp`).
