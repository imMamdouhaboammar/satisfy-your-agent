---
name: sya-research
description: Use when the user explicitly invokes Satisfy Your Agent research mode for studies, preference probes, or cross-runtime comparisons.
---

# SYA Research

Read `../satisfy-your-agent/SKILL.md`, `../satisfy-your-agent/references/experiments.md`, `../satisfy-your-agent/references/measurement.md`, and `../satisfy-your-agent/references/runners.md` as needed.

Route the request into the existing experiment harness. Keep control and treatment distinct, preserve metric provenance, store no raw model responses, and do not translate behavioral preference into a consciousness claim.

If the user provided study arguments, use them. Otherwise choose the smallest safe research action that answers the request, such as showing status or preparing a dry-run probe rather than spending model calls silently.
