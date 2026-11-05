export const roleNames = { employee: '门店员工', manager: '门店店长', custodian: '设备管理员', admin: '系统管理员' }
export const requestStates = { draft: '草稿', pending: '待店长审批', approved: '待发放', handover: '待签收', borrowed: '借用中', return_pending: '待归还验收', returned: '已归还', rejected: '已驳回', withdrawn: '已撤回' }
export const assetStates = { available: '空闲可用', handover: '交接中', in_use: '借用中', inspection: '待验收', maintenance: '待维修' }
export const actions = { submit: '提交申请', approve: '同意申请', reject: '驳回申请', withdraw: '撤回申请', issue: '发放设备', undo_issue: '撤销发放', receive: '确认签收', return: '申请归还', inspect: '归还验收' }
export function dateTime(value) { return value ? new Date(value).toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai', hour12: false, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }) : '—' }
export function day(value) { return value ? String(value).slice(0, 10) : '—' }
export function nextWeek() { const date = new Date(); date.setDate(date.getDate() + 7); return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}` }
