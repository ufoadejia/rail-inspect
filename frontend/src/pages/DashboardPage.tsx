import { useEffect, useState } from 'react'
import { Card, Row, Col, Spin, Empty, Typography } from 'antd'
import {
  ToolOutlined, ScanOutlined, WarningOutlined, CloseCircleOutlined,
} from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import { getStats } from '../api'

const defectNames: Record<string, string> = {
  nuclear: '核伤', bolt_hole: '螺孔裂纹', longitudinal: '纵向裂纹',
  spalling: '剥离', wear: '磨耗', corrugation: '波磨',
  weld: '焊缝缺陷', surface: '表面擦伤', normal: '正常',
}

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getStats().then(setStats).finally(() => setLoading(false))
  }, [])

  const statCards = [
    { label: '工单总数', value: stats?.total_workorders || 0, icon: <ToolOutlined />,
      color: '#2f6bff', bg: '#e8f0ff' },
    { label: '检测总数', value: stats?.total_detections || 0, icon: <ScanOutlined />,
      color: '#16a34a', bg: '#e8f7ee' },
    { label: '轻伤数量', value: stats?.grade_distribution?.轻伤 || 0, icon: <WarningOutlined />,
      color: '#f59e0b', bg: '#fef4e2' },
    { label: '重伤数量', value: stats?.grade_distribution?.重伤 || 0, icon: <CloseCircleOutlined />,
      color: '#ef4444', bg: '#fdeaea' },
  ]

  const defectPie = stats?.defect_type_distribution && Object.keys(stats.defect_type_distribution).length ? {
    tooltip: { trigger: 'item' },
    legend: { bottom: 0, textStyle: { fontSize: 12 } },
    series: [{
      type: 'pie', radius: ['42%', '68%'], center: ['50%', '45%'],
      itemStyle: { borderColor: '#fff', borderWidth: 2 },
      label: { fontSize: 12 },
      data: Object.entries(stats.defect_type_distribution).map(([k, v]: any) => ({
        name: defectNames[k] || k, value: v,
      })),
    }],
  } : null

  const gradeBar = stats?.grade_distribution && Object.keys(stats.grade_distribution).length ? {
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: Object.keys(stats.grade_distribution),
      axisLine: { lineStyle: { color: '#e4e9f0' } } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#f0f3f7' } } },
    series: [{
      type: 'bar', barWidth: '40%',
      data: Object.values(stats.grade_distribution).map((v: any, i: number) => ({
        value: v, itemStyle: { color: ['#16a34a', '#f59e0b', '#ef4444', '#6b7280'][i % 4], borderRadius: [4, 4, 0, 0] },
      })),
    }],
  } : null

  return (
    <div>
      <div className="page-header">
        <h2>数据看板</h2>
        <div className="sub">探伤作业与缺陷检测的全局统计与分析</div>
      </div>

      <Spin spinning={loading}>
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          {statCards.map((s, i) => (
            <Col span={6} key={i}>
              <div className="stat-card">
                <div className="icon" style={{ background: s.bg, color: s.color }}>{s.icon}</div>
                <div className="meta">
                  <div className="label">{s.label}</div>
                  <div className="value" style={{ color: s.color }}>{s.value}</div>
                </div>
              </div>
            </Col>
          ))}
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Card className="platform-card" title="缺陷类型分布" style={{ height: 380 }}>
              {defectPie
                ? <ReactECharts option={defectPie} style={{ height: 300 }} />
                : <Empty description="暂无数据" style={{ paddingTop: 80 }} />}
            </Card>
          </Col>
          <Col span={12}>
            <Card className="platform-card" title="判级分布" style={{ height: 380 }}>
              {gradeBar
                ? <ReactECharts option={gradeBar} style={{ height: 300 }} />
                : <Empty description="暂无数据" style={{ paddingTop: 80 }} />}
            </Card>
          </Col>
        </Row>
      </Spin>
    </div>
  )
}
