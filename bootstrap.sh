#!/usr/bin/env bash
# marketing-university bootstrap
# Usage:
#   bootstrap.sh <target-project-path> [--force] [--no-interview]
#
# Copies the generic university skeleton into <target>/university/, plus
# creates a Claude Code memory entry so future sessions on that project
# automatically route every URL through the university pipeline
# (per METHODOLOGY.md).
#
# By default, runs interactive interview (interview.py) after copying to fill
# in project-specific placeholders. Use --no-interview to skip and fill manually.
#
# Example:
#   ./bootstrap.sh ~/my-project
#   → creates ~/my-project/university/
#   → creates ~/.claude/projects/<path-slug>/memory/reference_url_summary_workflow.md
#     (slug = absolute project path with '/' replaced by '-')
#   → launches interactive interview to fill placeholders

set -euo pipefail

TEMPLATE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKELETON_DIR="$TEMPLATE_DIR/skeleton"
MEMORY_TEMPLATE_DIR="$TEMPLATE_DIR/memory-template"
INTERVIEW_SCRIPT="$TEMPLATE_DIR/interview.py"

err() { echo "ПОМИЛКА: $*" >&2; exit 1; }
warn() { echo "УВАГА: $*" >&2; }

# Portable in-place sed: GNU sed uses `-i`, BSD/macOS sed needs `-i ''`.
# Detect once, expose as an array we can splat.
if sed --version >/dev/null 2>&1; then
  SED_INPLACE=(sed -i)        # GNU
else
  SED_INPLACE=(sed -i '')     # BSD / macOS
fi

sed_subst() {
  # sed_subst <expr> <file>
  "${SED_INPLACE[@]}" "$1" "$2"
}

[[ $# -ge 1 ]] || err "використання: $0 <target-project-path> [--force] [--no-interview]"

TARGET="$1"
FORCE=0
RUN_INTERVIEW=1
shift
while [[ $# -gt 0 ]]; do
  case "$1" in
    --force) FORCE=1; shift;;
    --no-interview) RUN_INTERVIEW=0; shift;;
    *) err "невідомий прапорець: $1";;
  esac
done

# Resolve TARGET to absolute path. If missing, create it (expected for fresh projects).
# Parent must exist — we don't create arbitrary path prefixes to avoid typos creating garbage.
if [[ -d "$TARGET" ]]; then
  TARGET="$(cd "$TARGET" && pwd)"
else
  PARENT_DIR="$(dirname "$TARGET")"
  BASE_NAME="$(basename "$TARGET")"
  [[ -d "$PARENT_DIR" ]] || err "батьківська тека не існує: $PARENT_DIR (створи її або виправ помилку в шляху)"
  ABS_PARENT="$(cd "$PARENT_DIR" && pwd)"
  TARGET="$ABS_PARENT/$BASE_NAME"
  echo ">> Цільова тека не існує, створюю: $TARGET"
  mkdir "$TARGET" || err "не вдалося створити target: $TARGET"
fi

PROJECT_NAME="$(basename "$TARGET")"
UNIVERSITY_DIR="$TARGET/university"

# Derive Claude Code memory directory slug from absolute path:
# /home/alice/foo-bar → -home-alice-foo-bar
CLAUDE_SLUG="$(echo "$TARGET" | sed 's|/|-|g')"
CLAUDE_MEMORY_DIR="$HOME/.claude/projects/$CLAUDE_SLUG/memory"

echo "=== marketing-university bootstrap ==="
echo "Цільовий проєкт: $TARGET"
echo "Назва проєкту:   $PROJECT_NAME"
echo "University dir:  $UNIVERSITY_DIR"
echo "Claude memory:   $CLAUDE_MEMORY_DIR"
echo

# Step 1: check target doesn't already have a university (unless --force)
if [[ -d "$UNIVERSITY_DIR" && $FORCE -eq 0 ]]; then
  err "$UNIVERSITY_DIR вже існує. Використай --force, щоб перезаписати (затре наявні файли)."
fi

# Step 2: copy skeleton
echo ">> Копіюю skeleton…"
mkdir -p "$UNIVERSITY_DIR"
cp -r "$SKELETON_DIR/." "$UNIVERSITY_DIR/"
echo "   готово: $(find "$UNIVERSITY_DIR" -type f | wc -l | tr -d ' ') файлів скопійовано"

# Step 3: substitute {{PROJECT_NAME}} in the copied university files
# (we keep {{PROJECT_MISSION}} as-is — user fills that manually / via interview)
echo ">> Підставляю {{PROJECT_NAME}} у skeleton…"
while IFS= read -r -d '' f; do
  sed_subst "s|{{PROJECT_NAME}}|$PROJECT_NAME|g" "$f"
done < <(find "$UNIVERSITY_DIR" -type f \( -name "*.md" -o -name "*.yaml" -o -name "*.jsonl" \) -print0)

# Step 4: set up Claude memory
echo ">> Налаштовую Claude memory в $CLAUDE_MEMORY_DIR…"
mkdir -p "$CLAUDE_MEMORY_DIR"

MEMORY_FILE="$CLAUDE_MEMORY_DIR/reference_url_summary_workflow.md"
if [[ -f "$MEMORY_FILE" && $FORCE -eq 0 ]]; then
  warn "$MEMORY_FILE існує, пропускаю (використай --force, щоб перезаписати)"
else
  cp "$MEMORY_TEMPLATE_DIR/reference_url_summary_workflow.md" "$MEMORY_FILE"
  sed_subst "s|{{PROJECT_NAME}}|$PROJECT_NAME|g" "$MEMORY_FILE"
  sed_subst "s|{{PROJECT_PATH}}|$TARGET|g" "$MEMORY_FILE"
  echo "   готово: $MEMORY_FILE"
fi

# Step 5: append to MEMORY.md if exists, else create
MEMORY_INDEX="$CLAUDE_MEMORY_DIR/MEMORY.md"
ENTRY_LINE="- [URL processing → university pipeline](reference_url_summary_workflow.md) — CRITICAL. Кожен URL іде через $TARGET/university/ Zettelkasten, НЕ переказ у чаті. Спершу читай METHODOLOGY.md."

if [[ -f "$MEMORY_INDEX" ]]; then
  if grep -q "reference_url_summary_workflow.md" "$MEMORY_INDEX"; then
    warn "MEMORY.md вже має запис про url-summary-workflow, пропускаю"
  else
    echo "$ENTRY_LINE" >> "$MEMORY_INDEX"
    echo "   дописано запис у наявний MEMORY.md"
  fi
else
  echo "$ENTRY_LINE" > "$MEMORY_INDEX"
  echo "   створено новий MEMORY.md"
fi

echo
echo "=== ✓ копіювання skeleton завершено ==="
echo

# Step 6: interactive interview (unless --no-interview)
if [[ $RUN_INTERVIEW -eq 1 ]]; then
  if [[ ! -t 0 ]]; then
    warn "stdin не є TTY — не можу запустити інтерактивне інтервʼю. Пропускаю."
    warn "Запусти вручну пізніше:  python3 $INTERVIEW_SCRIPT $TARGET"
    RUN_INTERVIEW=0
  elif ! command -v python3 >/dev/null 2>&1; then
    warn "python3 не знайдено — не можу запустити інтервʼю. Пропускаю."
    warn "Встанови python3, потім: python3 $INTERVIEW_SCRIPT $TARGET"
    RUN_INTERVIEW=0
  else
    echo
    echo ">> Запускаю інтерактивне інтервʼю (Ctrl+C щоб пропустити)…"
    echo
    python3 "$INTERVIEW_SCRIPT" "$TARGET" || warn "Інтервʼю перервано/не вдалося — плейсхолдери лишились. Перезапуск: python3 $INTERVIEW_SCRIPT $TARGET"
  fi
fi

echo
echo "=== ✓ bootstrap завершено ==="
echo
if [[ $RUN_INTERVIEW -eq 0 ]]; then
  echo "Наступні кроки (вручну — інтервʼю пропущено):"
  echo
  echo "  Запусти інтервʼю пізніше:  python3 $INTERVIEW_SCRIPT $TARGET"
  echo "  АБО відредагуй плейсхолдери вручну в:"
  echo "     - $UNIVERSITY_DIR/METHODOLOGY.md"
  echo "         § 1 (Місія): заміни {{PROJECT_MISSION}}"
  echo "         § 1.1 (seed): перелічи наявні документи проєкту"
  echo "         § 2 (Скоуп): визнач in-scope / out-of-scope для ЦЬОГО проєкту"
  echo "         § 14 (Місток до активів): вкажи шляхи до стратегії / оферу / лендінгу / кампаній"
  echo "     - $UNIVERSITY_DIR/TAXONOMY.md"
  echo "         Заміни приклад дерева на реальну ієрархію тем"
  echo "     - $UNIVERSITY_DIR/README.md"
  echo "         Заміни {{PROJECT_MISSION}} (одне речення про проєкт)"
  echo "     - $UNIVERSITY_DIR/INDEX.md"
  echo "         Додай таблицю Pre-existing internal sources, якщо такі є"
  echo
fi

echo "Перевір, що Claude memory підхопилась:"
echo "   cat $MEMORY_INDEX"
echo
echo "Опціонально — git-init університету:"
echo "   cd $UNIVERSITY_DIR && git init && git add -A && git commit -m 'university: bootstrap from template'"
echo
echo "Кинь перше посилання в:"
echo "   $UNIVERSITY_DIR/queue/inbox.md"
echo "   — або просто встав URL у сесію Claude на проєкті"
echo
