/**
 * Offline-first commute store backed by localStorage.
 * Works as a standalone phone app without a backend.
 */

import { defaultSettings } from '../config/places.js'

const STORAGE_KEY = 'walk-to-work:v1'

function utcNowIso() {
  return new Date().toISOString()
}

function uuid() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  return `walk-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function haversineMeters(lat1, lon1, lat2, lon2) {
  const r = 6371000
  const toRad = (d) => (d * Math.PI) / 180
  const dPhi = toRad(lat2 - lat1)
  const dLambda = toRad(lon2 - lon1)
  const a =
    Math.sin(dPhi / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLambda / 2) ** 2
  return 2 * r * Math.asin(Math.sqrt(a))
}

function pathDistanceMeters(points) {
  let total = 0
  for (let i = 1; i < points.length; i++) {
    total += haversineMeters(
      points[i - 1].lat,
      points[i - 1].lng,
      points[i].lat,
      points[i].lng
    )
  }
  return total
}

function defaultState() {
  return {
    walks: [],
    settings: defaultSettings()
  }
}

function readState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return defaultState()
    const parsed = JSON.parse(raw)
    const defaults = defaultSettings()
    const settings = { ...defaults, ...(parsed.settings || {}) }
    // Upgrade older installs that still have blank home coords
    if (settings.home_lat == null && settings.home_lng == null) {
      settings.home_label = settings.home_label === 'Home' ? defaults.home_label : settings.home_label
      settings.home_address = settings.home_address || defaults.home_address
      settings.home_lat = defaults.home_lat
      settings.home_lng = defaults.home_lng
    }
    return {
      walks: Array.isArray(parsed.walks) ? parsed.walks : [],
      settings
    }
  } catch {
    return defaultState()
  }
}

function writeState(state) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
}

function computeStats(walks) {
  const completed = walks.filter((w) => w.status === 'completed')
  const totalDistance = completed.reduce((s, w) => s + (w.distance_meters || 0), 0)
  const totalDuration = completed.reduce((s, w) => s + (w.duration_seconds || 0), 0)
  const count = completed.length
  const daySet = new Set(
    completed
      .map((w) => (w.started_at ? new Date(w.started_at).toISOString().slice(0, 10) : null))
      .filter(Boolean)
  )
  let streak = 0
  if (daySet.size) {
    const today = new Date()
    const todayKey = today.toISOString().slice(0, 10)
    const yesterday = new Date(today)
    yesterday.setUTCDate(yesterday.getUTCDate() - 1)
    const yesterdayKey = yesterday.toISOString().slice(0, 10)
    let cursor = daySet.has(todayKey) ? today : daySet.has(yesterdayKey) ? yesterday : null
    while (cursor) {
      const key = cursor.toISOString().slice(0, 10)
      if (!daySet.has(key)) break
      streak += 1
      cursor = new Date(cursor)
      cursor.setUTCDate(cursor.getUTCDate() - 1)
    }
  }
  return {
    total_walks: count,
    total_distance_meters: Math.round(totalDistance * 100) / 100,
    total_duration_seconds: totalDuration,
    average_distance_meters: count ? Math.round((totalDistance / count) * 100) / 100 : 0,
    average_duration_seconds: count ? Math.round((totalDuration / count) * 10) / 10 : 0,
    current_streak_days: streak,
    walks_to_work: completed.filter((w) => w.direction === 'to_work').length,
    walks_to_home: completed.filter((w) => w.direction === 'to_home').length
  }
}

export const localStore = {
  getSettings() {
    return { ...readState().settings }
  },

  updateSettings(settings) {
    const state = readState()
    state.settings = { ...state.settings, ...settings }
    writeState(state)
    return { ...state.settings }
  },

  listWalks(limit = null) {
    const walks = [...readState().walks].sort((a, b) =>
      (b.started_at || '').localeCompare(a.started_at || '')
    )
    const total = walks.length
    return { walks: limit != null ? walks.slice(0, limit) : walks, total }
  },

  getWalk(id) {
    return readState().walks.find((w) => w.id === id) || null
  },

  createWalk(payload = {}) {
    const state = readState()
    const points = Array.isArray(payload.points) ? [...payload.points] : []
    const walk = {
      id: uuid(),
      started_at: payload.started_at || utcNowIso(),
      ended_at: null,
      status: 'in_progress',
      direction: payload.direction || 'to_work',
      notes: payload.notes || null,
      points,
      distance_meters: Math.round(pathDistanceMeters(points) * 100) / 100,
      duration_seconds: 0
    }
    state.walks.push(walk)
    writeState(state)
    return { ...walk, points: [...walk.points] }
  },

  updateWalk(id, payload = {}) {
    const state = readState()
    const idx = state.walks.findIndex((w) => w.id === id)
    if (idx < 0) return null
    const walk = { ...state.walks[idx], points: [...(state.walks[idx].points || [])] }

    if (payload.points != null) walk.points = [...payload.points]
    if (payload.notes != null) walk.notes = payload.notes
    if (payload.direction != null) walk.direction = payload.direction
    if (payload.status != null) walk.status = payload.status

    walk.distance_meters = Math.round(pathDistanceMeters(walk.points) * 100) / 100

    if (walk.status === 'completed') {
      walk.ended_at = payload.ended_at || walk.ended_at || utcNowIso()
      const start = Date.parse(walk.started_at)
      const end = Date.parse(walk.ended_at)
      walk.duration_seconds =
        Number.isFinite(start) && Number.isFinite(end) ? Math.max(0, Math.floor((end - start) / 1000)) : 0
    } else if (walk.status === 'cancelled') {
      walk.ended_at = payload.ended_at || walk.ended_at || utcNowIso()
      walk.duration_seconds = 0
    }

    state.walks[idx] = walk
    writeState(state)
    return { ...walk, points: [...walk.points] }
  },

  appendPoints(id, points) {
    const state = readState()
    const idx = state.walks.findIndex((w) => w.id === id)
    if (idx < 0) return null
    const walk = { ...state.walks[idx], points: [...(state.walks[idx].points || [])] }
    if (walk.status !== 'in_progress') return walk
    walk.points.push(...points)
    walk.distance_meters = Math.round(pathDistanceMeters(walk.points) * 100) / 100
    state.walks[idx] = walk
    writeState(state)
    return { ...walk, points: [...walk.points] }
  },

  deleteWalk(id) {
    const state = readState()
    const before = state.walks.length
    state.walks = state.walks.filter((w) => w.id !== id)
    if (state.walks.length === before) return false
    writeState(state)
    return true
  },

  getStats() {
    return computeStats(readState().walks)
  }
}
