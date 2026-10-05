The base container of every Rumbo screen section: paper surface, 1px line border, 28px radius, low warm shadow.

```jsx
<SectionCard
  title="Alertas del negocio"
  subtitle="Pagos por cobrar y recordatorios del vehículo que merecen atención."
  action={<button className="r-btn r-btn--ghost">Nuevo cobro <Icon name="ArrowRight" /></button>}
>
  …subcards…
</SectionCard>
```

Inner items go in `.r-subcard` (cloudSoft) so the page never feels like nested panels of the same color.
