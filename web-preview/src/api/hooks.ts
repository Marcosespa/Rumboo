import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, post } from './client'
import type { Account, Page, Panel, Position, Trip, TripInput, Vehicle } from './types'
export const usePanel = () => useQuery({queryKey: ['panel'], queryFn: () => api<Panel>('/panel'), refetchInterval: 60000})
export const useFleet = () => useQuery({queryKey: ['flota'], queryFn: () => api<Vehicle[]>('/vehiculos'), refetchInterval: 60000})
export const useAccount = () => useQuery({queryKey: ['cuenta'], queryFn: () => api<Account | null>('/cuenta-satelital'), refetchInterval: 5000})
export const useTrips = (state: string, q: string, page: number) => useQuery({queryKey: ['viajes', state, q, page], queryFn: () => api<Page<Trip>>(`/viajes?estado=${encodeURIComponent(state)}&q=${encodeURIComponent(q)}&page=${page}`), refetchInterval: 60000})
export const useTrip = (id: string) => useQuery({queryKey: ['viaje', id], queryFn: () => api<Trip>(`/viajes/${id}`), refetchInterval: 60000})
export const usePositions = (id: string) => useQuery({queryKey: ['posiciones', id], queryFn: () => api<Position[]>(`/viajes/${id}/posiciones`), refetchInterval: 60000})
export function useCreateTrip() {
  const client = useQueryClient()
  return useMutation({mutationFn: (data: TripInput) => post<Trip>('/viajes', data), onSuccess: () => client.invalidateQueries()})
}
export function useSatelliteAction(kind: 'sincronizar' | 'consultar') {
  const client = useQueryClient()
  return useMutation({mutationFn: () => post(`/cuenta-satelital/${kind}`), onSuccess: () => client.invalidateQueries()})
}
