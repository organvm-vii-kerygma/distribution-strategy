# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

`kerygma_strategy` — the analytics, scheduling, and distribution strategy package for ORGAN-VII (Kerygma). Tracks engagement metrics, manages publication calendars with posting modifiers, configures channel registries, and generates distribution reports.

## Package Structure

Source is in `kerygma_strategy/`, installed as the `kerygma_strategy` package:

| Module | Purpose |
|--------|---------|
| `analytics.py` | `AnalyticsCollector` — records `EngagementMetric` dataclasses (impressions, clicks, shares, replies). Auto-persists every N records via `JsonStore`. `aggregate_by_channel()`, `top_content()` queries. |
| `scheduler.py` | `ContentScheduler` — manages `ScheduleEntry` with recurrence (`Frequency` enum: ONCE/DAILY/WEEKLY/BIWEEKLY/MONTHLY). `get_due()`, `get_upcoming()`. Calendar-aware: `schedule_with_calendar()` delays posts during quiet periods. `get_due_with_priority()` returns `PrioritizedEntry` scored by overdue hours * calendar modifier. |
| `calendar.py` | `DistributionCalendar` — tracks `CalendarEvent` objects (grant_deadline, conference, quiet_period). `get_posting_modifier()` multiplies active event modifiers. `is_quiet_period()` check. Loadable from YAML via `from_yaml()`. |
| `channels.py` | `ChannelRegistry` — `ChannelConfig` dataclasses with `channel_id`, `platform`, `max_length`, `enabled`. `format_content()` truncates to limit. YAML serialize/deserialize via `from_yaml()`/`to_yaml()`. |
| `persistence.py` | `JsonStore` — key-value store with atomic writes (`os.replace` via `.tmp` file). Used by `AnalyticsCollector` for metric persistence. |
| `report_generator.py` | Generates Markdown distribution reports from analytics data. |
| `ghost_metrics.py` | Pull-back adapter for Ghost newsletter engagement metrics. |
| `mastodon_metrics.py` | Pull-back adapter for Mastodon post engagement metrics. |
| `config.py` | `load_config(path)` → `StrategyConfig` dataclass. YAML-based config for analytics store path, calendar path, channels path, reports directory. |
| `cli.py` | CLI entry point (`distrib`). |

## Development Commands

```bash
# Install (from superproject root or this directory)
pip install -e .[dev]

# Tests
pytest tests/ -v
pytest tests/test_scheduler.py::TestContentScheduler::test_get_due -v

# Lint
ruff check kerygma_strategy/
```

## Key Design Details

- **Calendar modifiers** are multiplicative: a `posting_modifier` of 1.5 (conference) combined with another 1.5 (grant deadline) yields 2.25x. Quiet periods use < 1.0 (e.g., 0.3). The scheduler uses these to prioritize what to post.
- **Scheduler auto-reschedules recurring entries** — when `publish_entry()` is called on a recurring entry, it creates a new `{id}-next` entry at the next occurrence time.
- **Analytics flush** — `AnalyticsCollector` buffers records in memory and auto-persists every `persist_every` records (default 50). Call `flush()` explicitly after batch operations.
- **JsonStore uses atomic writes** — same pattern as other ORGAN-VII stores: write to `.tmp`, then `os.replace()`.
- **Runtime dependency**: only `pyyaml>=6.0` (for channel/calendar/config YAML loading).

## Test Structure

Tests in `tests/` with `fixtures/` directory:
- `test_analytics.py` — recording, aggregation, top content
- `test_analytics_persistence.py` — JsonStore round-trip
- `test_scheduler.py` — due/upcoming, publish, recurrence
- `test_scheduler_calendar.py` — calendar-aware scheduling, quiet periods, priority
- `test_calendar.py` — event lifecycle, modifiers, active windows
- `test_channels.py` — registry, format_content, enable/disable
- `test_channels_yaml.py` — YAML serialize/deserialize
- `test_persistence.py` — JsonStore atomic writes, from_dict
- `test_report_generator.py` — Markdown report output
- `test_ghost_metrics.py` — Ghost metrics adapter
- `test_mastodon_metrics.py` — Mastodon metrics adapter

## ORGANVM Context

Consumes essays from ORGAN-V. Produces distribution artifacts consumed by ORGAN-IV. Subscribes to `essay.published` and `promotion.completed` events.

<!-- ORGANVM:AUTO:START -->
## System Context (auto-generated — do not edit)

**Organ:** ORGAN-VII (Marketing) | **Tier:** standard | **Status:** GRADUATED
**Org:** `organvm-vii-kerygma` | **Repo:** `distribution-strategy`

### Edges
- **Produces** → `ORGAN-IV`: distribution_artifact
- **Consumes** ← `ORGAN-V`: essay

### Siblings in Marketing
`announcement-templates`, `social-automation`, `.github`, `kerygma-pipeline`, `kerygma-profiles`

### Governance
- *Standard ORGANVM governance applies*

*Last synced: 2026-04-14T21:32:12Z*

## Active Handoff Protocol

If `.conductor/active-handoff.md` exists, **READ IT FIRST** before doing any work.
It contains constraints, locked files, conventions, and completed work from the
originating agent. You MUST honor all constraints listed there.

If the handoff says "CROSS-VERIFICATION REQUIRED", your self-assessment will
NOT be trusted. A different agent will verify your output against these constraints.

## Session Review Protocol

At the end of each session that produces or modifies files:
1. Run `organvm session review --latest` to get a session summary
2. Check for unimplemented plans: `organvm session plans --project .`
3. Export significant sessions: `organvm session export <id> --slug <slug>`
4. Run `organvm prompts distill --dry-run` to detect uncovered operational patterns

Transcripts are on-demand (never committed):
- `organvm session transcript <id>` — conversation summary
- `organvm session transcript <id> --unabridged` — full audit trail
- `organvm session prompts <id>` — human prompts only


## System Library

Plans: 269 indexed | Chains: 5 available | SOPs: 121 active
Discover: `organvm plans search <query>` | `organvm chains list` | `organvm sop lifecycle`
Library: `meta-organvm/praxis-perpetua/library/`


## Active Directives

| Scope | Phase | Name | Description |
|-------|-------|------|-------------|
| system | any | atomic-clock | The Atomic Clock |
| system | any | execution-sequence | Execution Sequence |
| system | any | multi-agent-dispatch | Multi-Agent Dispatch |
| system | any | session-handoff-avalanche | Session Handoff Avalanche |
| system | any | system-loops | System Loops |
| system | any | prompting-standards | Prompting Standards |
| system | any | research-standards-bibliography | APPENDIX: Research Standards Bibliography |
| system | any | phase-closing-and-forward-plan | METADOC: Phase-Closing Commemoration & Forward Attack Plan |
| system | any | research-standards | METADOC: Architectural Typology & Research Standards |
| system | any | sop-ecosystem | METADOC: SOP Ecosystem — Taxonomy, Inventory & Coverage |
| system | any | autonomous-content-syndication | SOP: Autonomous Content Syndication (The Broadcast Protocol) |
| system | any | autopoietic-systems-diagnostics | SOP: Autopoietic Systems Diagnostics (The Mirror of Eternity) |
| system | any | background-task-resilience | background-task-resilience |
| system | any | cicd-resilience-and-recovery | SOP: CI/CD Pipeline Resilience & Recovery |
| system | any | community-event-facilitation | SOP: Community Event Facilitation (The Dialectic Crucible) |
| system | any | context-window-conservation | context-window-conservation |
| system | any | conversation-to-content-pipeline | SOP — Conversation-to-Content Pipeline |
| system | any | cross-agent-handoff | SOP: Cross-Agent Session Handoff |
| system | any | cross-channel-publishing-metrics | SOP: Cross-Channel Publishing Metrics (The Echo Protocol) |
| system | any | data-migration-and-backup | SOP: Data Migration and Backup Protocol (The Memory Vault) |
| system | any | document-audit-feature-extraction | SOP: Document Audit & Feature Extraction |
| system | any | dynamic-lens-assembly | SOP: Dynamic Lens Assembly |
| system | any | essay-publishing-and-distribution | SOP: Essay Publishing & Distribution |
| system | any | formal-methods-applied-protocols | SOP: Formal Methods Applied Protocols |
| system | any | formal-methods-master-taxonomy | SOP: Formal Methods Master Taxonomy (The Blueprint of Proof) |
| system | any | formal-methods-tla-pluscal | SOP: Formal Methods — TLA+ and PlusCal Verification (The Blueprint Verifier) |
| system | any | generative-art-deployment | SOP: Generative Art Deployment (The Gallery Protocol) |
| system | any | market-gap-analysis | SOP: Full-Breath Market-Gap Analysis & Defensive Parrying |
| system | any | mcp-server-fleet-management | SOP: MCP Server Fleet Management (The Server Protocol) |
| system | any | multi-agent-swarm-orchestration | SOP: Multi-Agent Swarm Orchestration (The Polymorphic Swarm) |
| system | any | network-testament-protocol | SOP: Network Testament Protocol (The Mirror Protocol) |
| system | any | open-source-licensing-and-ip | SOP: Open Source Licensing and IP (The Commons Protocol) |
| system | any | performance-interface-design | SOP: Performance Interface Design (The Stage Protocol) |
| system | any | pitch-deck-rollout | SOP: Pitch Deck Generation & Rollout |
| system | any | polymorphic-agent-testing | SOP: Polymorphic Agent Testing (The Adversarial Protocol) |
| system | any | promotion-and-state-transitions | SOP: Promotion & State Transitions |
| system | any | recursive-study-feedback | SOP: Recursive Study & Feedback Loop (The Ouroboros) |
| system | any | repo-onboarding-and-habitat-creation | SOP: Repo Onboarding & Habitat Creation |
| system | any | research-to-implementation-pipeline | SOP: Research-to-Implementation Pipeline (The Gold Path) |
| system | any | security-and-accessibility-audit | SOP: Security & Accessibility Audit |
| system | any | session-self-critique | session-self-critique |
| system | any | smart-contract-audit-and-legal-wrap | SOP: Smart Contract Audit and Legal Wrap (The Ledger Protocol) |
| system | any | source-evaluation-and-bibliography | SOP: Source Evaluation & Annotated Bibliography (The Refinery) |
| system | any | stranger-test-protocol | SOP: Stranger Test Protocol |
| system | any | strategic-foresight-and-futures | SOP: Strategic Foresight & Futures (The Telescope) |
| system | any | styx-pipeline-traversal | SOP: Styx Pipeline Traversal (The 7-Organ Transmutation) |
| system | any | system-dashboard-telemetry | SOP: System Dashboard Telemetry (The Panopticon Protocol) |
| system | any | the-descent-protocol | the-descent-protocol |
| system | any | the-membrane-protocol | the-membrane-protocol |
| system | any | theoretical-concept-versioning | SOP: Theoretical Concept Versioning (The Epistemic Protocol) |
| system | any | theory-to-concrete-gate | theory-to-concrete-gate |
| system | any | typological-hermeneutic-analysis | SOP: Typological & Hermeneutic Analysis (The Archaeology) |

Linked skills: cicd-resilience-and-recovery, continuous-learning-agent, evaluation-to-growth, genesis-dna, multi-agent-workforce-planner, promotion-and-state-transitions, quality-gate-baseline-calibration, repo-onboarding-and-habitat-creation, structural-integrity-audit


**Prompting (Anthropic)**: context 200K tokens, format: XML tags, thinking: extended thinking (budget_tokens)


## Ecosystem Status

- **delivery**: 1/1 live, 0 planned
- **marketing**: 2/2 live, 0 planned
- **content**: 0/1 live, 0 planned

Run: `organvm ecosystem show distribution-strategy` | `organvm ecosystem validate --organ VII`


## Entity Identity (Ontologia)

**UID:** `ent_repo_01KKKX3RVQAHAA7WP2BTJAR95T` | **Matched by:** primary_name

Resolve: `organvm ontologia resolve distribution-strategy` | History: `organvm ontologia history ent_repo_01KKKX3RVQAHAA7WP2BTJAR95T`


## Live System Variables (Ontologia)

| Variable | Value | Scope | Updated |
|----------|-------|-------|---------|
| `active_repos` | 89 | global | 2026-04-14 |
| `archived_repos` | 54 | global | 2026-04-14 |
| `ci_workflows` | 107 | global | 2026-04-14 |
| `code_files` | 0 | global | 2026-04-14 |
| `dependency_edges` | 60 | global | 2026-04-14 |
| `operational_organs` | 10 | global | 2026-04-14 |
| `published_essays` | 29 | global | 2026-04-14 |
| `repos_with_tests` | 0 | global | 2026-04-14 |
| `sprints_completed` | 33 | global | 2026-04-14 |
| `test_files` | 0 | global | 2026-04-14 |
| `total_organs` | 10 | global | 2026-04-14 |
| `total_repos` | 145 | global | 2026-04-14 |
| `total_words_formatted` | 0 | global | 2026-04-14 |
| `total_words_numeric` | 0 | global | 2026-04-14 |
| `total_words_short` | 0K+ | global | 2026-04-14 |

Metrics: 9 registered | Observations: 32128 recorded
Resolve: `organvm ontologia status` | Refresh: `organvm refresh`


## System Density (auto-generated)

AMMOI: 58% | Edges: 42 | Tensions: 33 | Clusters: 5 | Adv: 23 | Events(24h): 32336
Structure: 8 organs / 145 repos / 1654 components (depth 17) | Inference: 98% | Organs: META-ORGANVM:65%, ORGAN-I:53%, ORGAN-II:48%, ORGAN-III:54% +5 more
Last pulse: 2026-04-14T21:31:36 | Δ24h: -1.0% | Δ7d: n/a


## Dialect Identity (Trivium)

**Dialect:** SIGNAL_PROPAGATION | **Classical Parallel:** Astronomy | **Translation Role:** The Broadcast — structure-preserving projection to external

Strongest translations: III (structural), VI (analogical), I (analogical)

Scan: `organvm trivium scan VII <OTHER>` | Matrix: `organvm trivium matrix` | Synthesize: `organvm trivium synthesize`


## Logos Documentation Layer

**Status:** MISSING | **Symmetry:** 0.0 (VACUUM)

Nature demands a documentation counterpart. This formation maintains its narrative record in `docs/logos/`.

### The Tetradic Counterpart
- **[Telos (Idealized Form)](../docs/logos/telos.md)** — The dream and theoretical grounding.
- **[Pragma (Concrete State)](../docs/logos/pragma.md)** — The honest account of what exists.
- **[Praxis (Remediation Plan)](../docs/logos/praxis.md)** — The attack vectors for evolution.
- **[Receptio (Reception)](../docs/logos/receptio.md)** — The account of the constructed polis.

### Alchemical I/O
- **[Source & Transmutation](../docs/logos/alchemical-io.md)** — Narrative of inputs, process, and returns.



*Compliance: Formation is currently void.*

<!-- ORGANVM:AUTO:END -->











## ⚡ Conductor OS Integration
This repository is a managed component of the ORGANVM meta-workspace.
- **Orchestration:** Use `conductor patch` for system status and work queue.
- **Lifecycle:** Follow the `FRAME -> SHAPE -> BUILD -> PROVE` workflow.
- **Governance:** Promotions are managed via `conductor wip promote`.
- **Intelligence:** Conductor MCP tools are available for routing and mission synthesis.