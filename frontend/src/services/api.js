import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  }
})

export const fetchCommuteWalks = async (limit = null) => {
  try {
    const params = {}
    if (limit != null) params.limit = limit
    const response = await api.get('/commute/walks', { params })
    return response.data
  } catch (error) {
    console.error('Error fetching commute walks:', error)
    throw error
  }
}

export const fetchCommuteStats = async () => {
  try {
    const response = await api.get('/commute/stats')
    return response.data
  } catch (error) {
    console.error('Error fetching commute stats:', error)
    throw error
  }
}

export const fetchCommuteSettings = async () => {
  try {
    const response = await api.get('/commute/settings')
    return response.data
  } catch (error) {
    console.error('Error fetching commute settings:', error)
    throw error
  }
}

export const updateCommuteSettings = async (settings) => {
  try {
    const response = await api.put('/commute/settings', settings)
    return response.data
  } catch (error) {
    console.error('Error updating commute settings:', error)
    throw error
  }
}

export const createCommuteWalk = async (payload) => {
  try {
    const response = await api.post('/commute/walks', payload)
    return response.data
  } catch (error) {
    console.error('Error creating commute walk:', error)
    throw error
  }
}

export const updateCommuteWalk = async (walkId, payload) => {
  try {
    const response = await api.patch(`/commute/walks/${walkId}`, payload)
    return response.data
  } catch (error) {
    console.error('Error updating commute walk:', error)
    throw error
  }
}

export const appendCommutePoints = async (walkId, points) => {
  try {
    const response = await api.post(`/commute/walks/${walkId}/points`, { points })
    return response.data
  } catch (error) {
    console.error('Error appending commute points:', error)
    throw error
  }
}

export const deleteCommuteWalk = async (walkId) => {
  try {
    const response = await api.delete(`/commute/walks/${walkId}`)
    return response.data
  } catch (error) {
    console.error('Error deleting commute walk:', error)
    throw error
  }
}

