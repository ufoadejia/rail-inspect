import React from 'react'
import ReactDOM from 'react-dom/client'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import { HashRouter } from 'react-router-dom'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          colorPrimary: '#2f6bff',
          borderRadius: 6,
          fontSize: 14,
          colorBgLayout: '#f0f3f7',
        },
        components: {
          Card: { headerBg: 'transparent' },
          Table: {
            headerBg: '#f7f9fc',
            headerColor: '#1f2937',
            headerSplitColor: '#e4e9f0',
            rowHoverBg: '#f0f5ff',
          },
          Button: { fontWeight: 500 },
        },
      }}
    >
      <HashRouter>
        <App />
      </HashRouter>
    </ConfigProvider>
  </React.StrictMode>,
)
