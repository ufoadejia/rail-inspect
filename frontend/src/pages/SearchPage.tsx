import { useState } from 'react'
import { Card, Input, Button, Tabs, List, Tag, Typography, message, Spin, Empty, Row, Col } from 'antd'
import { SearchOutlined, SendOutlined, FileSearchOutlined } from '@ant-design/icons'
import { ask, retrieve } from '../api'

const { Text } = Typography

const docTypeMeta: Record<string, { color: string; label: string }> = {
  text: { color: 'blue', label: '规程' },
  image: { color: 'purple', label: '图谱' },
  table: { color: 'cyan', label: '标准' },
  case: { color: 'gold', label: '案例' },
}

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [answer, setAnswer] = useState('')
  const [citations, setCitations] = useState<any[]>([])
  const [retrieved, setRetrieved] = useState<any[]>([])

  const handleAsk = async () => {
    if (!query.trim()) { message.warning('请输入问题'); return }
    setLoading(true)
    try {
      const data = await ask(query)
      setAnswer(data.answer)
      setCitations(data.citations || [])
      setRetrieved(data.retrieved || [])
    } catch (e: any) {
      message.error('检索失败：' + (e.message || '请检查后端'))
    } finally {
      setLoading(false)
    }
  }

  const handleRetrieveOnly = async () => {
    if (!query.trim()) { message.warning('请输入问题'); return }
    setLoading(true)
    try {
      const data = await retrieve(query)
      setRetrieved(data.items || [])
      setAnswer('')
      setCitations([])
    } catch (e: any) {
      message.error('检索失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <h2>跨模态知识检索</h2>
        <div className="sub">输入文字（如「核伤判级标准」）检索探伤规程、缺陷图谱、历史案例，每条建议可溯源到原始资料</div>
      </div>

      <Card className="platform-card" style={{ marginBottom: 16 }}>
        <Input.TextArea
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="例如：发现回波当量 31dB 的核伤，应如何处置？"
          rows={3}
          style={{ marginBottom: 12 }}
        />
        <div className="flex gap-8">
          <Button type="primary" icon={<SendOutlined />} loading={loading} onClick={handleAsk}>
            智能问答
          </Button>
          <Button icon={<FileSearchOutlined />} loading={loading} onClick={handleRetrieveOnly}>
            仅检索
          </Button>
        </div>
      </Card>

      <Spin spinning={loading}>
        <Tabs
          defaultActiveKey="answer"
          items={[
            {
              key: 'answer',
              label: '智能回答',
              children: answer ? (
                <Card className="platform-card">
                  <div style={{ whiteSpace: 'pre-wrap', fontSize: 15, lineHeight: 1.8 }}>{answer}</div>
                  {citations.length > 0 && (
                    <div style={{ marginTop: 16, paddingTop: 12, borderTop: '1px dashed var(--c-border)' }}>
                      <Text strong style={{ fontSize: 13, color: 'var(--c-text-2)' }}>
                        <SearchOutlined style={{ marginRight: 6 }} />引用来源
                      </Text>
                      <List size="small" dataSource={citations}
                        renderItem={(c: any) => (
                          <List.Item style={{ padding: '8px 0' }}>
                            <Tag>[{c.id}]</Tag>
                            <Text type="secondary" style={{ flex: 1 }}>
                              {c.source} · {c.title}
                            </Text>
                            <Tag color="default">相似度 {c.score}</Tag>
                          </List.Item>
                        )} />
                    </div>
                  )}
                </Card>
              ) : <Empty description="点击「智能问答」生成带引用的回答" style={{ padding: 60 }} />,
            },
            {
              key: 'docs',
              label: `检索结果 (${retrieved.length})`,
              children: retrieved.length ? (
                <Row gutter={[16, 16]}>
                  {retrieved.map((item: any, i: number) => {
                    const m = docTypeMeta[item.doc_type] || { color: 'default', label: item.doc_type }
                    return (
                      <Col span={12} key={i}>
                        <Card className="platform-card" size="small"
                          title={<><Tag color={m.color}>{m.label}</Tag><Text>{item.title}</Text></>}>
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            来源：{item.source} · 相似度 {(item.score ?? item.fused_score ?? 0).toFixed(4)}
                          </Text>
                          <div style={{ marginTop: 8, fontSize: 13, lineHeight: 1.7, color: 'var(--c-text)' }}>
                            {(item.content || '').slice(0, 160)}
                            {(item.content || '').length > 160 ? '…' : ''}
                          </div>
                        </Card>
                      </Col>
                    )
                  })}
                </Row>
              ) : <Empty description="暂无检索结果" style={{ padding: 60 }} />,
            },
          ]}
        />
      </Spin>
    </div>
  )
}
