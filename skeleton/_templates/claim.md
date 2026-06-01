---
id: c-NNNN
statement: '<перевірюване твердження однією фразою>'
domain: [<тема-1>, <тема-2>, ...]   # домени таксономії, до яких належить
confidence: H | M | L
conditions: '<ВІСЬ МЕЖІ — обов’язково: де/для кого правда — сегмент / ринок / канал / тип трафіку / цінова категорія>'
durability: tactical | principle    # ВІСЬ ЧАСУ: tactical (протухає) / principle (вічнозелене)
evidence: [n-..., n-...]
contradictions: []
sources: [src-...]
testable: true | false
test_method: '<як перевірити В МЕЖАХ conditions: A/B-тест / запуск кампанії / порівняння з власними даними / опитування>'
implication_for_project: '<що конкретно це означає для стратегії / оферу / кампанії / контенту>'
status: live | stale | superseded
review_by: YYYY-MM-DD | null         # дата для tactical; для principle → null
last_validated: YYYY-MM-DD
created: YYYY-MM-DD
---

# <statement повторюється як заголовок>

## Context

За яких умов твердження справедливе. Межі застосовності (дублює `conditions` розгорнуто).

## Evidence walk-through

Коротко: які нотатки/джерела і чому дають саме такий рівень `confidence`. Якщо є активні bias-прапорці у джерел — нагадай про стелю довіри (METHODOLOGY §3).

## Counter-evidence / edge cases

Що могло б спростувати. Де ми на тонкому льоду. У яких сусідніх сегментах це вже НЕ працює.

## Implication for project (детальніше)

Конкретні висновки: що саме робити/не робити в стратегії, офері, кампанії, контенті.

## Validation log

- YYYY-MM-DD: created — `confidence: X`, на базі src-...
- _(при перевалідації: дата, що перевіряли по осі часу й по осі межі, результат: confirm / narrow / widen / supersede)_
