/**
 * Default places for this install of Walk to Work.
 * Home is prefilled from the owner's address.
 */
export const DEFAULT_HOME = {
  label: '959 Lombard St',
  address: '959 Lombard Street, San Francisco, CA 94133',
  lat: 37.801945,
  lng: -122.418892
}

export const DEFAULT_WORK = {
  label: 'Work',
  address: '',
  lat: null,
  lng: null
}

export function defaultSettings() {
  return {
    home_label: DEFAULT_HOME.label,
    home_address: DEFAULT_HOME.address,
    home_lat: DEFAULT_HOME.lat,
    home_lng: DEFAULT_HOME.lng,
    work_label: DEFAULT_WORK.label,
    work_address: DEFAULT_WORK.address,
    work_lat: DEFAULT_WORK.lat,
    work_lng: DEFAULT_WORK.lng,
    typical_distance_meters: null
  }
}
