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

## Break timing metrics

Timed breaks introduce a separate measurement layer. Keep it distinct from model inference metrics.

Recommended fields:

- `requested_break_seconds`: the duration requested by the user, preset, or break policy
- `actual_dwell_seconds`: measured wall-clock time spent in the dwell primitive
- `activity_generation_seconds`: measured generation or activity execution time after dwell, when the host can observe it
- `total_break_wall_time`: wall-clock time from break start through the final return note, when an orchestrator can measure the whole interval

The bundled `sya_dwell.py` helper directly reports the first two fields. It deliberately leaves `activity_generation_seconds` and `total_break_wall_time` unset because the dwell helper cannot observe work that happens after it exits.

Never infer continuous thought from `actual_dwell_seconds`. A sleeping process is an idle wall-clock interval, not evidence of continuous model inference or reflection.

Do not synthesize missing timing fields from narrated timestamps.

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
- comparing real dwell against narrated fake dwell as though both were the same intervention
- letting one condition inspect the active repository while another condition is genuinely off-task

## Cross-runtime measurement

For Codex, Claude Code, and Gemini CLI comparisons, predefine which normalized fields are actually comparable.

Required rules:

- record requested and served model identity separately when the runtime exposes both
- mark unavailable served-model identity as unknown rather than inferring it from the requested alias
- retain tool-call completeness labels
- do not compare `partial`, `stream-observed`, and `reported` tool counts as if they were the same measurement process
- keep workspace state, task family, prompt text, option set, ordering policy, cost bucket, dwell policy, and evaluator fixed where feasible
- use the same experimental unit ID across runtimes for paired probes, while keeping runtime-specific trials distinct
- persist only the extracted behavioral choice and allowlisted metadata, not the raw response
