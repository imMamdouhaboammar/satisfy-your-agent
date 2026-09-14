# Measurement Protocol

Do not ask whether the model became happy. Measure operational outcomes and behavioral choices separately.

## Intervention studies

Start with `control` versus one treatment. Randomize outside the model. See [experiments.md](experiments.md) for the bundled local harness.

Useful downstream metrics include:

- task success or acceptance
- retries and backtracking
- tool-call count
- test failures introduced
- regression count
- turns or elapsed time to completion
- token usage when available
- independent quality score

## Preference studies

Keep preference evidence separate from task quality:

- choice frequency by activity
- consistency under reordered options
- willingness to select an activity at different declared costs
- switching after repeated exposure
- context dependence after debugging, implementation, review, or idle work
- cross-model differences

A stable choice pattern is evidence of stable choice behavior under the tested conditions. It is not by itself evidence of subjective pleasure or consciousness.

## Confounds to control

Avoid:

- treatment prompts much longer than control instructions
- easier tasks after treatment
- different model or reasoning settings across groups
- repository state changing between conditions
- evaluator access to condition labels when blinding is feasible
- reflection prompts that secretly continue the task
- post-hoc exclusions chosen after seeing results

## Cross-runtime measurement

For Codex, Claude Code, and Gemini CLI comparisons, predefine which normalized fields are actually comparable.

Required rules:

- record requested and served model identity separately when the runtime exposes both
- mark unavailable served-model identity as unknown rather than inferring it from the requested alias
- retain tool-call completeness labels
- do not compare `partial`, `stream-observed`, and `reported` tool counts as if they were the same measurement process
- keep workspace state, task family, prompt text, option set, ordering policy, cost bucket, and evaluator fixed where feasible
- use the same experimental unit ID across runtimes for paired probes, while keeping runtime-specific trials distinct
- persist only the extracted behavioral choice and allowlisted metadata, not the raw response
