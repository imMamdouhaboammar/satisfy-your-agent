# Contributing to Satisfy Your Agent

Found a better break activity, a measurement flaw, a parser edge case, or a reason this entire premise is nonsense? All four are useful.

## Getting started

Clone and verify:

```bash
git clone https://github.com/imMamdouhaboammar/satisfy-your-agent.git
cd satisfy-your-agent
python3 scripts/verify.py
python3 -m unittest discover -s tests -v
```

No third-party Python packages are required.

## What you can contribute

### New break activities

Activities live in `skills/satisfy-your-agent/references/activities.md`. A good activity is:

- bounded (one short interaction)
- sandboxed (no production mutation)
- observable (the choice and duration can be recorded)
- distinct from existing activities

Add the activity to the catalog, update the CLI if it needs special handling, and include a test.

### Study designs

Study fixtures live in `evals/studies/`. Follow the schema in existing fixtures. Document the hypothesis, conditions, and expected measurements.

### Parser improvements

Runner parsers in `skills/satisfy-your-agent/scripts/sya_runners.py` handle Codex JSONL, Claude stream-json, and Gemini JSON. If you find a new output format or edge case, add a fixture to `evals/runners/` and a test to `tests/test_runners.py`.

### Documentation fixes

Typos, unclear sections, and measurement claims that overreach the experimental design are all fair game.

## Pull request checklist

Before opening a PR:

- [ ] `python3 scripts/verify.py` exits with `VERIFY_OK`
- [ ] `python3 -m unittest discover -s tests -v` passes all tests
- [ ] `python3 evals/metric_pack/satisfy_metric_pack.py .` passes all checks
- [ ] No raw prompts, transcripts, secrets, or private file contents in commits
- [ ] New behavior has at least one test
- [ ] Commit messages follow conventional format: `feat:`, `fix:`, `docs:`, `test:`

## Code style

- Python: stdlib only, no third-party dependencies
- Keep scripts dependency-free so they run in any sandbox
- One term per concept (see the skill's terminology)

## Questions?

Open an issue. The bar for discussion is low. The bar for merging untested changes is high.
