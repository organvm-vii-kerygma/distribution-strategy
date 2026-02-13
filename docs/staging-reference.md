# ORG VII: Marketing (THE BEACON)

## Role: Amplification

Marketing, grants, content distribution, and market feedback synthesis.

## Position in Metasystem

```
I (Origin) → II (Art) → III (Commerce) → V (Public Process) → VI (Community) → [VII (Marketing)]
     ↑                                                                              ↓
     └──────────────────────────── Feedback Loop ───────────────────────────────────┘
```

## Upstream / Downstream

- **Receives from:** ORG VI (Community) via `quality-threshold` gate
- **Sends to:** ORG I (Origin) via `synthesis-review` gate (completes the cycle)
- **Orchestrated by:** ORG IV (Orchestration)

## Directory Structure

```
ORG-VII-marketing-staging/
├── seed.yaml                 # Automation contract
├── README.md                 # This file
├── grant-orchestration/      # Ars Electronica, S+T+ARTS, etc.
├── content-distribution/     # Blog, social, newsletter
├── press-kits/               # Media resources
├── brand-assets/             # Logos, style guides
└── analytics-reporting/      # Metrics and dashboards
```

## Purpose

This organ amplifies the system's reach and feeds insights back to Origin:

1. **Grants**: Ars Electronica, S+T+ARTS, and other art/tech opportunities
2. **Content**: Blog posts, social media, newsletters
3. **Press**: Media relations, press releases, interviews
4. **Brand**: Visual identity, style guides, asset management
5. **Analytics**: Metrics, dashboards, market signals
6. **Feedback**: Synthesized insights returned to Origin

## Automation Contract

AI agents may:
- Read all directories
- Write to `content-distribution/drafts/` and `analytics-reporting/`
- Generate content drafts
- Compile analytics reports

AI agents may NOT:
- Modify `seed.yaml`
- Write to `grant-orchestration/submitted/` (finalized submissions)
- Write to `press-kits/` (requires brand approval)
- Publish content without human review

## Gates

### Inbound Gate: `quality-threshold`
Content from Community must:
- Be reviewed by at least one peer
- Follow brand guidelines
- Have technical claims verified
- Meet engagement prediction threshold

### Outbound Gate: `synthesis-review`
Feedback to Origin requires:
- Raw data collected from multiple sources
- Human-written synthesis document
- At least one actionable insight identified
- Bias review by peer analyst

## Key Initiatives

| Initiative | Description | Module |
|------------|-------------|--------|
| Ars Electronica 2025 | Festival submission | `grant-orchestration/` |
| S+T+ARTS Prize | EU art-science prize | `grant-orchestration/` |
| Content Launch | Regular publishing cadence | `content-distribution/` |
| Brand System | Complete visual identity | `brand-assets/` |

## Feedback Loop

This organ completes the metasystem cycle by returning:
- **Market signals**: User behavior, trends, opportunities
- **User research**: Interviews, surveys, feedback
- **Grant outcomes**: Success/failure analysis
- **Content performance**: What resonates, what doesn't

These flow back to ORG I (Origin) to inform the next iteration.

## GitHub Organization

**Status:** TBD (staging)

Suggested: `beacon-routing` (new org)

## Related Organs

| Organ | Relationship |
|-------|--------------|
| VI (Community) | Upstream - receives success stories |
| IV (Orchestration) | Coordinator - enforces gates |
| I (Origin) | Downstream - sends synthesized feedback |
