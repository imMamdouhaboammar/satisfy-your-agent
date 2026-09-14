# Security Policy

## Scope

Satisfy Your Agent is a local-only agent skill and experiment harness. It does not:

- access remote services or APIs
- store credentials, tokens, or secrets
- persist raw prompts, responses, or source code
- make network requests

The runtime stores only aggregate counters, hashed unit IDs, activity IDs, condition IDs, and structured metrics.

## Reporting a vulnerability

If you discover a security issue, please report it responsibly:

1. **Do not** open a public issue
2. Use [GitHub Security Advisories](https://github.com/imMamdouhaboammar/satisfy-your-agent/security/advisories/new) to report the vulnerability privately
3. Include steps to reproduce, expected behavior, and actual behavior

You should receive a response within 72 hours.

## install.sh considerations

The `install.sh` script copies the skill directory to agent-specific locations (`~/.claude/skills/`, `~/.gemini/config/skills/`, `~/.codex/skills/`, `~/.cursor/skills/`, `~/.agents/skills/`). It:

- runs only on the local filesystem
- does not download anything from the network
- does not modify system files or require elevated privileges
- uses `rm -rf` on the target skill directory before copying (limited to the named skill path)

Review the script before running it, especially if you have custom content in those directories.

## Supported versions

| Version | Supported |
| --- | --- |
| 0.4.x | Yes |
| 0.3.x | Security fixes only |
| < 0.3 | No |
