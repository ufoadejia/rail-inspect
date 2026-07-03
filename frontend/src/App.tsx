import { useState } from 'react'
import { Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { Layout, Menu, Drawer, Button } from 'antd'
import {
  ScanOutlined, SearchOutlined, FileTextOutlined,
  BarChartOutlined, ToolOutlined, AuditOutlined, MenuOutlined,
} from '@ant-design/icons'
import DetectPage from './pages/DetectPage'
import SearchPage from './pages/SearchPage'
import WorkorderPage from './pages/WorkorderPage'
import DashboardPage from './pages/DashboardPage'

const { Header, Content } = Layout

const menuItems = [
  { key: '/detect', icon: <ScanOutlined />, label: '缺陷识别' },
  { key: '/search', icon: <SearchOutlined />, label: '知识检索' },
  { key: '/workorder', icon: <ToolOutlined />, label: '作业工单' },
  { key: '/dashboard', icon: <BarChartOutlined />, label: '数据看板' },
]

export default function App() {
  const location = useLocation()
  const navigate = useNavigate()
  const selected = menuItems.find(m => location.pathname.startsWith(m.key))?.key || '/detect'
  const [drawerOpen, setDrawerOpen] = useState(false)

  const onMenuClick = ({ key }: { key: string }) => {
    navigate(key)
    setDrawerOpen(false)
  }

  return (
    <Layout className="platform-layout" style={{ minHeight: '100vh' }}>
      <Header className="platform-header">
        <div className="brand" style={{ flex: 1 }}>
          <Button type="text" icon={<MenuOutlined />} onClick={() => setDrawerOpen(true)}
            style={{ color: '#fff', marginRight: 12, display: 'none' }}
            className="mobile-menu-btn" />
          <span className="logo"><AuditOutlined /></span>
          <span>铁轨探伤智能检修平台</span>
        </div>
      </Header>
      <Layout>
        <Drawer
          placement="left"
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          styles={{ body: { padding: 0, background: 'var(--c-sider)' } }}
          width={220}
        >
          <Menu
            mode="inline"
            theme="dark"
            selectedKeys={[selected]}
            items={menuItems}
            onClick={onMenuClick}
            style={{ background: 'transparent' }}
          />
        </Drawer>
        <Content className="platform-content">
          <Routes>
            <Route path="/detect" element={<DetectPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/workorder" element={<WorkorderPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="*" element={<Navigate to="/detect" replace />} />
          </Routes>
        </Content>
      </Layout>
      <style>{`
        @media (max-width: 768px) {
          .platform-header .brand { font-size: 15px; }
          .platform-header .logo { width: 24px; height: 24px; font-size: 14px; }
          .platform-header .env-tag { display: none; }
          .mobile-menu-btn { display: inline-flex !important; }
          .platform-content { padding: 12px 14px !important; }
          .page-header h2 { font-size: 17px; }
          .page-header .sub { font-size: 12px; }
        }
      `}</style>
    </Layout>
  )
}