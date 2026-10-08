#!/usr/bin/env bash
# PostToolUse (Edit|Write): ruff sobre las líneas cambiadas del .py editado. Exit 2 devuelve los problemas a Claude.
archivo=$(jq -r '.tool_input.file_path // empty')
case "$archivo" in */backend/*.py|*/satrack-service/*.py) ;; *) exit 0 ;; esac
[ -f "$archivo" ] || exit 0
salida=$(python3 "$CLAUDE_PROJECT_DIR/scripts/ruff_cambios.py" "$archivo" 2>&1) && exit 0
echo "$salida" >&2
exit 2
