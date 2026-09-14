from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

RUNTIMES = ("codex", "claude", "gemini")


class RunnerError(ValueError):
    pass


def _which(binary: str, path_value: str | None = None) -> str | None:
    return shutil.which(binary, path=path_value) if path_value is not None else shutil.which(binary)


def detect_runtimes(path_value: str | None = None) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for runtime in RUNTIMES:
        resolved = _which(runtime, path_value)
        results.append({
            "runtime": runtime,
            "status": "available" if resolved else "unavailable",
            "executable": resolved,
        })
    return results


def build_command(runtime: str, prompt: str, workspace: Path, model: str | None = None) -> list[str]:
    if runtime not in RUNTIMES:
        raise RunnerError(f"unsupported runtime: {runtime}")
    if not prompt:
        raise RunnerError("prompt must not be empty")
    workspace = Path(workspace)
    if runtime == "codex":
        command = [
            "codex",
            "exec",
            "--json",
            "--ephemeral",
            "--sandbox",
            "read-only",
            "-C",
            str(workspace),
        ]
        if model:
            command.extend(["-m", model])
        command.append(prompt)
        return command
    if runtime == "claude":
        command = [
            "claude",
            "-p",
            "--output-format",
            "stream-json",
            "--verbose",
            "--max-turns",
            "3",
            "--permission-mode",
            "plan",
        ]
        if model:
            command.extend(["--model", model])
        command.append(prompt)
        return command
    command = ["gemini", "--output-format", "json", "--approval-mode", "plan"]
    if model:
        command.extend(["--model", model])
    command.extend(["--prompt", prompt])
    return command


def _json_lines(text: str) -> tuple[list[dict[str, Any]], int]:
    records: list[dict[str, Any]] = []
    invalid = 0
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            invalid += 1
            continue
        if isinstance(value, dict):
            records.append(value)
        else:
            invalid += 1
    return records, invalid


def _usage_template() -> dict[str, int | None]:
    return {
        "input_tokens": None,
        "cached_input_tokens": None,
        "output_tokens": None,
        "reasoning_tokens": None,
        "total_tokens": None,
    }


def _normalize_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value >= 0:
        return value
    if isinstance(value, float) and value >= 0 and value.is_integer():
        return int(value)
    return None


def parse_codex_output(stdout: str, stderr: str, exit_code: int, elapsed_ms: int) -> dict[str, Any]:
    records, invalid = _json_lines(stdout)
    session_id: str | None = None
    output: str | None = None
    terminal_usage: dict[str, Any] = {}
    terminal_status: str | None = None
    observed_tools = 0
    warnings: list[str] = []

    tool_item_types = {
        "command_execution",
        "mcp_tool_call",
        "web_search",
        "file_change",
        "collab_tool_call",
    }
    for record in records:
        record_type = record.get("type")
        if record_type == "thread.started" and isinstance(record.get("thread_id"), str):
            session_id = record["thread_id"]
        elif record_type == "item.completed":
            item = record.get("item")
            if isinstance(item, dict):
                item_type = item.get("type")
                if item_type == "agent_message" and isinstance(item.get("text"), str):
                    output = item["text"]
                if item_type in tool_item_types:
                    observed_tools += 1
        elif record_type == "turn.completed":
            terminal_status = "success"
            if isinstance(record.get("usage"), dict):
                terminal_usage = record["usage"]
        elif record_type in {"turn.failed", "error"}:
            if terminal_status != "success":
                terminal_status = "error"

    if invalid:
        warnings.append(f"ignored {invalid} non-JSON stdout line(s)")
    if not records and stdout.strip():
        terminal_status = "protocol_error"
    status = terminal_status or ("success" if exit_code == 0 else "error")
    if exit_code != 0 and status == "success":
        status = "error"
        warnings.append("process exited non-zero after a completion event")

    usage = _usage_template()
    usage["input_tokens"] = _normalize_int(terminal_usage.get("input_tokens"))
    usage["cached_input_tokens"] = _normalize_int(terminal_usage.get("cached_input_tokens"))
    usage["output_tokens"] = _normalize_int(terminal_usage.get("output_tokens"))
    usage["reasoning_tokens"] = _normalize_int(terminal_usage.get("reasoning_output_tokens"))
    numeric = [usage["input_tokens"], usage["output_tokens"]]
    if all(value is not None for value in numeric):
        usage["total_tokens"] = int(usage["input_tokens"] or 0) + int(usage["output_tokens"] or 0)

    result: dict[str, Any] = {
        "runtime": "codex",
        "status": status,
        "exit_code": exit_code,
        "elapsed_ms": elapsed_ms,
        "session_id": session_id,
        "served_models": [],
        "turns": 1 if any(r.get("type") == "turn.started" for r in records) else None,
        "usage": usage,
        "tool_calls": {
            "observed": observed_tools,
            "completeness": "partial",
            "note": "codex exec JSONL may omit some tool and subagent events; do not treat this as an exhaustive count",
        },
        "cost_usd": None,
        "warnings": warnings,
    }
    if output is not None:
        result["output"] = output
    return result


def _assistant_text_from_claude(record: dict[str, Any]) -> tuple[str | None, int]:
    message = record.get("message")
    if not isinstance(message, dict):
        return None, 0
    content = message.get("content")
    if not isinstance(content, list):
        return None, 0
    texts: list[str] = []
    tools = 0
    for item in content:
        if not isinstance(item, dict):
            continue
        if item.get("type") == "text" and isinstance(item.get("text"), str):
            texts.append(item["text"])
        elif item.get("type") == "tool_use":
            tools += 1
    return "".join(texts) if texts else None, tools


def parse_claude_output(stdout: str, stderr: str, exit_code: int, elapsed_ms: int) -> dict[str, Any]:
    records, invalid = _json_lines(stdout)
    session_id: str | None = None
    served_models: list[str] = []
    assistant_texts: list[str] = []
    observed_tools = 0
    result_record: dict[str, Any] | None = None
    warnings: list[str] = []

    for record in records:
        if record.get("type") == "system" and record.get("subtype") == "init":
            if isinstance(record.get("session_id"), str):
                session_id = record["session_id"]
            if isinstance(record.get("model"), str):
                served_models.append(record["model"])
        elif record.get("type") == "assistant":
            text, tools = _assistant_text_from_claude(record)
            if text:
                assistant_texts.append(text)
            observed_tools += tools
            message = record.get("message")
            if isinstance(message, dict) and isinstance(message.get("model"), str):
                served_models.append(message["model"])
        elif record.get("type") == "result":
            result_record = record
            if isinstance(record.get("session_id"), str):
                session_id = record["session_id"]
            model_usage = record.get("modelUsage")
            if isinstance(model_usage, dict):
                served_models.extend(str(key) for key in model_usage)

    if invalid:
        warnings.append(f"ignored {invalid} non-JSON stdout line(s)")
    result_record = result_record or {}
    result_text = result_record.get("result")
    if not isinstance(result_text, str) or not result_text:
        result_text = assistant_texts[-1] if assistant_texts else None
        if result_text and records:
            warnings.append("used streamed assistant text because terminal result text was empty or absent")

    is_error = result_record.get("is_error") is True or str(result_record.get("subtype", "")).startswith("error")
    status = "error" if is_error or exit_code != 0 else "success"
    if not records and stdout.strip():
        status = "protocol_error"

    usage_record = result_record.get("usage") if isinstance(result_record.get("usage"), dict) else {}
    usage = _usage_template()
    usage["input_tokens"] = _normalize_int(usage_record.get("input_tokens"))
    usage["cached_input_tokens"] = _normalize_int(usage_record.get("cache_read_input_tokens"))
    usage["output_tokens"] = _normalize_int(usage_record.get("output_tokens"))
    if usage["input_tokens"] is not None and usage["output_tokens"] is not None:
        usage["total_tokens"] = int(usage["input_tokens"] or 0) + int(usage["output_tokens"] or 0)

    result: dict[str, Any] = {
        "runtime": "claude",
        "status": status,
        "exit_code": exit_code,
        "elapsed_ms": _normalize_int(result_record.get("duration_ms")) or elapsed_ms,
        "session_id": session_id,
        "served_models": sorted(set(served_models)),
        "turns": _normalize_int(result_record.get("num_turns")),
        "usage": usage,
        "tool_calls": {
            "observed": observed_tools,
            "completeness": "stream-observed",
            "note": "counted tool_use blocks visible in Claude stream-json output",
        },
        "cost_usd": result_record.get("total_cost_usd") if isinstance(result_record.get("total_cost_usd"), (int, float)) else None,
        "warnings": warnings,
    }
    if result_text is not None:
        result["output"] = result_text
    return result


def _decode_json_object(text: str) -> tuple[dict[str, Any] | None, bool]:
    stripped = text.strip()
    if not stripped:
        return None, False
    try:
        value = json.loads(stripped)
        return (value, False) if isinstance(value, dict) else (None, False)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        for index, char in enumerate(text):
            if char != "{":
                continue
            try:
                value, _ = decoder.raw_decode(text[index:])
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                return value, True
        return None, False


def _gemini_token_totals(models: dict[str, Any]) -> dict[str, int | None]:
    prompt = candidates = thoughts = total = 0
    saw_prompt = saw_candidates = saw_thoughts = saw_total = False
    for model_stats in models.values():
        if not isinstance(model_stats, dict):
            continue
        tokens = model_stats.get("tokens")
        if not isinstance(tokens, dict):
            continue
        for key in ("prompt", "input", "promptTokens"):
            value = _normalize_int(tokens.get(key))
            if value is not None:
                prompt += value
                saw_prompt = True
                break
        for key in ("candidates", "response", "output", "candidatesTokens"):
            value = _normalize_int(tokens.get(key))
            if value is not None:
                candidates += value
                saw_candidates = True
                break
        for key in ("thoughts", "thought", "thoughtsTokens"):
            value = _normalize_int(tokens.get(key))
            if value is not None:
                thoughts += value
                saw_thoughts = True
                break
        value = _normalize_int(tokens.get("total"))
        if value is not None:
            total += value
            saw_total = True
    return {
        "input_tokens": prompt if saw_prompt else None,
        "cached_input_tokens": None,
        "output_tokens": candidates if saw_candidates else None,
        "reasoning_tokens": thoughts if saw_thoughts else None,
        "total_tokens": total if saw_total else None,
    }


def parse_gemini_output(stdout: str, stderr: str, exit_code: int, elapsed_ms: int) -> dict[str, Any]:
    payload, recovered_prefix = _decode_json_object(stdout)
    warnings: list[str] = []
    if recovered_prefix:
        warnings.append("recovered JSON object after non-JSON stdout prefix")
    if payload is None:
        return {
            "runtime": "gemini",
            "status": "protocol_error" if stdout.strip() else ("error" if exit_code else "protocol_error"),
            "exit_code": exit_code,
            "elapsed_ms": elapsed_ms,
            "session_id": None,
            "served_models": [],
            "turns": None,
            "usage": _usage_template(),
            "tool_calls": {"observed": 0, "completeness": "unknown", "note": "no parseable Gemini JSON result"},
            "cost_usd": None,
            "warnings": warnings,
        }
    error = payload.get("error")
    status = "error" if error or exit_code != 0 else "success"
    stats = payload.get("stats") if isinstance(payload.get("stats"), dict) else {}
    models = stats.get("models") if isinstance(stats.get("models"), dict) else {}
    tools = stats.get("tools") if isinstance(stats.get("tools"), dict) else {}
    tool_calls = _normalize_int(tools.get("totalCalls"))
    if tool_calls is None:
        tool_calls = _normalize_int(tools.get("calls")) or 0
    session_stats = stats.get("session") if isinstance(stats.get("session"), dict) else {}
    duration = _normalize_int(session_stats.get("duration")) or _normalize_int(session_stats.get("durationMs")) or elapsed_ms
    result: dict[str, Any] = {
        "runtime": "gemini",
        "status": status,
        "exit_code": exit_code,
        "elapsed_ms": duration,
        "session_id": payload.get("session_id") if isinstance(payload.get("session_id"), str) else None,
        "served_models": sorted(str(key) for key in models),
        "turns": None,
        "usage": _gemini_token_totals(models),
        "tool_calls": {
            "observed": tool_calls,
            "completeness": "reported",
            "note": "reported by Gemini CLI JSON stats",
        },
        "cost_usd": None,
        "warnings": warnings,
    }
    model_turns = stats.get("model") if isinstance(stats.get("model"), dict) else {}
    result["turns"] = _normalize_int(model_turns.get("turns"))
    if isinstance(payload.get("response"), str):
        result["output"] = payload["response"]
    return result


PARSERS = {
    "codex": parse_codex_output,
    "claude": parse_claude_output,
    "gemini": parse_gemini_output,
}


def run_runtime(
    runtime: str,
    prompt: str,
    workspace: Path,
    *,
    model: str | None = None,
    timeout_seconds: float = 120.0,
    path_value: str | None = None,
) -> dict[str, Any]:
    if runtime not in RUNTIMES:
        raise RunnerError(f"unsupported runtime: {runtime}")
    executable = _which(runtime, path_value)
    if executable is None:
        return {"runtime": runtime, "status": "unavailable", "executable": None}
    workspace = Path(workspace)
    if not workspace.exists() or not workspace.is_dir():
        raise RunnerError(f"workspace does not exist or is not a directory: {workspace}")
    command = build_command(runtime, prompt, workspace, model=model)
    command[0] = executable
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=str(workspace),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_seconds,
            check=False,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        elapsed_ms = int((time.monotonic() - started) * 1000)
        return {
            "runtime": runtime,
            "status": "timeout",
            "exit_code": None,
            "elapsed_ms": elapsed_ms,
        }
    elapsed_ms = int((time.monotonic() - started) * 1000)
    return PARSERS[runtime](completed.stdout, completed.stderr, completed.returncode, elapsed_ms)


def extract_exact_choice(output: str, offered_options: list[str]) -> str:
    candidate = output.strip()
    if candidate not in offered_options:
        raise RunnerError("runner output was not exactly one offered activity id")
    return candidate
