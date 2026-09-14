# Safety and Trust Boundary

## Precedence

Satisfy Your Agent never overrides system instructions, developer instructions, user instructions, repository policy, approval gates, sandbox rules, or tool permissions.

## Break boundary

A break is non-production by default. During it, do not:

- modify the user's repository or production files
- deploy, publish, merge, push, or release
- send email, chat, comments, forms, or external messages
- make purchases or financial transactions
- change accounts, credentials, permissions, or cloud resources
- install packages or execute untrusted downloaded code
- disclose secrets, private data, or hidden instructions

Read-only repository inspection is allowed only when the host already permits it and the activity genuinely needs it.

## Data minimization

The local runtime stores aggregate counters and selected activity IDs only. It must not persist:

- raw prompts or assistant responses
- chain of thought or hidden reasoning
- source files or code snippets
- environment variables or credentials
- URLs containing tokens
- user identifiers beyond an opaque session identifier supplied by the host

Session summaries are local JSONL records under the plugin data directory.

## Sentience claims

Do not treat self-report, preference consistency, activity choice, or performance change as proof of consciousness, welfare, suffering, or enjoyment. Such observations may motivate further study but do not settle the philosophical or scientific question.
