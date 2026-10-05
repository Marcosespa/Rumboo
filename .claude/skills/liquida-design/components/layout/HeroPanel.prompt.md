The screen-top "answer" panel: 32px radius, ink (or primary) background, deep soft shadow. One protagonist figure, a metric grid and the screen's main CTAs.

```jsx
<HeroPanel
  overline="Dashboard"
  figure="$ 1.250.000"
  caption="Lo que realmente te queda este mes después de ingresos y gastos."
  metrics={[
    { label: "Entró", value: "$ 3.180.000" },
    { label: "Salió", value: "$ 1.930.000" },
    { label: "Te deben", value: "$ 860.000" },
  ]}
  actions={<>
    <Button variant="light"><Icon name="Camera" /> Tomar foto</Button>
    <Button variant="lightGhost"><Icon name="Plus" /> Agregar sin foto</Button>
  </>}
/>
```

`tone="primary"` is used on the Vehículos screen. Only `light`/`lightGhost` buttons inside.
