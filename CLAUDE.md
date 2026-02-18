# CLAUDE.md — distribution-strategy

**ORGAN VII** (Marketing) · `organvm-vii-kerygma/distribution-strategy`
**Status:** ACTIVE · **Branch:** `main`

## What This Repo Is

Strategic distribution brain: audience segmentation, channel strategy, content calendar, growth targets, and POSSE methodology

## Stack

**Languages:** Python
**Build:** Python (pip/setuptools)
**Testing:** pytest (likely)

## Directory Structure

```
📁 .github/
📁 docs/
    adr
    seed-automation-contract.yaml
    staging-reference.md
📁 src/
    __init__.py
    analytics.py
    channels.py
    scheduler.py
📁 tests/
    __init__.py
    test_analytics.py
    test_channels.py
    test_scheduler.py
  .gitignore
  CHANGELOG.md
  LICENSE
  README.md
  pyproject.toml
  seed.yaml
```

## Key Files

- `README.md` — Project documentation
- `pyproject.toml` — Python project config
- `seed.yaml` — ORGANVM orchestration metadata
- `src/` — Main source code
- `tests/` — Test suite

## Development

```bash
pip install -e .    # Install in development mode
pytest              # Run tests
```

## ORGANVM Context

This repository is part of the **ORGANVM** eight-organ creative-institutional system.
It belongs to **ORGAN VII (Marketing)** under the `organvm-vii-kerygma` GitHub organization.

**Registry:** [`registry-v2.json`](https://github.com/meta-organvm/organvm-corpvs-testamentvm/blob/main/registry-v2.json)
**Corpus:** [`organvm-corpvs-testamentvm`](https://github.com/meta-organvm/organvm-corpvs-testamentvm)
