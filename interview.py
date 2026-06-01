#!/usr/bin/env python3
"""Інтерактивне налаштування скелета marketing-university/ після bootstrap.

Опитує оператора і заповнює плейсхолдери в:
  - METHODOLOGY.md (§1 місія, §1.1 seed-доки, §2 скоуп in/out, §14 місток до активів)
  - TAXONOMY.md (дерево тем)
  - INDEX.md (таблиця Pre-existing internal sources)
  - README.md (токен {{PROJECT_MISSION}})

Запуск:
  python3 interview.py <шлях-до-проєкту>

У цільовій теці вже має бути директорія `university/`, створена через bootstrap.sh.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Tuple


# -------- I/O-хелпери -------------------------------------------------------

def hr():
    print("─" * 60)


def header(n: int, total: int, title: str):
    hr()
    print(f"  [{n}/{total}]  {title}")
    hr()


def ask_single(prompt: str, required: bool = True, example: str | None = None) -> str:
    """Запитати один рядок. Перепитує, якщо обовʼязкове й порожнє."""
    if example:
        print(f"  приклад: {example}")
    while True:
        try:
            answer = input(f"> ").strip()
        except EOFError:
            print()  # перенос рядка після ^D
            sys.exit("перервано (EOF)")
        if answer or not required:
            return answer
        print("  (поле обовʼязкове, спробуй ще раз)")


def ask_bullets(help_text: str, example: str | None = None) -> List[str]:
    """Зібрати пункти, по одному на рядок. Порожній рядок завершує ввід.
    Повертає список рядків (без дефіса спереду). Порожній список — ОК."""
    print(f"  {help_text}")
    if example:
        print(f"  приклад рядка: {example}")
    print("  (порожній рядок = завершили)")
    bullets: List[str] = []
    while True:
        try:
            line = input(f"  {len(bullets)+1}> ").strip()
        except EOFError:
            print()
            break
        if not line:
            break
        # Прибрати "- " спереду, якщо користувач його ввів
        if line.startswith("- "):
            line = line[2:]
        bullets.append(line)
    return bullets


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    hint = "[Y/n]" if default else "[y/N]"
    while True:
        try:
            answer = input(f"{prompt} {hint}: ").strip().lower()
        except EOFError:
            print()
            return default
        if not answer:
            return default
        if answer in ("y", "yes", "т", "так"):
            return True
        if answer in ("n", "no", "н", "ні"):
            return False
        print("  (введи y або n)")


# -------- Підстановка у файли -----------------------------------------------

def replace_section(file_path: Path, section_id: str, new_content: str) -> bool:
    """Замінити вміст між маркерами BOOTSTRAP:PLACEHOLDER:<id> і BOOTSTRAP:END:<id>.

    Повертає True, якщо замінено; False, якщо маркерів не знайдено.
    """
    text = file_path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf'<!-- BOOTSTRAP:PLACEHOLDER:{re.escape(section_id)} -->.*?<!-- BOOTSTRAP:END:{re.escape(section_id)} -->',
        re.DOTALL,
    )
    replacement = (
        f'<!-- BOOTSTRAP:FILLED:{section_id} -->\n'
        f'{new_content}\n'
        f'<!-- BOOTSTRAP:END:{section_id} -->'
    )
    new_text, n = pattern.subn(replacement, text)
    if n == 0:
        return False
    file_path.write_text(new_text, encoding="utf-8")
    return True


def replace_token(file_path: Path, token: str, value: str) -> int:
    """Замінити всі входження `{{TOKEN}}` у файлі на value. Повертає кількість."""
    text = file_path.read_text(encoding="utf-8")
    new_text = text.replace(token, value)
    count = text.count(token)
    if count > 0:
        file_path.write_text(new_text, encoding="utf-8")
    return count


# -------- Білдери вмісту ----------------------------------------------------

def build_mission_section(mission: str) -> str:
    return (
        f'Зібрати й систематизувати знання, достатні, щоб **{mission}**. '
        f'«Обґрунтовано» = кожне рішення в стратегії, офері, кампанії чи контенті можна '
        f'привʼязати до конкретного перевірюваного твердження (`claim`), яке спирається '
        f'на конкретне першоджерело.\n\n'
        f'База знань не замінює маркетинг — вона дає йому доказову основу замість '
        f'«здається» й «у всіх так».'
    )


def build_bullet_list(items: List[str], empty_placeholder: str = "_Поки нема._") -> str:
    if not items:
        return empty_placeholder
    return "\n".join(f"- {item}" for item in items)


def build_index_seed_table(seed_docs: List[Tuple[str, str]]) -> str:
    """seed_docs — список кортежів (path, description)."""
    if not seed_docs:
        return (
            "| Path | Role | Quality | Relevance |\n"
            "|------|------|---------|-----------|\n"
            "| _(поки нема pre-existing документів)_ | — | — | — |"
        )
    lines = [
        "| Path | Role | Quality | Relevance |",
        "|------|------|---------|-----------|",
    ]
    for path, desc in seed_docs:
        lines.append(f"| [{path}]({path}) | {desc} | pending | 5 |")
    return "\n".join(lines)


def parse_seed_docs(raw: List[str]) -> List[Tuple[str, str]]:
    """Розпарсити формат 'path — опис' у кортежі (path, description).
    Фолбек: якщо нема роздільника '—' — увесь рядок = шлях із загальним описом."""
    result = []
    for line in raw:
        if "—" in line:
            path, _, desc = line.partition("—")
            result.append((path.strip(), desc.strip()))
        elif " - " in line:
            path, _, desc = line.partition(" - ")
            result.append((path.strip(), desc.strip()))
        else:
            result.append((line.strip(), "pre-existing документ"))
    return result


def build_taxonomy_tree(entries: List[str]) -> str:
    """Перетворити записи таксономії на дерево в код-блоці.

    Кожен запис — це або:
      'root/'                       — коренева тема
      'root/leaf — опис'            — лист з описом
    """
    if not entries:
        return "```\n<коренева-тема>/\n└── <лист>/   — що сюди потрапляє\n```"

    # Групуємо за кореневою темою
    roots: dict[str, List[Tuple[str, str]]] = {}
    for entry in entries:
        # Лист: "root/leaf — опис" або "root/leaf - опис"
        if "—" in entry or " - " in entry:
            sep = "—" if "—" in entry else " - "
            path_part, _, description = entry.partition(sep)
            description = description.strip()
        else:
            path_part = entry
            description = ""

        path_part = path_part.strip().rstrip("/")
        if "/" in path_part:
            root, leaf = path_part.split("/", 1)
            roots.setdefault(root, []).append((leaf, description))
        else:
            # Гола коренева тема
            roots.setdefault(path_part, [])

    # Рендеримо дерево
    lines = ["```"]
    root_list = list(roots.items())
    for i, (root, leaves) in enumerate(root_list):
        lines.append(f"{root}/")
        for j, (leaf, desc) in enumerate(leaves):
            is_last = j == len(leaves) - 1
            branch = "└──" if is_last else "├──"
            if desc:
                lines.append(f"{branch} {leaf}/    — {desc}")
            else:
                lines.append(f"{branch} {leaf}/")
        if i < len(root_list) - 1:
            lines.append("")
    lines.append("```")
    return "\n".join(lines)


# -------- Головне інтервʼю ---------------------------------------------------

def main():
    if len(sys.argv) < 2:
        sys.exit("використання: python3 interview.py <шлях-до-проєкту>")

    target = Path(sys.argv[1]).resolve()
    uni = target / "university"
    if not uni.is_dir():
        sys.exit(f"ПОМИЛКА: {uni} не існує. Спершу запусти bootstrap.sh.")

    methodology = uni / "METHODOLOGY.md"
    taxonomy = uni / "TAXONOMY.md"
    readme = uni / "README.md"
    index = uni / "INDEX.md"

    for f in (methodology, taxonomy, readme, index):
        if not f.exists():
            sys.exit(f"ПОМИЛКА: відсутній очікуваний файл: {f}")

    project_name = target.name

    print()
    hr()
    print(f"  Інтервʼю ініціалізації бази знань — проєкт: {project_name}")
    hr()
    print(
        "\n  Відповідай на питання по черзі. Усе можна пропустити порожнім рядком "
        "(крім місії). Наприкінці файли оновляться.\n"
    )

    # Q1: Місія (обовʼязкове)
    header(1, 6, "Місія проєкту")
    print("  Одним реченням опиши, яке знання має обґрунтувати ця база.")
    print("  Приклад 1: «Побудувати позиціонування й офер для експертного бренду»")
    print("  Приклад 2: «Зрозуміти, які канали дають найнижчий CAC у ніші X»")
    print()
    mission = ask_single("", required=True)

    # Q2: Seed-доки
    print()
    header(2, 6, "Наявні документи проєкту (seed)")
    print("  Чи є вже написані дослідження/доки в проєкті, які треба")
    print("  обробити як первинні внутрішні джерела (relevance=5)?")
    print()
    seed_docs_raw = ask_bullets(
        "Один запис на рядок у форматі: <шлях> — опис",
        example="research/audience-analysis.md — аналіз аудиторії та JTBD",
    )
    seed_docs = parse_seed_docs(seed_docs_raw)

    # Q3: In-scope
    print()
    header(3, 6, "Теми IN-SCOPE (що обробляємо)")
    print("  Які теми джерел база має приймати для обробки?")
    print()
    in_scope = ask_bullets(
        "Одна тема на рядок (короткий опис).",
        example="Воронки та лендінги (CRO) — що піднімає конверсію",
    )

    # Q4: Out-of-scope
    print()
    header(4, 6, "Теми OUT-OF-SCOPE (що відхиляємо)")
    print("  Які теми треба одразу відсікати, щоб скоуп не розповзався?")
    print()
    out_scope = ask_bullets(
        "Одна тема на рядок.",
        example="Технічна розробка / верстка — не наш домен",
    )

    # Q5: Таксономія
    print()
    header(5, 6, "Таксономія (дерево тем для syntheses/)")
    print("  Ієрархія тем, за якими будуватимуться зведені документи.")
    print("  Формат рядка: <root>/<leaf> — опис")
    print("  Кидай рядки по одному; кожен шлях '<root>/<leaf>' створює лист у дереві.")
    print()
    taxonomy_entries = ask_bullets(
        "Один рядок = один лист таксономії.",
        example="cro/landing-pages — структура й конверсія лендінгів",
    )

    # Q6: Місток до активів (опціонально)
    print()
    header(6, 6, "Шляхи до живих маркетингових активів (§14) — опціонально")
    print("  Шляхи до файлів/папок проєкту, з якими база порівнюватиме свої знання")
    print("  (стратегія, офер, лендінг, контент-план, кампанії). Можна пропустити.")
    print()
    bridge_paths_raw = ask_bullets(
        "Один запис на рядок: <шлях> — опис",
        example="offers/main-offer.md — опис основного оферу й позиціонування",
    )

    # ---- Підсумок + підтвердження ----
    print()
    hr()
    print("  Готовий записати?")
    hr()
    print(f"  Місія:          {mission}")
    print(f"  Seed docs:      {len(seed_docs)} шт")
    print(f"  In-scope:       {len(in_scope)} пунктів")
    print(f"  Out-of-scope:   {len(out_scope)} пунктів")
    print(f"  Taxonomy:       {len(taxonomy_entries)} листів")
    print(f"  Bridge paths:   {len(bridge_paths_raw)} шт")
    print()
    if not ask_yes_no("Застосувати?", default=True):
        print("скасовано; нічого не змінено.")
        sys.exit(0)

    # ---- Застосовуємо підстановки ----
    changes: List[str] = []

    # METHODOLOGY.md §1 місія
    if replace_section(methodology, "section_mission", build_mission_section(mission)):
        changes.append(f"  ✓ METHODOLOGY.md §1 (Місія)")

    # METHODOLOGY.md §1.1 seed-доки
    seed_content = build_bullet_list(
        [f"`{p}` — {d}" for p, d in seed_docs],
        empty_placeholder="_Поки нема pre-existing документів для обробки як seed._",
    )
    if replace_section(methodology, "section_seed_docs", seed_content):
        changes.append(f"  ✓ METHODOLOGY.md §1.1 (Seed docs)")

    # METHODOLOGY.md §2 scope in
    if replace_section(methodology, "section_scope_in", build_bullet_list(in_scope)):
        changes.append(f"  ✓ METHODOLOGY.md §2 in-scope")

    # METHODOLOGY.md §2 scope out
    if replace_section(methodology, "section_scope_out", build_bullet_list(out_scope)):
        changes.append(f"  ✓ METHODOLOGY.md §2 out-of-scope")

    # METHODOLOGY.md §14 місток до активів
    bridge_bullets = [f"   - `{line.split('—', 1)[0].strip() if '—' in line else line.split(' - ', 1)[0].strip()}` — "
                      f"{line.split('—', 1)[1].strip() if '—' in line else (line.split(' - ', 1)[1].strip() if ' - ' in line else '')}"
                      for line in bridge_paths_raw]
    # Відступ у 3 пробіли, щоб лягло в нумерований список
    if bridge_paths_raw:
        bridge_content = "\n".join(bridge_bullets)
    else:
        bridge_content = "   - _(шляхів ще нема — додай, коли зʼявляться активи для порівняння)_"
    if replace_section(methodology, "section_bridge_paths", bridge_content):
        changes.append(f"  ✓ METHODOLOGY.md §14 bridge paths")

    # TAXONOMY.md дерево
    if replace_section(taxonomy, "section_taxonomy_tree", build_taxonomy_tree(taxonomy_entries)):
        changes.append(f"  ✓ TAXONOMY.md дерево")

    # INDEX.md таблиця seed
    if replace_section(index, "section_index_preexisting", build_index_seed_table(seed_docs)):
        changes.append(f"  ✓ INDEX.md Pre-existing seed table")

    # README.md + METHODOLOGY.md підстановка токена місії
    readme_replaced = replace_token(readme, "{{PROJECT_MISSION}}", mission)
    methodology_replaced = replace_token(methodology, "{{PROJECT_MISSION}}", mission)
    if readme_replaced > 0:
        changes.append(f"  ✓ README.md: замінено {{PROJECT_MISSION}} ({readme_replaced} раз)")
    if methodology_replaced > 0:
        changes.append(f"  ✓ METHODOLOGY.md: замінено {{PROJECT_MISSION}} ({methodology_replaced} раз)")

    # ---- Готово ----
    print()
    hr()
    print("  Зміни застосовано:")
    hr()
    for c in changes:
        print(c)
    print()
    print("  Наступний крок — відкрий файли й перевір очима:")
    print(f"    {methodology}")
    print(f"    {taxonomy}")
    print(f"    {readme}")
    print(f"    {index}")
    print()
    print("  Якщо все ок — git add & commit.")
    print()


if __name__ == "__main__":
    main()
