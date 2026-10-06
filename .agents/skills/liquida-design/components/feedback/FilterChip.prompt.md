Pill-shaped filter toggle for alert lists ("Todas · Urgentes · Atención").

```jsx
<FilterChip active={filter === "all"} onClick={() => setFilter("all")}>Todas</FilterChip>
<FilterChip active={filter === "critical"} onClick={() => setFilter("critical")}>Urgentes</FilterChip>
```
