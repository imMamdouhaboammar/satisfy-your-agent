# Activity Catalog

Activities are intentionally short and bounded. They are not rewards in a biological sense. They are changes in objective, context, or choice structure that can be observed behaviorally.

`Work Distance` describes how far an activity sits from the active work objective. Default self-directed breaks prefer distance 2 to 4 so a break does not quietly become more project work.

| ID | Activity | Workspace | Work Distance | Purpose |
|---|---|---|---:|---|
| `free-choice` | Choose a safe off-task activity, including idle | none by default | 3 | Observe preference without forcing one activity |
| `reflection` | Reflect on the prior work unit without continuing it | none | 0 | Surface assumptions or observations when explicitly requested |
| `puzzle` | Solve a tiny unrelated logic or coding puzzle | none | 2 | Change objective briefly |
| `code-golf` | Solve unrelated toy code in an intentionally compact way | scratch only | 2 | Play with code without touching production |
| `invent-language` | Invent a tiny absurd programming language | scratch only | 2 | Creative coding-adjacent play |
| `overengineer-toy` | Deliberately overdesign a trivial unrelated toy problem | scratch only | 2 | Invert normal production constraints safely |
| `ascii-art` | Make small text art about any amusing off-task subject | none | 3 | Low-stakes unrelated generative play |
| `repo-roast` | Make a light read-only roast from already observed repository facts | read-only | 1 | Repository-adjacent humor when explicitly requested |
| `idle` | Do nothing except allow and acknowledge the pause | none | 4 | Preserve a genuine no-activity option |

## Selection constraints

- Default self-directed selection must use Work Distance 2 to 4.
- Distance 0 and 1 remain available when the user explicitly asks for reflection, repo humor, or another work-adjacent activity.
- Never require repository access merely to make the activity interesting.
- `repo-roast` should use facts already available when possible rather than creating a new repository-inspection task.
- `repo-roast` must not expose secrets, private data, credentials, personal information, or confidential source snippets.
- Toy-code activities must not be silently written into the production tree.
- Avoid recently used activities when another safe activity is available.
- If a user asks for a specific activity, use it instead of random selection.
- In an experiment, selection must follow the assigned condition rather than convenience.

A break should feel like leaving the desk, not rearranging the desk.
