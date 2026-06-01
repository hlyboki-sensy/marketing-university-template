# To-follow queue (BFS)

Внутрішня черга посилань, знайдених усередині вже оброблених джерел. Поповнюється автоматично на кроці 7 пайплайну (див. METHODOLOGY.md §4).

Формат:

```
- <URL>
  parent: <source-id>
  anchor: "<anchor text>"
  predicted_relevance: X/5
  depth: N
  status: queued | fetched | rejected
  note: (опціонально) чому це важливо
```

## Queue

<!-- порожньо -->

## Done

<!-- порожньо -->
