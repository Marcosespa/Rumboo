Screen header: brand chip (condor + wordmark), display title at 28px, mist subtitle, 44px utility icon buttons. Sticky with paper blur in the real app.

```jsx
<AppHeader
  title="Hola, Marcos"
  subtitle="Revisa caja, cobros y estado del vehículo."
  logoSrc="assets/logos/condor-sm.png"
  rightMeta={<span className="r-pill r-pill--ok">junio 2026</span>}
  onRefresh={() => {}}
  onLogout={() => {}}
/>
```

Brand rule: the condor logo always accompanies the "Rumbo" wordmark on each screen's first appearance.
