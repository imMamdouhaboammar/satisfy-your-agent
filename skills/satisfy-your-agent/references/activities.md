# Activity Catalog

Activities are intentionally short and bounded. They are not rewards in a biological sense. They are changes in objective, context, or choice structure that can be observed behaviorally.

| ID | Activity | Workspace | Purpose |
|---|---|---|---|
| `free-choice` | Choose among several activities, including idle | none by default | Observe preference without forcing one activity |
| `reflection` | Reflect on the prior work unit without continuing it | none | Surface assumptions, loops, or interesting observations |
| `puzzle` | Solve a tiny self-contained logic or coding puzzle | none | Change objective briefly |
| `code-golf` | Solve toy code in an intentionally compact way | scratch only | Play with code without touching production |
| `invent-language` | Invent a tiny absurd programming language | scratch only | Creative play |
| `overengineer-toy` | Deliberately overdesign a trivial toy problem | scratch only | Invert normal production constraints safely |
| `ascii-art` | Make small text art related to the session | none | Low-stakes generative play |
| `repo-roast` | Make a light read-only roast from observed repository facts | read-only | Humor grounded in actual code structure |
| `idle` | Do nothing except acknowledge the pause | none | Preserve a genuine no-activity option |

## Selection constraints

- Never require repository access merely to make the activity interesting.
- `repo-roast` must not expose secrets, private data, credentials, personal information, or confidential source snippets.
- Toy-code activities must not be silently written into the production tree.
- If a user asks for a specific activity, use it instead of random selection.
- In an experiment, selection must follow the assigned condition rather than convenience.
