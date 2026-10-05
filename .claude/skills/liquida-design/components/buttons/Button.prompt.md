The Rumbo action button: 16px radius, ≥44px tall, hover lifts -2px with a soft shadow; loading state shows a spinner with "Espera...".

```jsx
<Button onClick={save}>Guardar seguimiento</Button>
<Button variant="accent" size="lg" block><Icon name="Camera" /> Tomar foto</Button>
<Button variant="secondary">Marcar como pagado</Button>
```

Rules: `accent` is reserved for the main photo CTA. `light`/`lightGhost` only sit on dark `HeroPanel`s. Pair with `<Icon size={16} />` on the left. Labels are short operational Spanish ("Resolver", "Entrar al panel").
