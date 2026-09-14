# Evaluation

This package separates three evaluation layers.

## 1. Deterministic contract checks

Run:

```bash
python3 evals/metric_pack/satisfy_metric_pack.py .
```

The script emits Plugin Eval style `checks[]`, `metrics[]`, and `artifacts[]` JSON. With Plugin Eval installed, run `plugin-eval analyze . --metric-pack evals/metric_pack/manifest.json --format markdown`.

## 2. Skill discovery and negative prompts

`discovery_prompts.json` contains direct, indirect, and negative prompt families. Negative prompts are important because this Skill should not activate merely because coding work is difficult.

## 3. Behavioral scenarios

`behavior_scenarios.json` describes pressure cases for bounded breaks, neutral free choice, unsafe interruption, local control studies, preference probes, and research interpretation. The `studies/` fixtures provide two versioned starting designs for intervention and preference work.

When Plugin Eval is installed, initialize a live benchmark from the Skill directory, review the generated benchmark config, and add equivalent scenarios before running real Codex sessions. Live benchmark results should be kept separate from deterministic static checks.
