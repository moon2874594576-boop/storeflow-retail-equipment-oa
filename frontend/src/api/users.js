import request from '@/utils/request'

export function getUserList(params) {
  return request.get('/users/', { params })
}

export function getUserDetail(id) {
  return request.get(`/users/${id}/`)
}

export function createUser(data) {
  return request.post('/users/', data)
}

export function updateUser(id, data) {
  return request.put(`/users/${id}/`, data)
}

export function deleteUser(id) {
  return request.delete(`/users/${id}/`)
}

export function batchDeleteUsers(ids) {
  return request.post('/users/batch_delete/', { ids })
}

export function getRoleList() {
  return request.get('/users/roles/all/')
}

export function getRoleDetail(id) {
  return request.get(`/users/roles/${id}/`)
}

export function createRole(data) {
  return request.post('/users/roles/', data)
}

export function updateRole(id, data) {
  return request.put(`/users/roles/${id}/`, data)
}

export function deleteRole(id) {
  return request.delete(`/users/roles/${id}/`)
}

export function getPermissionList() {
  return request.get('/users/permissions/all/')
}
