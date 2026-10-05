The app's only navigation: a floating pill bar fixed to the bottom, five destinations max, label always visible, ink-filled active item, error badge on Alertas.

```jsx
<BottomNav fixed active="dashboard" badges={{ alerts: 3 }} onSelect={go} />
```

Defaults to the canonical destinations: Panel, Vehículos, Alertas, Foto, Nuevo.
