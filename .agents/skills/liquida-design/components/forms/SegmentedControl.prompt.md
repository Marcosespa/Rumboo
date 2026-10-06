Mode/type toggle: cloudSoft track, ink-filled active segment. Rumbo uses it for "Entrar / Crear cuenta" and the capture document-type picker.

```jsx
<SegmentedControl
  options={[{ value: "login", label: "Entrar" }, { value: "register", label: "Crear cuenta" }]}
  value={mode}
  onChange={setMode}
/>
<SegmentedControl block options={["Gasto", "Cobro", "Vehículo"]} value={kind} onChange={setKind} />
```
