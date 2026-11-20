import axios from 'axios'

export const TOKEN_KEY = 'tf_token'

export const api = axios.create({
  baseURL: '/',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem(TOKEN_KEY)
      window.dispatchEvent(new Event('tf:unauthorized'))
    }
    return Promise.reject(error)
  }
)

export function errorMessage(err, fallback = 'Something went wrong. Please try again.') {
  const detail = err?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0]
    if (first?.msg) return first.msg
  }
  if (err?.message === 'Network Error') {
    return 'Could not reach the server. Check your connection and try again.'
  }
  return fallback
}
