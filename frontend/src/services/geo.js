/**
 * Geolocation helper — uses Capacitor on native, browser API on web/PWA.
 */

async function getCapacitorGeolocation() {
  try {
    if (!window.Capacitor?.isNativePlatform?.()) return null
    const mod = await import('@capacitor/geolocation')
    return mod.Geolocation
  } catch {
    return null
  }
}

function toBrowserLikePosition(position) {
  return {
    coords: {
      latitude: position.coords.latitude,
      longitude: position.coords.longitude,
      accuracy: position.coords.accuracy,
      altitude: position.coords.altitude ?? null,
      altitudeAccuracy: position.coords.altitudeAccuracy ?? null,
      heading: position.coords.heading ?? null,
      speed: position.coords.speed ?? null
    },
    timestamp: position.timestamp || Date.now()
  }
}

export async function getCurrentPosition(options = {}) {
  const Geo = await getCapacitorGeolocation()
  if (Geo) {
    const pos = await Geo.getCurrentPosition({
      enableHighAccuracy: options.enableHighAccuracy ?? true,
      timeout: options.timeout ?? 10000,
      maximumAge: options.maximumAge ?? 60000
    })
    return toBrowserLikePosition(pos)
  }

  if (!navigator.geolocation) {
    throw Object.assign(new Error('Geolocation unavailable'), { code: 2 })
  }

  return new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(resolve, reject, {
      enableHighAccuracy: options.enableHighAccuracy ?? true,
      timeout: options.timeout ?? 10000,
      maximumAge: options.maximumAge ?? 60000
    })
  })
}

export async function watchPosition(onSuccess, onError, options = {}) {
  const Geo = await getCapacitorGeolocation()
  if (Geo) {
    const id = await Geo.watchPosition(
      {
        enableHighAccuracy: options.enableHighAccuracy ?? true,
        timeout: options.timeout ?? 15000,
        maximumAge: options.maximumAge ?? 2000
      },
      (pos, err) => {
        if (err) onError?.(err)
        else if (pos) onSuccess(toBrowserLikePosition(pos))
      }
    )
    return { type: 'capacitor', id }
  }

  if (!navigator.geolocation) {
    onError?.(Object.assign(new Error('Geolocation unavailable'), { code: 2 }))
    return { type: 'none', id: null }
  }

  const id = navigator.geolocation.watchPosition(onSuccess, onError, {
    enableHighAccuracy: options.enableHighAccuracy ?? true,
    timeout: options.timeout ?? 15000,
    maximumAge: options.maximumAge ?? 2000
  })
  return { type: 'browser', id }
}

export async function clearWatch(handle) {
  if (!handle || handle.id == null) return
  if (handle.type === 'capacitor') {
    const Geo = await getCapacitorGeolocation()
    if (Geo) await Geo.clearWatch({ id: handle.id })
    return
  }
  if (handle.type === 'browser' && navigator.geolocation) {
    navigator.geolocation.clearWatch(handle.id)
  }
}

export function isGeolocationAvailable() {
  return !!(window.Capacitor?.isNativePlatform?.() || navigator.geolocation)
}
