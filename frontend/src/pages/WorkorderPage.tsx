import { useState, useEffect } from 'react'
import {
  Card, Table, Button, Modal, Form, Input, Select, Tag, Space,
  message, Steps, Typography,
} from 'antd'
import { PlusOutlined, FileWordOutlined } from '@ant-design/icons'
import { listWorkorders, createWorkorder, transitionWorkorder, reportUrl } from '../api'

const statusMeta: Record<string, { label: string; color: string; step: number }> = {
  created: { label: '待派发', color: 'default', step: 0 },
  assigned: { label: '已派发', color: 'blue', step: 1 },
  in_progress: { label: '作业中', color: 'processing', step: 2 },
  reviewing: { label: '待验收', color: 'warning', step: 3 },
  rejected: { label: '已驳回', color: 'error', step: 2 },
  archived: { label: '已归档', color: 'success', step: 4 },
}

const stepItems = [
  { title: '创建' }, { title: '派发' }, { title: '作业' },
  { title: '验收' }, { title: '归档' },
]

export default function WorkorderPage() {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [form] = Form.useForm()

  const load = async () => {
    setLoading(true)
    try {
      const res = await listWorkorders()
      setData(res.items || [])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleCreate = async () => {
    const values = await form.validateFields()
    await createWorkorder(values)
    message.success('工单已创建')
    setModalOpen(false)
    form.resetFields()
    load()
  }

  const handleTransition = async (id: number, to: string) => {
    await transitionWorkorder(id, to)
    message.success('状态已更新')
    load()
  }

  const columns = [
    { title: '工单号', dataIndex: 'id', width: 110,
      render: (id: number) => <span style={{ fontFamily: 'monospace' }}>WO-{String(id).padStart(6, '0')}</span> },
    { title: '标题', dataIndex: 'title', ellipsis: true },
    { title: '线路', dataIndex: 'line_name', width: 110 },
    { title: '千米标', dataIndex: 'kilometer', width: 110 },
    { title: '股别', dataIndex: 'rail_side', width: 70 },
    {
      title: '状态', dataIndex: 'status', width: 100,
      render: (s: string) => <Tag color={statusMeta[s]?.color}>{statusMeta[s]?.label || s}</Tag>,
    },
    { title: '作业人', dataIndex: 'assignee', width: 90, render: (v: string) => v || '—' },
    {
      title: '创建时间', dataIndex: 'created_at', width: 160,
      render: (t: string) => t ? new Date(t).toLocaleString('zh-CN') : '—',
    },
    {
      title: '操作', width: 200, fixed: 'right' as const,
      render: (_: any, row: any) => (
        <Space size={0}>
          {row.status === 'created' &&
            <Button size="small" type="link" onClick={() => handleTransition(row.id, 'assigned')}>派发</Button>}
          {row.status === 'assigned' &&
            <Button size="small" type="link" onClick={() => handleTransition(row.id, 'in_progress')}>开始作业</Button>}
          {row.status === 'in_progress' &&
            <Button size="small" type="link" onClick={() => handleTransition(row.id, 'reviewing')}>提交验收</Button>}
          {row.status === 'reviewing' && <>
            <Button size="small" type="link" onClick={() => handleTransition(row.id, 'archived')}>验收通过</Button>
            <Button size="small" type="link" danger onClick={() => handleTransition(row.id, 'rejected')}>驳回</Button>
          </>}
          {row.status === 'archived' &&
            <Button size="small" type="link" icon={<FileWordOutlined />} href={reportUrl(row.id)}>报告</Button>}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div className="page-header">
        <h2>作业工单</h2>
        <div className="sub">探伤作业工单全流程管理：创建 → 派发 → 作业 → 验收 → 归档，归档后可一键导出探伤报告</div>
      </div>

      <Card className="platform-card">
        <div className="flex-between" style={{ marginBottom: 16 }}>
          <span style={{ color: 'var(--c-text-2)' }}>共 {data.length} 条工单</span>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>新建工单</Button>
        </div>
        <Table
          rowKey="id"
          loading={loading}
          dataSource={data}
          columns={columns}
          scroll={{ x: 1100 }}
          pagination={{ pageSize: 10, showSizeChanger: true, showTotal: (t) => `共 ${t} 条` }}
          expandable={{
            expandedRowRender: (row: any) => (
              <Steps size="small" current={statusMeta[row.status]?.step} items={stepItems} style={{ maxWidth: 800 }} />
            ),
            rowExpandable: () => true,
          }}
        />
      </Card>

      <Modal title="新建探伤工单" open={modalOpen} onOk={handleCreate}
        onCancel={() => setModalOpen(false)} okText="创建" cancelText="取消" width={520}>
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="title" label="工单标题" rules={[{ required: true, message: '请输入标题' }]}>
            <Input placeholder="如：K125+300 核伤复核" />
          </Form.Item>
          <Form.Item name="line_name" label="线路名称" rules={[{ required: true, message: '请输入线路' }]}>
            <Input placeholder="如：京沪下行" />
          </Form.Item>
          <Form.Item name="kilometer" label="千米标">
            <Input placeholder="如：K125+300" />
          </Form.Item>
          <Form.Item name="rail_side" label="股别">
            <Select options={[
              { value: '左股', label: '左股' },
              { value: '右股', label: '右股' },
              { value: '双股', label: '双股' },
            ]} />
          </Form.Item>
          <Form.Item name="description" label="作业说明">
            <Input.TextArea rows={3} placeholder="作业内容、注意事项等" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
