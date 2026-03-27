import { Layout as AntLayout, Menu, Button } from 'antd'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { KnowledgeBaseOutlined, MessageOutlined, LogoutOutlined } from '@ant-design/icons'
import { authService } from '../services/auth'

const { Header, Content, Sider } = AntLayout

const Layout = () => {
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    authService.logout()
    navigate('/login')
  }

  const menuItems = [
    {
      key: '/conversations',
      icon: <MessageOutlined />,
      label: '对话',
      onClick: () => navigate('/conversations'),
    },
    {
      key: '/knowledge-bases',
      icon: <KnowledgeBaseOutlined />,
      label: '知识库',
      onClick: () => navigate('/knowledge-bases'),
    },
  ]

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider theme="light">
        <div style={{ height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center', borderBottom: '1px solid #f0f0f0' }}>
          <span style={{ fontSize: '18px', fontWeight: 'bold' }}>知识库问答</span>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          style={{ height: 'calc(100vh - 64px)' }}
        />
      </Sider>
      <AntLayout>
        <Header style={{ background: '#fff', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #f0f0f0' }}>
          <div></div>
          <Button icon={<LogoutOutlined />} onClick={handleLogout}>
            退出登录
          </Button>
        </Header>
        <Content style={{ margin: '24px', overflow: 'auto' }}>
          <div style={{ padding: 24, background: '#fff', borderRadius: 8 }}>
            <Outlet />
          </div>
        </Content>
      </AntLayout>
    </AntLayout>
  )
}

export default Layout