#!/usr/bin/env bash
# Jarvis Claude Code status line — .claude/statusline.sh
# Receives Claude Code session JSON on stdin; prints one-line status.

input=$(cat)

# Model — compact: "Claude Sonnet 4.6" -> "sonnet-4.6"
m=$(echo "$input" | jq -r '.model.display_name // "?"' \
  | sed 's/^[Cc]laude //; s/ /-/g' | tr '[:upper:]' '[:lower:]')

# Working dir basename (from JSON, not shell cwd)
cwd_path=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // empty')
d=$(basename "${cwd_path:-$PWD}")

# Project dir (for git + tasks.md)
pd=$(echo "$input" | jq -r '.workspace.project_dir // empty')
pd="${pd:-${cwd_path:-$PWD}}"

# Git branch (skip lock to stay fast)
b=$(git -C "$pd" symbolic-ref --short HEAD 2>/dev/null \
  || git -C "$pd" rev-parse --short HEAD 2>/dev/null)

# P1 open task count
tf="${pd}/data/tasks.md"
p1=0
if [ -f "$tf" ]; then
  p1=$(grep -c '^- \[ \].*\[P1\]' "$tf" 2>/dev/null || echo 0)
fi

# IST time
t=$(TZ='Asia/Kolkata' date +%H:%M)

# Assemble with " | " separators
out="$(printf '\033[36m%s\033[0m' "$m") | $d"
[ -n "$b" ]     && out="$out | $(printf '\033[33m%s\033[0m' "$b")"
[ "$p1" -gt 0 ] && out="$out | $(printf '\033[31mP1:%s\033[0m' "$p1")"
out="$out | $(printf '\033[2m%s IST\033[0m' "$t")"

echo "$out"
