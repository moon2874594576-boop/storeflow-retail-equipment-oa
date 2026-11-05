import request from '@/utils/request'

export function getApprovalTypeList() {
  return request.get('/approvals/types/all/')
}

export function getApprovalTypeDetail(id) {
  return request.get(`/approvals/types/${id}/`)
}

export function createApprovalType(data) {
  return request.post('/approvals/types/', data)
}

export function updateApprovalType(id, data) {
  return request.put(`/approvals/types/${id}/`, data)
}

export function deleteApprovalType(id) {
  return request.delete(`/approvals/types/${id}/`)
}

export function getMyApprovals(params) {
  return request.get('/approvals/mine/', { params })
}

export function getPendingApprovals(params) {
  return request.get('/approvals/pending/', { params })
}

export function getApprovalList(params) {
  return request.get('/approvals/', { params })
}

export function getApprovalDetail(id) {
  return request.get(`/approvals/${id}/`)
}

export function createApproval(data) {
  return request.post('/approvals/', data)
}

export function approveApproval(id, data) {
  return request.post(`/approvals/${id}/approve/`, data)
}

export function rejectApproval(id, data) {
  return request.post(`/approvals/${id}/reject/`, data)
}

export function revokeApproval(id) {
  return request.post(`/approvals/${id}/revoke/`)
}

export function getApprovalRecords(id) {
  return request.get(`/approvals/${id}/records/`)
}
