Card for one alert (documento por vencer, cartera vencida, servicio próximo). Critical severity tints the card with error.

```jsx
<AlertCard
  severity="critical"
  title="SOAT vencido"
  detail="El SOAT de Turbo Azul venció el 2 de junio."
  meta="DOCUMENTO · 2 DE JUNIO DE 2026"
  actions={<>
    <Button variant="secondary"><Icon name="TriangleAlert" /> Ver vehículo</Button>
    <Button><Icon name="CheckCircle2" /> Resolver</Button>
  </>}
/>
```
