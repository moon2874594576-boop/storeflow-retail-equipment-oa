import request from '@/utils/request'

export function getAnnouncementList(params) {
  return request.get('/announcements/items/', { params })
}

export function getAnnouncementDetail(id) {
  return request.get(`/announcements/items/${id}/`)
}

export function createAnnouncement(data) {
  return request.post('/announcements/items/', data)
}

export function updateAnnouncement(id, data) {
  return request.put(`/announcements/items/${id}/`, data)
}

export function deleteAnnouncement(id) {
  return request.delete(`/announcements/items/${id}/`)
}

export function publishAnnouncement(id) {
  return request.post(`/announcements/items/${id}/publish/`)
}

export function revokeAnnouncement(id) {
  return request.post(`/announcements/items/${id}/revoke/`)
}

export function readAnnouncement(id) {
  return request.post(`/announcements/items/${id}/read/`)
}

export function getUnreadCount() {
  return request.get('/announcements/items/unread_count/')
}

export function getMyPublished(params) {
  return request.get('/announcements/items/my_published/', { params })
}
