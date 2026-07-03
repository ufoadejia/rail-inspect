import axios from 'axios'

const api = axios.create({ baseURL: '/' })

// ===== 缺陷识别 =====
export const detectDefect = (file: File, imageType = 'surface') => {
  const form = new FormData()
  form.append('file', file)
  form.append('image_type', imageType)
  return api.post('/detect', form).then(r => r.data)
}

// ===== 知识检索 =====
export const retrieve = (query: string, imageUrl?: string) =>
  api.post('/rag/retrieve', { query, image_url: imageUrl }).then(r => r.data)

export const ask = (query: string, imageUrl?: string) =>
  api.post('/rag/ask', { query, image_url: imageUrl }).then(r => r.data)

// ===== 工单 =====
export const listWorkorders = (status?: string) =>
  api.get('/workorders', { params: { status } }).then(r => r.data)
export const createWorkorder = (data: any) =>
  api.post('/workorders', data).then(r => r.data)
export const getWorkorder = (id: number) =>
  api.get(`/workorders/${id}`).then(r => r.data)
export const transitionWorkorder = (id: number, toStatus: string, assignee?: string) =>
  api.post(`/workorders/${id}/transition`, { to_status: toStatus, assignee }).then(r => r.data)

// ===== 报告 =====
export const reportUrl = (id: number) => `/reports/${id}/docx`

// ===== 看板 =====
export const getStats = () => api.get('/dashboard/stats').then(r => r.data)
