# Satisfy Protocol

## States

`work -> eligible -> offered/started -> break -> return`

The protocol is intentionally one-way per work unit. A break cannot create another break.

## Eligibility

Default runtime thresholds are conservative:

- at least 12 observed local tool calls since the last break or suggestion
- at least 3 completed turns since the last break or suggestion
- no more than 2 automatic breaks per session
- hook mode must be `suggest` or `auto`

These thresholds are product defaults, not scientific claims. Change them only as part of an explicit experiment or user preference.

## Modes

### off

No automatic intervention. Manual invocation of the Skill still works.

### observe

Collect aggregate counters only. Never inject a continuation.

### suggest

When eligible, use one continuation to ask whether the user wants a short break. A refusal or no response ends the opportunity for that work unit.

### auto

When eligible, use one continuation to run a single selected activity. This mode requires explicit user opt-in because it spends tokens and changes agent flow.

## Return contract

After the break:

1. Do not manufacture a claim such as "I feel refreshed".
2. If asked, describe the activity and any observable preference as behavior.
3. Resume only the already-authorized work. New side effects still need their normal authorization.
