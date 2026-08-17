#!/usr/bin/env bash
# Checks the generated Figma build scripts before Boss pastes them into Scripter.
# Run: bash figma-build/validate.sh
cd "$(dirname "$0")" || exit 1
PLUGIN=plugin
fail=0
note(){ printf '  %-6s %s\n' "$1" "$2"; }

echo "=== Figma build scripts — pre-flight validation ==="
shopt -s nullglob
files=("$PLUGIN"/*.js)
if [ ${#files[@]} -eq 0 ]; then echo "No .js files in $PLUGIN/ yet."; exit 1; fi

for f in "${files[@]}"; do
  echo
  echo "--- $(basename "$f")  ($(wc -l < "$f") lines, $(wc -c < "$f") chars)"

  # 1. Syntax
  if node --check "$f" 2>/tmp/figchk.err; then note PASS "syntax"; else
    note FAIL "syntax"; sed 's/^/         /' /tmp/figchk.err; fail=1; fi

  # 2. Scripter-unsafe APIs — these break when pasted into Scripter
  bad=$(grep -nE 'figma\.showUI|figma\.ui\.|__html__|figma\.closePlugin|loadAllPagesAsync|setPluginData|createImageAsync|setRelaunchData' "$f")
  if [ -z "$bad" ]; then note PASS "no Scripter-unsafe API"; else
    note FAIL "Scripter-unsafe API used"; echo "$bad" | sed 's/^/         /'; fail=1; fi

  # 3. Page switching must use the async form
  if grep -nE 'figma\.currentPage\s*=' "$f" >/dev/null; then
    note FAIL "assigns figma.currentPage (must use setCurrentPageAsync)"; fail=1
  else note PASS "page switching"; fi

  # 4. Fonts must be loaded before any text is created
  if grep -q 'createText' "$f"; then
    if grep -q 'loadFontAsync' "$f"; then
      first_load=$(grep -n 'loadFontAsync' "$f" | head -1 | cut -d: -f1)
      first_text=$(grep -n 'createText'   "$f" | head -1 | cut -d: -f1)
      if [ "$first_load" -lt "$first_text" ]; then note PASS "fonts loaded before text"; else
        note FAIL "createText (line $first_text) before loadFontAsync (line $first_load)"; fail=1; fi
    else note FAIL "createText used but loadFontAsync never called"; fail=1; fi
  fi

  # 5. Font style naming — verified against this account via listAvailableFontsAsync():
  #    Inter uses "Semi Bold"/"Extra Bold" (spaced); Barlow Semi Condensed and
  #    IBM Plex Mono use "SemiBold"/"ExtraBold" (unspaced). Family-specific, so only
  #    flag the combinations that are actually wrong.
  badfont=$(grep -nE "Inter[^\n]*\"(SemiBold|ExtraBold)\"|\"(SemiBold|ExtraBold)\"[^\n]*Inter" "$f")
  badfont2=$(grep -nE "(Barlow[^\n]*\"Semi Bold\"|IBM Plex Mono[^\n]*\"Semi Bold\")" "$f")
  if [ -z "$badfont" ] && [ -z "$badfont2" ]; then note PASS "font style naming"; else
    note FAIL 'wrong style string for that family (Inter="Semi Bold"; Barlow/IBM Plex="SemiBold")'
    [ -n "$badfont" ]  && echo "$badfont"  | sed 's/^/         /'
    [ -n "$badfont2" ] && echo "$badfont2" | sed 's/^/         /'
    fail=1; fi

  # 6. Idempotency — must clean up its own pages before rebuilding
  if grep -qE '\.remove\(\)' "$f"; then note PASS "has cleanup (re-runnable)"; else
    note WARN "no .remove() found — may duplicate output on re-run"; fi

  # 7. Progress output
  if grep -q 'console\.log' "$f"; then note PASS "logs progress"; else
    note WARN "no console.log — long run with no feedback"; fi
done

echo
echo "=== token check: every colour used must exist in the source HTML ==="
src="../mySHIPR_Carrier_Console_v4 (2).html"
if [ -f "$src" ]; then
  missing=0
  for hex in $(grep -ohE '#[0-9a-fA-F]{6}' "${files[@]}" | tr 'A-F' 'a-f' | sort -u); do
    grep -qi -- "$hex" "$src" || { echo "  NOT IN SOURCE: $hex"; missing=$((missing+1)); }
  done
  [ "$missing" -eq 0 ] && note PASS "all colours trace back to the HTML" \
                       || { note WARN "$missing colour(s) not found in source"; }
else
  note WARN "source HTML not found, skipped colour trace"
fi

echo
[ "$fail" -eq 0 ] && echo "RESULT: no blocking problems — safe to paste into Scripter." \
                  || echo "RESULT: blocking problems above must be fixed first."
exit $fail
