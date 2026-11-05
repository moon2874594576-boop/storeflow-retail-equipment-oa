import request from '@/utils/request'

export function getEmployeeList(params) {
  return request.get('/employees/', { params })
}

export function getEmployeeDetail(id) {
  return request.get(`/employees/${id}/`)
}

export function createEmployee(data) {
  return request.post('/employees/', data)
}

export function updateEmployee(id, data) {
  return request.put(`/employees/${id}/`, data)
}

export function deleteEmployee(id) {
  return request.delete(`/employees/${id}/`)
}

export function batchDeleteEmployees(ids) {
  return request.post('/employees/batch_delete/', { ids })
}

export function getDepartmentTree() {
  return request.get('/employees/departments/tree/')
}

export function getDepartmentList() {
  return request.get('/employees/departments/all/')
}

export function getDepartmentDetail(id) {
  return request.get(`/employees/departments/${id}/`)
}

export function createDepartment(data) {
  return request.post('/employees/departments/', data)
}

export function updateDepartment(id, data) {
  return request.put(`/employees/departments/${id}/`, data)
}

export function deleteDepartment(id) {
  return request.delete(`/employees/departments/${id}/`)
}

export function getPositionList() {
  return request.get('/employees/positions/all/')
}

export function getPositionDetail(id) {
  return request.get(`/employees/positions/${id}/`)
}

export function createPosition(data) {
  return request.post('/employees/positions/', data)
}

export function updatePosition(id, data) {
  return request.put(`/employees/positions/${id}/`, data)
}

export function deletePosition(id) {
  return request.delete(`/employees/positions/${id}/`)
}
