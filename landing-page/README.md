# landing-page/ · sitio público de Rumbo

Landing de marketing en español e inglés. Presenta agentes para el mercado de la logística, beneficios, funcionamiento, revisión humana, piloto y contacto. No incluye la aplicación del producto, cuentas, formularios ni backend.

## Vista local

Desde esta carpeta ejecuta `npm run dev` y abre [http://127.0.0.1:4173](http://127.0.0.1:4173).

El servidor solo publica archivos estáticos. La página usa español por defecto; el selector ES/EN cambia todo el contenido. También puedes compartir la versión inglesa con `?lang=en`.

## Publicación

Desde la raíz del repositorio, el build es `npm --prefix landing-page run build`. Dentro de esta carpeta también puedes ejecutar `npm run build`. Publica la carpeta `dist/` en un hosting estático. No necesitas instalar dependencias.

## Contacto

El canal público se configura en `config.js`: `export const contact = { label: 'Tu correo oficial', href: 'mailto:tu-correo-oficial' };`.

Usa el destino oficial de Rumbo: correo, WhatsApp, teléfono o enlace para agendar. Hasta confirmarlo, la página muestra un mensaje de contacto pendiente. No inventa direcciones ni recoge datos.

## Identidad

Se aplicó la skill `.claude/skills/liquida-design`: cóndor original, papel cálido, azul ruta, Inter e Inter Tight, radios y sombras oficiales, iconos Lucide, tono directo y sin emoji. El contenido comercial presenta los pilotos como una propuesta; no afirma resultados, clientes, testimonios ni precios no confirmados.

Fuentes, logo e iconos se sirven localmente; no se utilizan CDN, rastreadores ni llamadas a servicios externos.

## Elementos conservados de la landing anterior

Se adaptaron el contexto del trabajo manual entre herramientas, las preguntas sobre herramientas y Satrack, los metadatos Open Graph/Twitter bilingües y el cierre del menú al tocar fuera. Se mantuvo la identidad de esta versión. No se trasladaron correos ficticios, planes comerciales no validados, cifras legales ni simulaciones de la interfaz del producto.

## Cloudflare Workers

Usa la rama `main` y el directorio raíz `/`.

- Build command: `npm --prefix landing-page run build`
- Deploy command: `npx wrangler deploy --name rumboo --assets ./landing-page/dist --compatibility-date 2026-10-06`

La única carpeta del frontend es `landing-page/`. Los archivos publicados salen de `landing-page/dist/`.
