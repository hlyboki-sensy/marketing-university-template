# marketing-university

Переносимий шаблон Zettelkasten-бази знань для маркетингових проєктів, що працюють у звʼязці з [Claude Code](https://claude.com/claude-code).

Це **порожній generic-каркас**: без жодного контенту, готовий до розмноження в будь-який проєкт (включно з власним особистим брендом). Ти кидаєш джерела — Claude розкладає їх за методологією.

## Що це

База знань, керована за суворими правилами (`METHODOLOGY.md`). Працює як система: користувач кидає джерело (посилання, документ, відео) → Claude обробляє його за пайплайном → результат лягає в структуровані папки з перехресними посиланнями.

База знань не замінює рішення — вона їх **обґрунтовує і перевіряє**: кожне рішення в стратегії, офері, кампанії чи контенті привʼязане до конкретного перевірюваного твердження, що спирається на першоджерело.

**Артефакти пайплайну**:
- `sources/<id>/` — першоджерела з конспектами
- `notes/n-<slug>.md` — атомарні нотатки (одна ідея = один файл)
- `claims/c-<NNNN>.md` — перевірювані твердження з evidence
- `syntheses/syn-<topic>.md` — зведені документи
- `contradictions/contr-<NNN>.md` — зафіксовані конфлікти
- `verdicts/v-<slug>.md` — підсумкові рішення
- `experiments/` — власні тести (A/B, запуски, результати кампаній)
- `graph/edges.jsonl` — машиночитаний граф звʼязків

**Це НЕ скрипти.** Це конвенція + шаблони. Пайплайн виконує Claude, прочитавши `METHODOLOGY.md`.

## Встановлення

```bash
git clone <URL-цього-репозиторію> ~/marketing-university
# або в будь-яке зручне місце
```

Далі в будь-якому своєму проєкті запускаєш `~/marketing-university/bootstrap.sh <шлях-до-проєкту>` — див. розділ «Як використовувати» нижче.

## Залежності

- `bash` (стандартний на Linux/macOS)
- `python3` 3.6+ (тільки stdlib, нічого встановлювати не треба)
- `sed`, `find`, `cp`, `mkdir` — стандартні утиліти
- [Claude Code](https://claude.com/claude-code) — сам шаблон працює без нього, але вся цінність у звʼязці з Claude (memory-файли, інтеграція пайплайну)

## Платформи

- ✅ **macOS**
- ✅ **Linux**
- ⚠️ **Windows** — лише через WSL2

## Структура цього template-репозиторію

```
marketing-university/
├── README.md                         # цей файл — доки по шаблону
├── bootstrap.sh                      # скрипт ініціалізації в target-проєкті
├── interview.py                      # інтерактивне опитування (6 питань)
├── skeleton/                         # те, що копіюється в <target>/university/
│   ├── METHODOLOGY.md                # generic, з плейсхолдерами {{PROJECT_MISSION}} / {{PROJECT_NAME}}
│   ├── README.md                     # generic, з {{PROJECT_NAME}}
│   ├── TAXONOMY.md                   # порожній скелет (заповнюється при ініціалізації)
│   ├── INDEX.md                      # порожній індекс-скелет
│   ├── _templates/                   # шаблони для всіх типів артефактів
│   ├── sources/.gitkeep              # порожньо
│   ├── notes/.gitkeep                # порожньо
│   ├── claims/.gitkeep              # порожньо
│   ├── syntheses/.gitkeep            # порожньо
│   ├── contradictions/.gitkeep       # порожньо
│   ├── verdicts/.gitkeep             # порожньо
│   ├── experiments/.gitkeep          # порожньо
│   ├── graph/edges.jsonl             # порожній файл
│   └── queue/
│       ├── inbox.md                  # порожній
│       ├── to-follow.md              # порожній
│       └── escalation.md             # порожній
└── memory-template/                  # те, що потрапляє в Claude memory target-проєкту
    ├── reference_url_summary_workflow.md   # з {{PROJECT_NAME}} / {{PROJECT_PATH}}
    └── MEMORY.md.template            # entry для індексу MEMORY.md
```

## Як використовувати

### Крок 1 — bootstrap у новий проєкт

```bash
# приклад: ініціалізуємо university у новому проєкті ~/my-project
# (тека може ще не існувати — скрипт створить її, якщо батьківська є)
~/marketing-university/bootstrap.sh ~/my-project
```

Скрипт зробить:
1. Створить `<target>`, якщо теки ще нема (батьківська має існувати — захист від помилок у шляху)
2. Скопіює весь skeleton у `<target>/university/`
3. Замінить `{{PROJECT_NAME}}` на імʼя теки проєкту (автоматично)
4. Створить Claude memory-файл з правильними шляхами
5. Додасть entry в `MEMORY.md` цього memory-каталогу
6. **Запустить інтерактивне інтервʼю** (`interview.py`) — поставить 6 питань і сам заповнить плейсхолдери

Після цього Claude у новій сесії на проєкт автоматично побачить memory й спрямовуватиме всі джерела через базу знань.

### Крок 2 — відповісти на 6 питань інтервʼю

Bootstrap після копіювання скелета запустить `python3 interview.py <target>` автоматично. Питання:

1. **Місія проєкту** (обовʼязкове, одне речення)
   — _приклад: «Побудувати позиціонування й офер для експертного бренду»_

2. **Seed docs** (опціонально, список)
   — наявні документи проєкту, які треба обробити як первинні внутрішні джерела
   — формат: `<шлях> — опис`, по одному на рядок, порожній рядок = готово

3. **IN-SCOPE теми** (список)
   — що база приймає для обробки
   — приклад: `Воронки та лендінги (CRO) — що піднімає конверсію`

4. **OUT-OF-SCOPE теми** (список)
   — що одразу відхиляємо (захист від розповзання скоупу)
   — приклад: `Технічна розробка / верстка — не наш домен`

5. **Таксономія** (список листів дерева)
   — формат: `<root>/<leaf> — опис`
   — приклад: `cro/landing-pages — структура й конверсія лендінгів`

6. **Шляхи до маркетингових активів** (опціонально, для §14)
   — стратегія / офер / лендінг / контент-план, з якими база порівнює знання
   — приклад: `offers/main-offer.md — опис основного оферу`

Після відповідей скрипт покаже підсумок і попросить підтвердження (`Y/n`).

**Важливо**: інтервʼю працює лише в **справжньому терміналі** (TTY). Якщо bootstrap запущено в середовищі без TTY (наприклад, зсередини Claude Code Bash-tool) — інтервʼю автоматично пропускається з попередженням, і його треба запустити окремо в терміналі:

```bash
python3 ~/marketing-university/interview.py ~/my-project
```

### Альтернатива: `--no-interview`

Якщо хочеш заповнити вручну або скриптом пізніше:

```bash
~/marketing-university/bootstrap.sh <target> --no-interview
```

Тоді плейсхолдери лишаться як є (з інструкціями), їх треба замінити вручну в:
- `<project>/university/METHODOLOGY.md` — §1 (Місія), §1.1 (seed), §2 (scope), §14 (bridge paths)
- `<project>/university/TAXONOMY.md` — дерево тем
- `<project>/university/README.md` — `{{PROJECT_MISSION}}`
- `<project>/university/INDEX.md` — таблиця Pre-existing sources

Або запустити інтервʼю окремо пізніше:

```bash
python3 ~/marketing-university/interview.py <target>
```

### Крок 3 — перше джерело

```bash
# варіант A: вручну в inbox
echo "- https://example.com/article — стаття про X" >> <project>/university/queue/inbox.md

# варіант B: просто в чаті Claude
# → "обробити https://example.com/article"
# Claude прочитає memory → побачить, що джерело обробляється через university →
# прочитає METHODOLOGY → виконає пайплайн
```

### Опціонально — git-init

Рекомендується комітити university як частину проєкту (або окремий submodule):

```bash
cd <project>/university/
git init && git add -A && git commit -m "university: bootstrap from template"
```

## Перемикання між проєктами

У тебе **кілька проєктів** з university? Жодних конфліктів:
- Кожна база живе всередині свого проєкту (`<project>/university/`)
- Кожна Claude memory привʼязана до свого `~/.claude/projects/<path-slug>/memory/` (slug = абсолютний шлях проєкту, де `/` → `-`)
- Коли відкриваєш Claude Code у проєкті X — активна лише його memory
- Контент (sources, notes, claims) не перетинається

## Оновлення template

Якщо ти покращуєш `METHODOLOGY.md` або шаблони **в цьому template-репо**, наявні university в проєктах **не оновляться автоматично**. Це by design: кожен проєкт живе своїм життям.

Для оновлення:
```bash
# вручну скопіювати новий файл поверх
cp ~/marketing-university/skeleton/METHODOLOGY.md <project>/university/METHODOLOGY.md
# потім повернути проєкт-специфічні правки (§1, §1.1, §2, §14)
```

Або `bootstrap.sh` з `--force` (перезапише все — обережно):
```bash
~/marketing-university/bootstrap.sh <project> --force
```

## Створення нового проєкту «з нуля»

```bash
# 1. створити проєкт
mkdir ~/my-project
cd ~/my-project
git init

# 2. bootstrap university
~/marketing-university/bootstrap.sh $(pwd)

# 3. відкрити Claude Code у цій теці
# → у сесії Claude автоматично підтягне memory й слідуватиме правилам university
```

## Можливі покращення (на майбутнє)

- [ ] Опціональний `graph-validator` — перевірка цілісності `graph/edges.jsonl` (нема dangling references)
- [ ] Лінтер для атомарних нотаток (перевірка frontmatter, обовʼязковість секції Links)
- [ ] GitHub Action: при коміті в university/ автоматично перегенерувати INDEX.md
- [ ] MCP-сервер для Claude — прямий доступ до графа без читання jsonl

Поки все pure markdown — можна використовувати в будь-якій сесії Claude Code без додаткового тулінгу.
