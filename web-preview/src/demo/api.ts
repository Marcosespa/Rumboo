import type {Account, Driver, Page, Panel, Position, Remesa, Trip, TripInput, TripState, User, Vehicle} from '../api/types'

const DATA_KEY = 'rumboo.demo.data'
const user: User = {id: 1, usuario: 'marcos', nombre: 'Marcos', transportadora: {id: 1, nombre: 'Transportes del camino'}}
const colombia = [
  {lat: 4.711, lng: -74.0721, city: 'Bogotá'},
  {lat: 6.2442, lng: -75.5812, city: 'Medellín'},
  {lat: 3.4516, lng: -76.532, city: 'Cali'},
  {lat: 10.9639, lng: -74.7964, city: 'Barranquilla'},
  {lat: 7.1193, lng: -73.1227, city: 'Bucaramanga'},
]
const seedDrivers: Driver[] = [
  {id: 1, nombre: 'Carlos Rojas', cedula: '7956412380', telefono: '3005550101', autoriza_contacto: true},
  {id: 2, nombre: 'María Fernanda Díaz', cedula: '5234187690', telefono: '3015550102', autoriza_contacto: true},
  {id: 3, nombre: 'Jorge Andrés López', cedula: '8012675430', telefono: '3025550103', autoriza_contacto: false},
  {id: 4, nombre: 'Luz Marina Torres', cedula: '4387651209', telefono: '3105550104', autoriza_contacto: true},
  {id: 5, nombre: 'Óscar Ramírez', cedula: '7123409856', telefono: '3115550105', autoriza_contacto: false},
]
type DemoEvent = {id: number; tipo: string; detalle: Record<string, unknown>; creado_en: string; usuario_id: number | null}
type DemoTrip = Trip & {remesas: Remesa[]; eventos: DemoEvent[]}
type DemoState = {trips: DemoTrip[]; account: Account; nextTripId: number; nextDriverId: number; nextVehicleId: number; nextEventId: number; nextPositionId: number}

export class DemoApiError extends Error {
  constructor(public status: number, message: string, public errores: {campo: string; mensaje: string}[] = []) {super(message)}
}

const nowIso = (offsetMinutes = 0) => new Date(Date.now() + offsetMinutes * 60000).toISOString()
const remesas = (base: string, client: string, weight: number): Remesa[] => [
  {numero: `R-${base}-01`, cliente: client, peso_kg: weight, cantidad: 18},
  {numero: `R-${base}-02`, cliente: `${client} · segunda entrega`, peso_kg: Math.round(weight * .4), cantidad: 8},
]

function makePosition(id: number, tripId: number, point: number, offsetMinutes: number): Position {
  const city = colombia[tripId % colombia.length]
  const delta = point === 0 ? -.1 : .08
  const reported = nowIso(offsetMinutes)
  return {id, lat: city.lat + delta, lng: city.lng + delta, velocidad_kmh: point === 0 ? 48 : 0, direccion: point === 0 ? `Vía ${city.city} · muestra de recorrido` : `Zona urbana de ${city.city}`, estado_gps: 'ok', reportado_en: reported, capturado_en: reported, reportado_texto: new Intl.DateTimeFormat('es-CO', {dateStyle: 'medium', timeStyle: 'short', timeZone: 'America/Bogota'}).format(new Date(reported)), viaje_id: tripId}
}

function makeTrip(id: number, state: TripState, driver: Driver, weight: number, point: number, departureOffset: number, arrivalOffset: number): DemoTrip {
  const cargo = remesas(String(2026 + id), ['Alimentos del Valle', 'Distribuciones Andinas', 'Comercializadora La 14', 'Mercados del Norte', 'Suministros El Camino'][id - 1], weight)
  const created = nowIso(departureOffset - 180)
  const position = state === 'en_ruta' || state === 'entregado' ? makePosition(id, id, 1, -23 - id * 2) : null
  const vehicle: Vehicle = {id, placa: ['JKL123', 'MNP456', 'RST789', 'ABC234', 'DEF567'][id - 1], propietario: 'Transportes del camino', en_satelital: true, ultima_posicion: position}
  return {
    id, manifiesto: `MC-${String(id).padStart(3, '0')}-2026`, origen: ['Bogotá', 'Medellín', 'Cali', 'Barranquilla', 'Bucaramanga'][id - 1], destino: ['Medellín', 'Cali', 'Pereira', 'Cartagena', 'Bogotá'][id - 1],
    estado: state, salida_estimada: nowIso(departureOffset), llegada_estimada: nowIso(arrivalOffset), peso_salida_kg: cargo.reduce((sum, item) => sum + item.peso_kg, 0), creado_en: created, actualizado_en: state === 'entregado' ? nowIso(-90) : created,
    conductor: driver, vehiculo: vehicle, remesas: cargo,
    eventos: [{id: id, tipo: 'viaje_creado', detalle: {estado: state}, creado_en: created, usuario_id: 1}],
  }
}

function freshState(): DemoState {
  const trips = [
    makeTrip(1, 'en_ruta', seedDrivers[0], 8200, 0, -150, 120),
    makeTrip(2, 'programado', seedDrivers[1], 6400, 1, 210, 430),
    makeTrip(3, 'registrado', seedDrivers[2], 5100, 2, 600, 820),
    makeTrip(4, 'entregado', seedDrivers[3], 4700, 3, -260, -80),
    makeTrip(5, 'en_ruta', seedDrivers[4], 7200, 4, -90, 190),
  ]
  // Add a second point to the active routes so trip detail previews a plausible path.
  for (const trip of trips.filter(item => item.estado === 'en_ruta')) {
    const first = makePosition(trip.id * 10, trip.id, 0, -58 - trip.id * 2)
    trip.eventos = trip.eventos || []
    if (trip.vehiculo.ultima_posicion) trip.vehiculo.ultima_posicion = {...trip.vehiculo.ultima_posicion, lat: colombia[trip.id % colombia.length].lat, lng: colombia[trip.id % colombia.length].lng}
    ;(trip as DemoTrip & {demoPositions?: Position[]}).demoPositions = [first, trip.vehiculo.ultima_posicion!]
  }
  const account: Account = {id: 1, usuario: 'operaciones_demo', proveedor: 'satrack', estado: 'ok', ultima_consulta_ok: nowIso(-22), ultimo_error: null, backoff_hasta: null, fallos_consecutivos: 0, consulta_pendiente: false}
  return {trips, account, nextTripId: 6, nextDriverId: 6, nextVehicleId: 6, nextEventId: 6, nextPositionId: 100}
}

function readState(): DemoState {
  const stored = sessionStorage.getItem(DATA_KEY)
  if (stored) {
    try {return JSON.parse(stored) as DemoState} catch {sessionStorage.removeItem(DATA_KEY)}
  }
  const state = freshState()
  writeState(state)
  return state
}
function writeState(state: DemoState) {sessionStorage.setItem(DATA_KEY, JSON.stringify(state))}
export function clearDemoData() {sessionStorage.removeItem(DATA_KEY)}
export function hasDemoData() {return sessionStorage.getItem(DATA_KEY) !== null}

const copy = <T,>(value: T): T => JSON.parse(JSON.stringify(value)) as T
const bodyOf = (options: RequestInit) => {
  if (!options.body) return {}
  try {return JSON.parse(String(options.body)) as Record<string, unknown>} catch {throw new DemoApiError(400, 'No pudimos leer los datos enviados.')}
}
const fail = (status: number, message: string, errores: {campo: string; mensaje: string}[] = []): never => {throw new DemoApiError(status, message, errores)}

function getPositions(trip: DemoTrip, state: DemoState): Position[] {
  const saved = (trip as DemoTrip & {demoPositions?: Position[]}).demoPositions
  if (saved) return saved
  return trip.vehiculo.ultima_posicion ? [trip.vehiculo.ultima_posicion] : []
}

export async function handleDemoApi<T>(path: string, options: RequestInit = {}): Promise<T> {
  const method = (options.method || 'GET').toUpperCase()
  const [pathname, query = ''] = path.split('?', 2)
  const params = new URLSearchParams(query)
  const body = bodyOf(options)
  const state = readState()
  let result: unknown

  if (pathname === '/auth/me' && method === 'GET') result = user
  else if (pathname === '/auth/logout' && method === 'POST') result = {status: 'ok'}
  else if (pathname === '/panel' && method === 'GET') {
    const conteos: Record<string, number> = {registrado: 0, programado: 0, en_ruta: 0, entregado: 0, cancelado: 0}
    for (const trip of state.trips) conteos[trip.estado] = (conteos[trip.estado] || 0) + 1
    result = {conteos, entregados_hoy: state.trips.filter(trip => trip.estado === 'entregado').length, vehiculos_con_posicion: state.trips.filter(trip => trip.vehiculo.ultima_posicion?.lat != null && trip.vehiculo.ultima_posicion.lng != null).length, cuenta_satelital: state.account, viajes_activos: state.trips.filter(trip => ['registrado', 'programado', 'en_ruta'].includes(trip.estado)).sort((a, b) => b.id - a.id).slice(0, 10)} satisfies Panel
  } else if (pathname === '/vehiculos' && method === 'GET') result = state.trips.map(trip => trip.vehiculo).sort((a, b) => a.placa.localeCompare(b.placa))
  else if (pathname === '/conductores' && method === 'GET') result = state.trips.map(trip => trip.conductor)
  else if (pathname === '/cuenta-satelital' && method === 'GET') result = state.account
  else if (pathname === '/cuenta-satelital' && method === 'PUT') {
    const accountUser = String(body.usuario || '').trim()
    if (!accountUser || !String(body.password || '')) fail(422, 'Revisa los datos de la cuenta.', [{campo: !accountUser ? 'usuario' : 'password', mensaje: !accountUser ? 'Escribe el usuario de Satrack.' : 'Escribe la contraseña de Satrack.'}])
    // The preview never persists the submitted password, even inside this session.
    state.account = {...state.account, usuario: accountUser, estado: 'sin_verificar', ultimo_error: null, fallos_consecutivos: 0, ultima_consulta_ok: null, consulta_pendiente: false}
    writeState(state); result = state.account
  } else if (/^\/cuenta-satelital\/(sincronizar|consultar)$/.test(pathname) && method === 'POST') {
    if (!state.account) fail(409, 'Conecta tu cuenta de Satrack primero.')
    if (pathname.endsWith('/consultar') && !state.trips.some(trip => ['programado', 'en_ruta'].includes(trip.estado))) fail(409, 'No hay viajes próximos o en ruta para consultar.')
    result = {status: 'aceptado', job_id: null}
  } else if (pathname === '/viajes' && method === 'GET') {
    const requestedState = params.get('estado') || '', q = (params.get('q') || '').trim().toLocaleLowerCase('es-CO')
    const page = Math.max(1, Number(params.get('page')) || 1), pageSize = Math.min(100, Math.max(1, Number(params.get('page_size')) || 20))
    const filtered = state.trips.filter(trip => (!requestedState || trip.estado === requestedState) && (!q || `${trip.manifiesto} ${trip.vehiculo.placa} ${trip.conductor.nombre}`.toLocaleLowerCase('es-CO').includes(q))).sort((a, b) => b.id - a.id)
    result = {items: filtered.slice((page - 1) * pageSize, page * pageSize), total: filtered.length, page, page_size: pageSize} satisfies Page<Trip>
  } else if (pathname === '/viajes' && method === 'POST') {
    const input = body as unknown as TripInput
    const errors: {campo: string; mensaje: string}[] = []
    if (!input.manifiesto?.trim()) errors.push({campo: 'manifiesto', mensaje: 'Escribe el número de manifiesto.'})
    if (!input.origen?.trim()) errors.push({campo: 'origen', mensaje: 'Escribe el origen.'})
    if (!input.destino?.trim()) errors.push({campo: 'destino', mensaje: 'Escribe el destino.'})
    if (input.origen?.trim().toLocaleLowerCase() === input.destino?.trim().toLocaleLowerCase()) errors.push({campo: 'destino', mensaje: 'El origen y el destino deben ser distintos.'})
    const departure = new Date(input.salida_estimada).getTime(), arrival = new Date(input.llegada_estimada).getTime()
    if (!Number.isFinite(departure)) errors.push({campo: 'salida_estimada', mensaje: 'Escribe una fecha de salida válida.'})
    if (!Number.isFinite(arrival) || arrival <= departure) errors.push({campo: 'llegada_estimada', mensaje: 'La llegada debe ser posterior a la salida.'})
    if (!input.conductor?.nombre?.trim()) errors.push({campo: 'conductor.nombre', mensaje: 'Escribe el nombre del conductor.'})
    if (!/^\d{6,10}$/.test(input.conductor?.cedula || '')) errors.push({campo: 'conductor.cedula', mensaje: 'Escribe una cédula de 6 a 10 números.'})
    if (!/^\d{10}$/.test((input.conductor?.telefono || '').replace(/\D/g, ''))) errors.push({campo: 'conductor.telefono', mensaje: 'Escribe un celular válido.'})
    if (!/^[A-Za-z]{3}[- ]?\d{3}$/.test(input.vehiculo?.placa || '')) errors.push({campo: 'vehiculo.placa', mensaje: 'Escribe una placa colombiana válida.'})
    if (!input.remesas?.length) errors.push({campo: 'remesas.0.numero', mensaje: 'Agrega al menos una remesa.'})
    input.remesas?.forEach((item, index) => {
      if (!item.numero?.trim()) errors.push({campo: `remesas.${index}.numero`, mensaje: 'Escribe el número de la remesa.'})
      if (!item.cliente?.trim()) errors.push({campo: `remesas.${index}.cliente`, mensaje: 'Escribe el nombre del cliente.'})
      if (!Number.isFinite(item.peso_kg) || item.peso_kg <= 0 || item.peso_kg > 100000) errors.push({campo: `remesas.${index}.peso_kg`, mensaje: 'El peso debe ser mayor que cero y no superar 100.000 kg.'})
      if (item.cantidad != null && (!Number.isInteger(item.cantidad) || item.cantidad <= 0)) errors.push({campo: `remesas.${index}.cantidad`, mensaje: 'La cantidad debe ser un número entero mayor que cero.'})
    })
    if (errors.length) fail(422, 'Revisa los datos del viaje.', errors)
    if (state.trips.some(trip => trip.manifiesto.toLocaleLowerCase() === input.manifiesto.trim().toLocaleLowerCase())) fail(409, 'Ya existe un viaje con ese manifiesto.')
    const placa = input.vehiculo.placa.replace(/[- ]/g, '').toLocaleUpperCase()
    if (state.trips.some(trip => trip.estado === 'programado' || trip.estado === 'en_ruta' || trip.estado === 'registrado' && trip.vehiculo.placa === placa)) {
      const existing = state.trips.find(trip => trip.vehiculo.placa === placa && ['registrado', 'programado', 'en_ruta'].includes(trip.estado))
      if (existing) fail(409, 'El vehículo ya tiene un viaje activo.')
    }
    const driver: Driver = {id: state.nextDriverId++, ...input.conductor}
    const positionVehicle: Vehicle = {id: state.nextVehicleId++, placa, propietario: input.vehiculo.propietario || '', en_satelital: null, ultima_posicion: null}
    const id = state.nextTripId++, created = nowIso()
    const cargo = input.remesas.map(item => ({...item, peso_kg: Number(item.peso_kg)}))
    const trip: DemoTrip = {id, manifiesto: input.manifiesto.trim(), origen: input.origen.trim(), destino: input.destino.trim(), estado: 'registrado', salida_estimada: input.salida_estimada, llegada_estimada: input.llegada_estimada, peso_salida_kg: cargo.reduce((sum, item) => sum + item.peso_kg, 0), creado_en: created, actualizado_en: created, conductor: driver, vehiculo: positionVehicle, remesas: cargo, eventos: [{id: state.nextEventId++, tipo: 'viaje_creado', detalle: {estado: 'registrado'}, creado_en: created, usuario_id: user.id}]}
    state.trips.push(trip); writeState(state); result = trip
  } else {
    const tripPath = pathname.match(/^\/viajes\/(\d+)(?:\/(posiciones|transiciones))?$/)
    if (tripPath) {
      const trip = state.trips.find(item => item.id === Number(tripPath[1]))
      if (!trip) fail(404, 'No encontramos este viaje.')
      if (!tripPath[2] && method === 'GET') result = trip
      else if (tripPath[2] === 'posiciones' && method === 'GET') result = getPositions(trip, state)
      else if (tripPath[2] === 'transiciones' && method === 'POST') {
        const nextState = String(body.estado) as TripState, reason = String(body.motivo || '').trim()
        const allowed: Record<string, string[]> = {registrado: ['cancelado'], programado: ['en_ruta', 'cancelado'], en_ruta: ['entregado', 'cancelado']}
        if (!allowed[trip.estado]?.includes(nextState)) fail(409, 'Ese cambio no está permitido desde el estado actual.')
        if (nextState === 'cancelado' && !reason) fail(422, 'Escribe el motivo de cancelación.', [{campo: 'motivo', mensaje: 'Escribe el motivo de cancelación.'}])
        const previous = trip.estado, changedAt = nowIso()
        trip.estado = nextState; trip.actualizado_en = changedAt
        const detail: Record<string, unknown> = {anterior: previous, estado: nextState, motivo: reason || 'Acción manual del operador'}
        trip.eventos.unshift({id: state.nextEventId++, tipo: 'estado_actualizado', detalle: detail, creado_en: changedAt, usuario_id: user.id})
        if (nextState === 'cancelado') detail.motivo = reason
        writeState(state); result = trip
      } else fail(405, 'Esta acción no está disponible en la vista de ejemplo.')
    } else if (pathname === '/posiciones' && method === 'GET') result = state.trips.flatMap(trip => getPositions(trip, state))
    else fail(404, 'Esta operación no está disponible en la vista de ejemplo.')
  }
  return copy(result) as T
}
