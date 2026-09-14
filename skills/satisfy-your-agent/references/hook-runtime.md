# Hook Runtime

The plugin bundles optional Codex lifecycle hooks. Hooks are a transport mechanism, not the Skill itself.

## Default

`hook_mode` is `off`. Installation alone must not spend extra model turns or create session telemetry files.

## Configuration

The runtime looks for `config.json` in the plugin data directory. Use the bundled CLI instead of editing it manually:

Resolve the installed Skill directory as `SYA_SKILL_DIR`, then run:

```bash
python3 "$SYA_SKILL_DIR/scripts/sya.py" status
python3 "$SYA_SKILL_DIR/scripts/sya.py" arm --mode observe
python3 "$SYA_SKILL_DIR/scripts/sya.py" arm --mode suggest
python3 "$SYA_SKILL_DIR/scripts/sya.py" arm --mode auto
python3 "$SYA_SKILL_DIR/scripts/sya.py" arm --mode off
```

`auto` should be enabled only after explicit user authorization.

## Hook roles

- `SessionStart`: initialize an opaque local session record
- `PostToolUse`: increment an aggregate local tool-call counter
- `Stop`: decide whether an eligible `suggest` or `auto` continuation should occur
- `SessionEnd`: append a compact aggregate summary and remove volatile session state

## Loop prevention

The Stop hook checks the host's `stop_hook_active` flag and its own state. A break continuation cannot trigger another break continuation. Eligibility counters reset after an offer or automatic break.

## Storage

Use `PLUGIN_DATA` when the plugin host provides it. The manual CLI falls back to a user-local data directory. Runtime state is never stored in the working repository by default.
