/**
 * Diccionario en español (Colombia): FUENTE DE VERDAD de las claves.
 * `en.ts` debe tener exactamente la misma forma (`Messages`); si falta o sobra una clave, TypeScript falla.
 *
 * Cómo añadir textos de una pantalla: rellena SOLO tu sección (`login`, `panel`, `trips`, `newTrip`,
 * `tripDetail`, `fleet`, `settings`) en AMBOS archivos. Reglas:
 *  - Claves anidadas (`panel.hero.title`), nombres en camelCase.
 *  - Interpolación con llaves: 'Hola, {name}'.
 *  - Plurales: un objeto con `one` y `other` y la variable `{count}`:
 *      count: { one: '{count} viaje', other: '{count} viajes' }  →  t('trips.count', { count })
 *  - Tuteo, sentence case, botón = verbo + objeto, placeholders "Ej. …", sin emoji.
 */
export const es = {
  common: {
    wait: 'Espera...',
    loading: 'Cargando…',
    retry: 'Reintentar',
    back: 'Volver',
    noData: 'Sin dato',
    time: {
      unavailable: 'Hora GPS no disponible',
      ahead: 'Hora GPS adelantada',
      justNow: 'Hace un momento',
      minutes: 'Hace {count} min',
      hours: 'Hace {count} h',
      days: { one: 'Hace {count} día', other: 'Hace {count} días' },
    },
  },
  nav: {
    panel: 'Panel',
    trips: 'Viajes',
    newTrip: 'Nuevo',
    fleet: 'Flota',
    settings: 'Ajustes',
    mainLabel: 'Navegación principal',
    mobileLabel: 'Navegación móvil',
  },
  status: {
    trip: {
      registrado: 'Sin verificar',
      programado: 'Programado',
      en_ruta: 'En ruta',
      entregado: 'Entregado',
      cancelado: 'Cancelado',
      unknown: 'Por revisar',
    },
    satrack: {
      ok: 'Conectado',
      sin_verificar: 'Por verificar',
      credenciales_invalidas: 'Revisa las credenciales',
      falla: 'Conexión con fallas',
      unknown: 'Por revisar',
    },
    pill: {
      ok: 'Al día',
      attention: 'Pendiente',
      critical: 'Urgente',
      success: 'Pagado',
      warning: 'Por vencer',
      accent: 'Nuevo',
    },
    severity: {
      attention: 'Atención',
      critical: 'Urgente',
    },
  },
  auth: {
    loading: 'Cargando tu operación…',
    sessionError: 'No pudimos comprobar tu sesión. Vuelve a intentar.',
  },
  layout: {
    trafficControl: 'Control de tráfico',
    logout: 'Cerrar sesión',
    logoutError: 'No pudimos cerrar la sesión. Vuelve a intentar.',
    skipToContent: 'Saltar al contenido',
    brandAlt: 'Logo de Rumbo: cóndor andino',
    tagline: 'Tu operación, al día',
    language: 'Idioma',
    languageEs: 'Español',
    languageEn: 'English',
  },
  errors: {
    network: 'No pudimos conectar. Revisa tu conexión y vuelve a intentar.',
    unknown: 'No fue posible completar la operación.',
    demoUnavailable: 'La vista de ejemplo solo está disponible durante el desarrollo.',
    notFound: {
      title: 'No encontramos esta página',
      text: 'Puede que el enlace esté mal escrito o que la página ya no exista.',
      action: 'Volver al panel',
    },
  },
  /** Textos de las pantallas provisionales; cada página los reemplaza por su propia sección. */
  placeholder: {
    underConstruction: 'Pantalla en construcción.',
    login: { title: 'Entra a tu operación' },
    panel: { title: 'Panel', subtitle: 'Aquí verás cómo va tu operación ahora.' },
    trips: { title: 'Viajes', subtitle: 'Aquí verás tus viajes y en qué van.' },
    newTrip: { title: 'Nuevo viaje', subtitle: 'Aquí registrarás un viaje nuevo.' },
    tripDetail: { title: 'Detalle del viaje', subtitle: 'Aquí verás dónde va este camión.' },
    fleet: { title: 'Flota', subtitle: 'Aquí verás dónde están tus vehículos.' },
    settings: { title: 'Ajustes', subtitle: 'Aquí revisarás la conexión con Satrack.' },
  },
  // Secciones por pantalla: las rellena cada agente de página (en es.ts y en en.ts).
  login: {},
  panel: {},
  trips: {},
  newTrip: {},
  tripDetail: {},
  fleet: {},
  settings: {},
}

/** Forma de todos los diccionarios: `en` y futuros idiomas deben cumplirla. */
export type Messages = typeof es
