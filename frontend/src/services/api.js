/**
 * App data API — offline-first by default (localStorage).
 * Set VITE_USE_API=true to talk to the FastAPI backend instead.
 */
import axios from 'axios'
import { localStore } from './localStore.js'

const useApi = String(import.meta.env.VITE_USE_API || '').toLowerCase() === 'true'
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 8000
})

async function withFallback(remote, local) {
  if (!useApi) return local()
  try {
    return await remote()
  } catch (error) {
    console.warn('API unavailable, using on-device storage', error?.message || error)
    return local()
  }
}

export const fetchCommuteWalks = async (limit = null) =>
  withFallback(
    async () => {
      const params = {}
      if (limit != null) params.limit = limit
      const response = await api.get('/commute/walks', { params })
      return response.data
    },
    () => localStore.listWalks(limit)
  )

export const fetchCommuteStats = async () =>
  withFallback(
    async () => (await api.get('/commute/stats')).data,
    () => localStore.getStats()
  )

export const fetchCommuteSettings = async () =>
  withFallback(
    async () => (await api.get('/commute/settings')).data,
    () => localStore.getSettings()
  )

export const updateCommuteSettings = async (settings) =>
  withFallback(
    async () => (await api.put('/commute/settings', settings)).data,
    () => localStore.updateSettings(settings)
  )

export const createCommuteWalk = async (payload) =>
  withFallback(
    async () => (await api.post('/commute/walks', payload)).data,
    () => localStore.createWalk(payload)
  )

export const updateCommuteWalk = async (walkId, payload) =>
  withFallback(
    async () => (await api.patch(`/commute/walks/${walkId}`, payload)).data,
    () => {
      const walk = localStore.updateWalk(walkId, payload)
      if (!walk) throw new Error('Walk not found')
      return walk
    }
  )

export const appendCommutePoints = async (walkId, points) =>
  withFallback(
    async () => (await api.post(`/commute/walks/${walkId}/points`, { points })).data,
    () => {
      const walk = localStore.appendPoints(walkId, points)
      if (!walk) throw new Error('Walk not found')
      return walk
    }
  )

export const deleteCommuteWalk = async (walkId) =>
  withFallback(
    async () => (await api.delete(`/commute/walks/${walkId}`)).data,
    () => {
      if (!localStore.deleteWalk(walkId)) throw new Error('Walk not found')
      return { ok: true, id: walkId }
    }
  )

export const isOfflineFirst = !useApi
