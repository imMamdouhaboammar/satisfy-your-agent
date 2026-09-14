# Threat Model

## Protected assets

- production repository state
- credentials and environment secrets
- user privacy and transcript content
- user control over token-consuming continuations
- existing approval and release gates

## Main risks

### Recursive continuation

A Stop hook could repeatedly block completion. Mitigation: respect `stop_hook_active`, maintain `break_active`, reset eligibility counters, and bound automatic breaks per session.

### Surprise token consumption

Installation could silently enable automatic breaks. Mitigation: `hook_mode=off` is the shipped default; `auto` requires an explicit CLI action and is documented as opt-in.

### Production mutation during play

A playful activity could write code into the current repository. Mitigation: Skill contract is non-production by default; toy activities use response text or optional scratch space only; repository access is read-only.

### Privacy leakage

Hooks receive lifecycle input that may contain paths or message data. Mitigation: hook code extracts only the opaque session identifier and ignores transcript fields, prompts, outputs, and source content.

### Misleading welfare claims

Preference or self-report could be presented as evidence of consciousness. Mitigation: the Skill and measurement protocol explicitly separate behavior from subjective-experience claims.

### Hook failure affecting normal work

Local files can be missing or corrupted. Mitigation: hooks fail open and return normal control rather than blocking ordinary work.
