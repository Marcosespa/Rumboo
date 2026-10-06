State pill for vehicles, alerts and payments. Presets carry the canonical labels: "Al día", "Pendiente", "Urgente".

```jsx
<StatusPill status="ok" />
<StatusPill status="attention" />
<StatusPill status="critical" withIcon />
<StatusPill status="critical" solid>Urgente</StatusPill>
```

Never communicate state with color alone — use `withIcon` when the pill is the only state indicator.
