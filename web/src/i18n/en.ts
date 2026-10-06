import type { Messages } from './es'

/**
 * English dictionary. It must match `es.ts` key by key (type `Messages`).
 * Copy rules: plain operational language, sentence case, buttons = verb + object ("Save trip"),
 * placeholders "e.g. …", no emoji. Domain terms: manifiesto → manifest, remesa → consignment note,
 * cumplido → proof of delivery, placa → plate, transportadora → carrier,
 * coordinador de tráfico → traffic coordinator. The brand wordmark "Rumbo" is never translated.
 */
export const en: Messages = {
  common: {
    wait: 'Wait...',
    loading: 'Loading…',
    retry: 'Try again',
    back: 'Back',
    noData: 'No data',
    time: {
      unavailable: 'GPS time not available',
      ahead: 'GPS time is ahead',
      justNow: 'Just now',
      minutes: '{count} min ago',
      hours: '{count} h ago',
      days: { one: '{count} day ago', other: '{count} days ago' },
    },
  },
  nav: {
    panel: 'Home',
    trips: 'Trips',
    newTrip: 'New',
    fleet: 'Fleet',
    settings: 'Settings',
    mainLabel: 'Main navigation',
    mobileLabel: 'Mobile navigation',
  },
  status: {
    trip: {
      registrado: 'Unverified',
      programado: 'Scheduled',
      en_ruta: 'On route',
      entregado: 'Delivered',
      cancelado: 'Cancelled',
      unknown: 'To review',
    },
    satrack: {
      ok: 'Connected',
      sin_verificar: 'To verify',
      credenciales_invalidas: 'Check your credentials',
      falla: 'Connection issues',
      unknown: 'To review',
    },
    pill: {
      ok: 'Up to date',
      attention: 'Pending',
      critical: 'Urgent',
      success: 'Paid',
      warning: 'Due soon',
      accent: 'New',
    },
    severity: {
      attention: 'Attention',
      critical: 'Urgent',
    },
  },
  auth: {
    loading: 'Loading your operation…',
    sessionError: "We couldn't check your session. Try again.",
  },
  layout: {
    trafficControl: 'Traffic control',
    logout: 'Log out',
    logoutError: "We couldn't log you out. Try again.",
    skipToContent: 'Skip to content',
    brandAlt: 'Rumbo logo: Andean condor',
    tagline: 'Your operation, up to date',
    language: 'Language',
    languageEs: 'Español',
    languageEn: 'English',
  },
  errors: {
    network: "We couldn't connect. Check your connection and try again.",
    unknown: "We couldn't complete the operation.",
    demoUnavailable: 'The sample view is only available during development.',
    notFound: {
      title: "We couldn't find this page",
      text: 'The link may be mistyped or the page no longer exists.',
      action: 'Back to home',
    },
  },
  placeholder: {
    underConstruction: 'Screen under construction.',
    login: { title: 'Sign in to your operation' },
    panel: { title: 'Home', subtitle: "Here you'll see how your operation is going right now." },
    trips: { title: 'Trips', subtitle: "Here you'll see your trips and where each one stands." },
    newTrip: { title: 'New trip', subtitle: "Here you'll register a new trip." },
    tripDetail: { title: 'Trip details', subtitle: "Here you'll see where this truck is." },
    fleet: { title: 'Fleet', subtitle: "Here you'll see where your vehicles are." },
    settings: { title: 'Settings', subtitle: "Here you'll check the Satrack connection." },
  },
  login: {},
  panel: {},
  trips: {},
  newTrip: {},
  tripDetail: {},
  fleet: {},
  settings: {},
}
