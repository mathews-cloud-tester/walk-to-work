/**
 * Lightweight checks for on-device localStore (run with: node --experimental-vm-modules or via vite-node).
 * These run in Node with a localStorage polyfill.
 */
import assert from 'node:assert/strict'
import { localStore } from '../src/services/localStore.js'

const mem = new Map()
globalThis.localStorage = {
  getItem: (k) => (mem.has(k) ? mem.get(k) : null),
  setItem: (k, v) => mem.set(k, String(v)),
  removeItem: (k) => mem.delete(k),
  clear: () => mem.clear()
}

mem.clear()

const walk = localStore.createWalk({
  direction: 'to_work',
  points: [
    { lat: 40.7, lng: -74.0 },
    { lat: 40.701, lng: -74.0 }
  ]
})
assert.ok(walk.id)
assert.equal(walk.status, 'in_progress')
assert.ok(walk.distance_meters > 0)

localStore.appendPoints(walk.id, [{ lat: 40.702, lng: -74.001 }])
const updated = localStore.updateWalk(walk.id, {
  status: 'completed',
  ended_at: new Date(Date.parse(walk.started_at) + 30 * 60 * 1000).toISOString()
})
assert.equal(updated.status, 'completed')
assert.equal(updated.duration_seconds, 1800)

const stats = localStore.getStats()
assert.equal(stats.total_walks, 1)
assert.ok(stats.total_distance_meters > 0)

const defaults = localStore.getSettings()
assert.equal(defaults.home_label, '959 Lombard St')
assert.equal(defaults.home_lat, 37.801945)
assert.ok(String(defaults.home_address || '').includes('Lombard'))

localStore.updateSettings({ home_label: 'Apt', work_label: 'Office' })
assert.equal(localStore.getSettings().home_label, 'Apt')

assert.equal(localStore.deleteWalk(walk.id), true)
assert.equal(localStore.listWalks().total, 0)

console.log('localStore checks passed')
