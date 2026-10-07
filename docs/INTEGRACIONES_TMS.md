# Integraciones con TMS de transportadoras (futuro)

> Notas de diseño para cuando Rumbo se conecte a los TMS (sistemas de gestión de transporte) de las transportadoras. **No forma parte del alcance del MVP**: el alcance vigente lo define el [Plan maestro](../backend/PLAN.md). Esta referencia recoge el análisis previo para no repetirlo cuando empiece esa fase.

---

## 1. El problema

Cada transportadora usa un TMS distinto. Muchos no tienen API: son aplicaciones web sin servicios expuestos, software de escritorio viejo o desarrollos a la medida con la base de datos en una máquina de la oficina. No existe un mecanismo único que sirva para todos.

## 2. Tipos de TMS y cómo integrarlos

| Tipo de TMS | Mecanismo recomendado | Notas |
|---|---|---|
| Con API o web service | API oficial | Siempre la primera opción |
| Web moderna sin API | Navegador automatizado ([Browserbase](https://www.browserbase.com)) | Caso ideal para Browserbase |
| Web vieja (ASP clásico, JSF, iframes) | Navegador automatizado | Más trabajo de selectores. Si solo funciona en Internet Explorer, no corre en el navegador remoto |
| Escritorio Windows (VB, FoxPro, Delphi, cliente-servidor) | Lectura de base de datos o exportes | Browserbase **no** sirve: no hay navegador |
| Instalado en servidor local (intranet) | Agente local | Browserbase solo sirve si el TMS se expone hacia afuera o hay VPN |
| Excel o correo usados como "TMS" | Importación de archivos | No hace falta automatizar nada |

### 2.1 Orden de preferencia

1. **API oficial o web service**, si existe.
2. **Base de datos de solo lectura o exportes** (SQL, CSV o Excel por correo o SFTP). Barato y estable.
3. **Navegador automatizado (Browserbase)** para los TMS web sin API.
4. **Automatización de escritorio o IA que maneja la pantalla**, solo como último recurso.

El RNDC del Ministerio de Transporte tiene su propio web service: nunca se integra por scraping.

### 2.2 Agente local

En pequeñas y medianas transportadoras es común el software de escritorio con SQL Server en una máquina de la oficina. Para esos casos la integración más estable es un agente pequeño instalado en la empresa que:

- lee la base de datos con un usuario de **solo lectura**, o vigila una carpeta de exportes;
- envía los datos a Rumbo por HTTPS (solo conexiones salientes, sin abrir puertos en la oficina);
- se autentica con una llave por transportadora.

## 3. Browserbase

Servicio de navegadores en la nube, compatible con Selenium, Playwright y Puppeteer.

### 3.1 Qué aporta

- **Saca Chrome de nuestra infraestructura.** Hoy `satrack-service` levanta `webdriver.Chrome` dentro del contenedor. Con Browserbase el cambio es usar `webdriver.Remote` hacia su endpoint.
- **Contexts persistentes.** Guardan cookies y sesión entre consultas: el scheduler no inicia sesión en cada consulta. Baja la latencia, el costo y el riesgo de bloqueo de la cuenta.
- **Live view embebible.** El coordinador puede iniciar sesión en su TMS desde la web de Rumbo con su propia contraseña y su 2FA. Rumbo guarda la sesión, no la contraseña. Encaja con el flujo "Conectar Satrack".
- **Grabación de sesiones** para depurar fallos.
- **Stagehand** (automatización con IA). Aguanta mejor los cambios de interfaz que los selectores fijos. Útil cuando haya muchos TMS distintos.

### 3.2 Riesgos y cuidados

1. **Costo por minuto de navegador.** Calcular cuentas × frecuencia × duración de sesión antes de comprometerse. Agrupar las consultas por cuenta, no por vehículo.
2. **Leer no es lo mismo que escribir.** Leer posiciones o viajes es de bajo riesgo. Crear remesas o manifiestos en el TMS del cliente exige evitar duplicados, comprobar después de cada escritura y que un humano confirme. Con IA de por medio, esto pesa todavía más.
3. **Datos y términos de uso.** Las sesiones de los clientes quedan en servidores de un tercero (EE. UU.). Debe constar en los términos y en el tratamiento de datos. Revisar también qué permite cada proveedor sobre el acceso automatizado, y tener autorización escrita de la transportadora.
4. **Dependencia del proveedor.** Escribir los conectores con Selenium o Playwright estándar permite volver a Chrome local o cambiar de servicio. Stagehand ata más a Browserbase: usarlo solo donde los selectores fijos no aguanten.

## 4. Encaje en el código

`satrack-service` ya separa proveedores en `app/providers/` ([base.py](../satrack-service/app/providers/base.py), `satrack.py`, `simulator.py`). Los TMS siguen el mismo patrón:

- Una interfaz genérica de conector, en la línea de `Provider`, con operaciones del dominio: `obtener_viajes`, `obtener_posiciones`, `crear_remesa`…
- Una implementación por TMS. Cada una elige su mecanismo por debajo (API, base de datos, Browserbase, archivo).
- El backend consume el conector sin saber cómo se obtienen los datos.
- El backend de navegador se elige por configuración, por ejemplo `BROWSER_BACKEND=local|browserbase`, para poder revertir sin cambiar código.

## 5. Plan sugerido

1. **MVP:** seguir con Selenium local en `satrack-service`. No cambiar mientras se valida el producto.
2. **Encuesta de mercado:** preguntar a 10–15 transportadoras qué TMS usan, si es web o de escritorio, si tiene API y dónde está la base de datos. Probablemente 3 o 4 sistemas cubren la mayoría.
3. **Piloto de Browserbase:** activar `BROWSER_BACKEND=browserbase` contra Satrack real y medir tiempo y costo por consulta.
4. **Primeros conectores TMS:** integrar los 3 o 4 sistemas más comunes, cada uno con el mecanismo que le corresponda, en vez de buscar una solución universal.
5. **Flujo "Conectar TMS"** con live view para los conectores web.

## 6. Pendientes

- [ ] Encuesta de TMS usados por transportadoras en Colombia
- [ ] Precio vigente de Browserbase y costo estimado por cuenta/mes
- [ ] Revisar dónde guarda los datos Browserbase y su política de privacidad
- [ ] Definir la interfaz genérica de conector TMS
- [ ] Decidir si el agente local se distribuye como instalador Windows o contenedor
