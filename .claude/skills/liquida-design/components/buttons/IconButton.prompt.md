Square 44px bordered icon button — used for header utility actions (refresh, logout).

```jsx
<IconButton icon="RefreshCw" label="Actualizar" onClick={refresh} />
<IconButton icon="LogOut" label="Salir" />
```

Always pass `label`; it doubles as tooltip and aria-label.
