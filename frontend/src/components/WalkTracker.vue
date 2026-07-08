<template>
  <div class="walk-tracker">
    <div v-if="pageError" class="error banner-error">
      <p>{{ pageError }}</p>
      <button @click="refreshAll">Retry</button>
    </div>

    <!-- Live tracking panel -->
    <section class="track-panel" :class="{ live: isTracking }">
      <div class="track-status">
        <div class="status-pill" :class="statusClass">
          <span class="pulse" v-if="isTracking"></span>
          {{ statusLabel }}
        </div>
        <div class="direction-toggle" v-if="!isTracking">
          <button
            type="button"
            :class="{ active: direction === 'to_work' }"
            @click="direction = 'to_work'"
          >
            <Briefcase :size="16" :stroke-width="2" />
            To work
          </button>
          <button
            type="button"
            :class="{ active: direction === 'to_home' }"
            @click="direction = 'to_home'"
          >
            <Home :size="16" :stroke-width="2" />
            To home
          </button>
        </div>
        <div v-else class="direction-live">
          {{ direction === 'to_work' ? 'Heading to work' : 'Heading home' }}
        </div>
      </div>

      <div class="live-metrics">
        <div class="metric">
          <div class="metric-label">Distance</div>
          <div class="metric-value">{{ formatDistance(liveDistance) }}</div>
        </div>
        <div class="metric">
          <div class="metric-label">Duration</div>
          <div class="metric-value">{{ formatDuration(liveDuration) }}</div>
        </div>
        <div class="metric">
          <div class="metric-label">Points</div>
          <div class="metric-value">{{ livePoints.length }}</div>
        </div>
      </div>

      <div class="track-actions">
        <button
          v-if="!isTracking"
          class="btn primary"
          :disabled="starting"
          @click="startWalk"
        >
          <Play :size="18" :stroke-width="2" />
          {{ starting ? 'Starting…' : 'Start walk' }}
        </button>
        <template v-else>
          <button class="btn danger" :disabled="stopping" @click="finishWalk('completed')">
            <Square :size="18" :stroke-width="2" />
            {{ stopping ? 'Saving…' : 'Finish' }}
          </button>
          <button class="btn ghost" :disabled="stopping" @click="finishWalk('cancelled')">
            Cancel
          </button>
        </template>
      </div>

      <p v-if="geoMessage" class="geo-message" :class="{ warn: geoWarn }">{{ geoMessage }}</p>
    </section>

    <!-- Stats -->
    <section class="stats-row" v-if="stats">
      <div class="stat-card">
        <div class="stat-icon"><Footprints :size="24" :stroke-width="2" /></div>
        <div>
          <div class="stat-label">Walks</div>
          <div class="stat-value">{{ stats.total_walks }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><MapPin :size="24" :stroke-width="2" /></div>
        <div>
          <div class="stat-label">Total distance</div>
          <div class="stat-value">{{ formatDistance(stats.total_distance_meters) }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><Timer :size="24" :stroke-width="2" /></div>
        <div>
          <div class="stat-label">Avg duration</div>
          <div class="stat-value">{{ formatDuration(Math.round(stats.average_duration_seconds)) }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><Flame :size="24" :stroke-width="2" /></div>
        <div>
          <div class="stat-label">Streak</div>
          <div class="stat-value">{{ stats.current_streak_days }} day{{ stats.current_streak_days === 1 ? '' : 's' }}</div>
        </div>
      </div>
    </section>

    <!-- Settings -->
    <section class="settings-panel">
      <button type="button" class="settings-toggle" @click="showSettings = !showSettings">
        <Settings :size="18" :stroke-width="2" />
        {{ showSettings ? 'Hide' : 'Edit' }} home &amp; work
      </button>
      <div v-if="showSettings" class="settings-form">
        <div class="form-grid">
          <label>
            Home label
            <input v-model="settingsForm.home_label" type="text" />
          </label>
          <label>
            Work label
            <input v-model="settingsForm.work_label" type="text" />
          </label>
          <label>
            Home lat
            <input v-model.number="settingsForm.home_lat" type="number" step="any" placeholder="optional" />
          </label>
          <label>
            Home lng
            <input v-model.number="settingsForm.home_lng" type="number" step="any" placeholder="optional" />
          </label>
          <label>
            Work lat
            <input v-model.number="settingsForm.work_lat" type="number" step="any" placeholder="optional" />
          </label>
          <label>
            Work lng
            <input v-model.number="settingsForm.work_lng" type="number" step="any" placeholder="optional" />
          </label>
        </div>
        <div class="settings-actions">
          <button class="btn secondary" type="button" @click="useCurrentAs('home')" :disabled="!lastPosition">
            Use current as home
          </button>
          <button class="btn secondary" type="button" @click="useCurrentAs('work')" :disabled="!lastPosition">
            Use current as work
          </button>
          <button class="btn primary" type="button" :disabled="savingSettings" @click="saveSettings">
            {{ savingSettings ? 'Saving…' : 'Save settings' }}
          </button>
        </div>
        <p v-if="settingsMessage" class="geo-message">{{ settingsMessage }}</p>
      </div>
    </section>

    <!-- Path sketch -->
    <section class="path-panel" v-if="displayPoints.length > 0">
      <h3>{{ isTracking ? 'Live path' : 'Last route' }}</h3>
      <svg class="path-svg" viewBox="0 0 320 180" role="img" aria-label="Walk path sketch">
        <rect x="0" y="0" width="320" height="180" class="path-bg" />
        <polyline
          v-if="pathPolyline"
          :points="pathPolyline"
          class="path-line"
          fill="none"
        />
        <circle
          v-if="pathEndpoints.start"
          :cx="pathEndpoints.start.x"
          :cy="pathEndpoints.start.y"
          r="5"
          class="path-start"
        />
        <circle
          v-if="pathEndpoints.end"
          :cx="pathEndpoints.end.x"
          :cy="pathEndpoints.end.y"
          r="5"
          class="path-end"
        />
      </svg>
    </section>

    <!-- History -->
    <section class="history">
      <h3>Recent walks</h3>
      <div v-if="loadingHistory" class="loading">
        <div class="spinner"></div>
        <p>Loading walks…</p>
      </div>
      <div v-else-if="walks.length === 0" class="empty">
        No walks yet. Start your first commute above.
      </div>
      <ul v-else class="walk-list">
        <li v-for="walk in walks" :key="walk.id" class="walk-item" :class="walk.status">
          <div class="walk-main">
            <div class="walk-title">
              <span class="walk-dir">{{ walk.direction === 'to_work' ? 'To work' : 'To home' }}</span>
              <span class="walk-status-badge">{{ walk.status.replace('_', ' ') }}</span>
            </div>
            <div class="walk-meta">
              {{ formatDate(walk.started_at) }}
              · {{ formatDistance(walk.distance_meters) }}
              · {{ formatDuration(walk.duration_seconds) }}
            </div>
            <div v-if="walk.notes" class="walk-notes">{{ walk.notes }}</div>
          </div>
          <button
            class="btn icon-btn"
            type="button"
            title="Delete walk"
            @click="removeWalk(walk.id)"
          >
            <Trash2 :size="16" :stroke-width="2" />
          </button>
        </li>
      </ul>
    </section>
  </div>
</template>

<script>
import {
  Briefcase,
  Flame,
  Footprints,
  Home,
  MapPin,
  Play,
  Settings,
  Square,
  Timer,
  Trash2
} from 'lucide-vue-next'
import {
  fetchCommuteWalks,
  fetchCommuteStats,
  fetchCommuteSettings,
  updateCommuteSettings,
  createCommuteWalk,
  updateCommuteWalk,
  appendCommutePoints,
  deleteCommuteWalk
} from '../services/api.js'

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

function pathDistance(points) {
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

export default {
  name: 'WalkTracker',
  components: {
    Briefcase,
    Flame,
    Footprints,
    Home,
    MapPin,
    Play,
    Settings,
    Square,
    Timer,
    Trash2
  },
  data() {
    return {
      direction: 'to_work',
      isTracking: false,
      starting: false,
      stopping: false,
      activeWalkId: null,
      livePoints: [],
      liveStartedAt: null,
      liveTick: 0,
      tickTimer: null,
      watchId: null,
      pointBuffer: [],
      flushTimer: null,
      lastPosition: null,
      geoMessage: '',
      geoWarn: false,
      walks: [],
      stats: null,
      loadingHistory: true,
      pageError: null,
      showSettings: false,
      settingsForm: {
        home_label: 'Home',
        work_label: 'Work',
        home_lat: null,
        home_lng: null,
        work_lat: null,
        work_lng: null,
        typical_distance_meters: null
      },
      savingSettings: false,
      settingsMessage: '',
      previewPoints: []
    }
  },
  computed: {
    liveDistance() {
      return pathDistance(this.livePoints)
    },
    liveDuration() {
      if (!this.liveStartedAt) return 0
      // liveTick forces recompute every second while tracking
      void this.liveTick
      return Math.max(0, Math.floor((Date.now() - this.liveStartedAt) / 1000))
    },
    statusLabel() {
      if (this.isTracking) return 'Walking'
      return 'Ready'
    },
    statusClass() {
      return this.isTracking ? 'live' : 'idle'
    },
    displayPoints() {
      if (this.livePoints.length) return this.livePoints
      return this.previewPoints
    },
    pathPolyline() {
      const pts = this.normalizedPath
      if (pts.length < 2) return ''
      return pts.map((p) => `${p.x},${p.y}`).join(' ')
    },
    pathEndpoints() {
      const pts = this.normalizedPath
      if (!pts.length) return { start: null, end: null }
      return { start: pts[0], end: pts[pts.length - 1] }
    },
    normalizedPath() {
      const points = this.displayPoints
      if (!points.length) return []
      const lats = points.map((p) => p.lat)
      const lngs = points.map((p) => p.lng)
      const minLat = Math.min(...lats)
      const maxLat = Math.max(...lats)
      const minLng = Math.min(...lngs)
      const maxLng = Math.max(...lngs)
      const pad = 24
      const w = 320 - pad * 2
      const h = 180 - pad * 2
      const spanLat = Math.max(maxLat - minLat, 0.0001)
      const spanLng = Math.max(maxLng - minLng, 0.0001)
      return points.map((p) => ({
        x: pad + ((p.lng - minLng) / spanLng) * w,
        y: pad + (1 - (p.lat - minLat) / spanLat) * h
      }))
    }
  },
  mounted() {
    this.refreshAll()
    this.probeLocation()
  },
  beforeUnmount() {
    this.stopWatching()
    this.clearTimers()
  },
  methods: {
    formatDistance(meters) {
      const m = Number(meters) || 0
      if (m < 1000) return `${Math.round(m)} m`
      return `${(m / 1000).toFixed(2)} km`
    },
    formatDuration(seconds) {
      const s = Math.max(0, Number(seconds) || 0)
      const h = Math.floor(s / 3600)
      const m = Math.floor((s % 3600) / 60)
      const sec = s % 60
      if (h > 0) return `${h}h ${m}m`
      if (m > 0) return `${m}m ${sec}s`
      return `${sec}s`
    },
    formatDate(iso) {
      if (!iso) return ''
      try {
        return new Date(iso).toLocaleString(undefined, {
          month: 'short',
          day: 'numeric',
          hour: 'numeric',
          minute: '2-digit'
        })
      } catch {
        return iso
      }
    },
    async refreshAll() {
      this.pageError = null
      this.loadingHistory = true
      try {
        const [walksRes, statsRes, settings] = await Promise.all([
          fetchCommuteWalks(30),
          fetchCommuteStats(),
          fetchCommuteSettings()
        ])
        this.walks = walksRes.walks || []
        this.stats = statsRes
        this.settingsForm = { ...settings }
        const lastCompleted = this.walks.find((w) => w.status === 'completed' && w.points?.length)
        this.previewPoints = lastCompleted ? lastCompleted.points : []
      } catch (err) {
        console.error(err)
        this.pageError = 'Could not load commute data. Is the API running?'
      } finally {
        this.loadingHistory = false
      }
    },
    probeLocation() {
      if (!navigator.geolocation) {
        this.geoMessage = 'Geolocation is not available in this browser.'
        this.geoWarn = true
        return
      }
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          this.lastPosition = pos.coords
          this.geoMessage = 'Location ready — you can start walking.'
          this.geoWarn = false
        },
        (err) => {
          this.geoMessage = this.geoErrorText(err)
          this.geoWarn = true
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
      )
    },
    geoErrorText(err) {
      if (!err) return 'Unable to read location.'
      if (err.code === 1) return 'Location permission denied. Allow location access to track walks.'
      if (err.code === 2) return 'Location unavailable. Try again outdoors or check device GPS.'
      if (err.code === 3) return 'Location request timed out. Try again.'
      return err.message || 'Unable to read location.'
    },
    async startWalk() {
      if (!navigator.geolocation) {
        this.geoMessage = 'Geolocation is not available in this browser.'
        this.geoWarn = true
        return
      }
      this.starting = true
      this.geoMessage = ''
      this.geoWarn = false
      try {
        const walk = await createCommuteWalk({
          direction: this.direction,
          points: []
        })
        this.activeWalkId = walk.id
        this.isTracking = true
        this.livePoints = []
        this.liveStartedAt = Date.now()
        this.liveTick = 0
        this.pointBuffer = []
        this.tickTimer = setInterval(() => {
          this.liveTick += 1
        }, 1000)
        this.flushTimer = setInterval(() => this.flushPoints(), 8000)
        this.watchId = navigator.geolocation.watchPosition(
          (pos) => this.onPosition(pos),
          (err) => {
            this.geoMessage = this.geoErrorText(err)
            this.geoWarn = true
          },
          { enableHighAccuracy: true, maximumAge: 2000, timeout: 15000 }
        )
        this.geoMessage = 'Tracking… keep this tab open while you walk.'
      } catch (err) {
        console.error(err)
        this.geoMessage = 'Failed to start walk. Check the API connection.'
        this.geoWarn = true
      } finally {
        this.starting = false
      }
    },
    onPosition(pos) {
      this.lastPosition = pos.coords
      const point = {
        lat: pos.coords.latitude,
        lng: pos.coords.longitude,
        recorded_at: new Date().toISOString(),
        accuracy_meters: pos.coords.accuracy
      }
      // Skip noisy duplicate points within ~5m
      const last = this.livePoints[this.livePoints.length - 1]
      if (last) {
        const d = haversineMeters(last.lat, last.lng, point.lat, point.lng)
        if (d < 5) return
      }
      this.livePoints.push(point)
      this.pointBuffer.push(point)
    },
    async flushPoints() {
      if (!this.activeWalkId || !this.pointBuffer.length) return
      const batch = this.pointBuffer.splice(0, this.pointBuffer.length)
      try {
        await appendCommutePoints(this.activeWalkId, batch)
      } catch (err) {
        console.error('Failed to flush points', err)
        // Put points back so we can retry
        this.pointBuffer.unshift(...batch)
      }
    },
    async finishWalk(status) {
      this.stopping = true
      try {
        await this.flushPoints()
        this.stopWatching()
        this.clearTimers()
        if (this.activeWalkId) {
          await updateCommuteWalk(this.activeWalkId, {
            status,
            points: this.livePoints,
            ended_at: new Date().toISOString()
          })
        }
        if (status === 'completed' && this.livePoints.length) {
          this.previewPoints = [...this.livePoints]
        }
        this.isTracking = false
        this.activeWalkId = null
        this.livePoints = []
        this.liveStartedAt = null
        this.geoMessage = status === 'completed' ? 'Walk saved.' : 'Walk cancelled.'
        this.geoWarn = false
        await this.refreshAll()
      } catch (err) {
        console.error(err)
        this.geoMessage = 'Could not save walk.'
        this.geoWarn = true
      } finally {
        this.stopping = false
      }
    },
    stopWatching() {
      if (this.watchId != null && navigator.geolocation) {
        navigator.geolocation.clearWatch(this.watchId)
      }
      this.watchId = null
    },
    clearTimers() {
      if (this.tickTimer) clearInterval(this.tickTimer)
      if (this.flushTimer) clearInterval(this.flushTimer)
      this.tickTimer = null
      this.flushTimer = null
    },
    useCurrentAs(kind) {
      if (!this.lastPosition) {
        this.probeLocation()
        this.settingsMessage = 'Waiting for current location…'
        return
      }
      if (kind === 'home') {
        this.settingsForm.home_lat = this.lastPosition.latitude
        this.settingsForm.home_lng = this.lastPosition.longitude
      } else {
        this.settingsForm.work_lat = this.lastPosition.latitude
        this.settingsForm.work_lng = this.lastPosition.longitude
      }
      this.settingsMessage = `Set ${kind} from current location.`
    },
    async saveSettings() {
      this.savingSettings = true
      this.settingsMessage = ''
      try {
        const payload = {
          ...this.settingsForm,
          home_lat: this.settingsForm.home_lat === '' ? null : this.settingsForm.home_lat,
          home_lng: this.settingsForm.home_lng === '' ? null : this.settingsForm.home_lng,
          work_lat: this.settingsForm.work_lat === '' ? null : this.settingsForm.work_lat,
          work_lng: this.settingsForm.work_lng === '' ? null : this.settingsForm.work_lng
        }
        const saved = await updateCommuteSettings(payload)
        this.settingsForm = { ...saved }
        this.settingsMessage = 'Settings saved.'
      } catch (err) {
        console.error(err)
        this.settingsMessage = 'Failed to save settings.'
      } finally {
        this.savingSettings = false
      }
    },
    async removeWalk(id) {
      try {
        await deleteCommuteWalk(id)
        await this.refreshAll()
      } catch (err) {
        console.error(err)
        this.pageError = 'Failed to delete walk.'
      }
    }
  }
}
</script>

<style scoped>
.walk-tracker {
  max-width: 900px;
  margin: 0 auto;
}

.banner-error {
  margin-bottom: 1rem;
}

.error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: 1rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.error button {
  background: var(--primary);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
}

.track-panel {
  background: var(--bg-white);
  border: 1px solid var(--border);
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: var(--shadow-md);
  margin-bottom: 1.5rem;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.track-panel.live {
  border-color: #86efac;
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.12), var(--shadow-md);
}

.track-status {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.85rem;
  border-radius: 999px;
  font-weight: 600;
  font-size: 0.875rem;
  background: var(--bg-cream);
  color: var(--text-gray);
}

.status-pill.live {
  background: #dcfce7;
  color: #166534;
}

.pulse {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
  animation: pulse 1.4s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.4); opacity: 0.55; }
}

.direction-toggle {
  display: flex;
  gap: 0.5rem;
  background: var(--bg-cream);
  padding: 0.25rem;
  border-radius: 0.75rem;
}

.direction-toggle button {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  border: none;
  background: transparent;
  padding: 0.5rem 0.85rem;
  border-radius: 0.55rem;
  cursor: pointer;
  color: var(--text-gray);
  font-weight: 500;
}

.direction-toggle button.active {
  background: var(--bg-white);
  color: var(--primary);
  box-shadow: var(--shadow);
}

.direction-live {
  color: var(--text-gray);
  font-weight: 500;
}

.live-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.metric {
  background: var(--bg-light);
  border-radius: 0.75rem;
  padding: 1rem;
  text-align: center;
}

.metric-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-light);
  margin-bottom: 0.35rem;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-dark);
  font-variant-numeric: tabular-nums;
}

.track-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  border: none;
  border-radius: 0.65rem;
  padding: 0.7rem 1.15rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, transform 0.1s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn.primary {
  background: var(--primary);
  color: white;
}

.btn.primary:hover:not(:disabled) {
  background: var(--primary-dark);
}

.btn.danger {
  background: #dc2626;
  color: white;
}

.btn.secondary {
  background: var(--bg-cream);
  color: var(--text-dark);
}

.btn.ghost {
  background: transparent;
  color: var(--text-gray);
  border: 1px solid var(--border);
}

.btn.icon-btn {
  background: transparent;
  color: var(--text-light);
  padding: 0.5rem;
}

.btn.icon-btn:hover {
  color: #dc2626;
  background: #fef2f2;
}

.geo-message {
  margin-top: 1rem;
  font-size: 0.9rem;
  color: var(--text-gray);
}

.geo-message.warn {
  color: #b45309;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: var(--bg-white);
  border: 1px solid var(--border);
  border-radius: 0.85rem;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  box-shadow: var(--shadow);
}

.stat-icon {
  width: 42px;
  height: 42px;
  border-radius: 0.65rem;
  background: var(--primary-light);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-light);
}

.stat-value {
  font-weight: 700;
  color: var(--text-dark);
  font-variant-numeric: tabular-nums;
}

.settings-panel {
  margin-bottom: 1.5rem;
}

.settings-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: transparent;
  border: none;
  color: var(--primary);
  font-weight: 600;
  cursor: pointer;
  padding: 0.25rem 0;
  margin-bottom: 0.75rem;
}

.settings-form {
  background: var(--bg-white);
  border: 1px solid var(--border);
  border-radius: 0.85rem;
  padding: 1.25rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.85rem;
  margin-bottom: 1rem;
}

.form-grid label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.85rem;
  color: var(--text-gray);
  font-weight: 500;
}

.form-grid input {
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  padding: 0.55rem 0.7rem;
  font-size: 0.95rem;
  color: var(--text-dark);
  background: var(--bg-light);
}

.settings-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.path-panel {
  background: var(--bg-white);
  border: 1px solid var(--border);
  border-radius: 0.85rem;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
}

.path-panel h3 {
  margin-bottom: 0.75rem;
  font-size: 1.05rem;
}

.path-svg {
  width: 100%;
  height: auto;
  border-radius: 0.5rem;
  overflow: hidden;
}

.path-bg {
  fill: var(--bg-cream);
}

.path-line {
  stroke: var(--primary);
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.path-start {
  fill: #16a34a;
}

.path-end {
  fill: #dc2626;
}

.history h3 {
  margin-bottom: 0.85rem;
  font-size: 1.05rem;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 2rem;
  color: var(--text-light);
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty {
  color: var(--text-light);
  padding: 1.5rem;
  background: var(--bg-cream);
  border-radius: 0.75rem;
  text-align: center;
}

.walk-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.walk-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  background: var(--bg-white);
  border: 1px solid var(--border);
  border-radius: 0.75rem;
  padding: 0.9rem 1rem;
}

.walk-item.in_progress {
  border-left: 3px solid #22c55e;
}

.walk-item.cancelled {
  opacity: 0.7;
}

.walk-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.2rem;
}

.walk-dir {
  font-weight: 600;
}

.walk-status-badge {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  background: var(--bg-cream);
  color: var(--text-light);
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
}

.walk-meta {
  font-size: 0.875rem;
  color: var(--text-light);
}

.walk-notes {
  margin-top: 0.35rem;
  font-size: 0.875rem;
  color: var(--text-gray);
}

@media (max-width: 768px) {
  .live-metrics {
    grid-template-columns: 1fr;
  }

  .stats-row {
    grid-template-columns: 1fr 1fr;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .track-status {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
