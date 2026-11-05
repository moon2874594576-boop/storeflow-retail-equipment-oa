import request from '@/utils/request'

export function login(data) {
  return request.post('/auth/login/', data)
}

export function logout() {
  return request.post('/auth/logout/')
}

export function getProfile() {
  return request.get('/auth/profile/')
}

export function updateProfile(data) {
  return request.put('/auth/profile/', data)
}

export function changePassword(data) {
  return request.post('/auth/change_password/', data)
}

export function refreshToken() {
  const refreshToken = localStorage.getItem('refresh_token')
  return request.post('/token/refresh/', {
    refresh: refreshToken
  })
}