import { Routes, Route, Navigate } from 'react-router-dom'
import { ConfigProvider, theme } from 'antd'
import Login from './pages/Login'
import Layout from './components/Layout'
import KnowledgeBaseList from './pages/KnowledgeBaseList'
import KnowledgeBaseDetail from './pages/KnowledgeBaseDetail'
import ConversationList from './pages/ConversationList'
import ConversationDetail from './pages/ConversationDetail'

function App() {
  return (
    <ConfigProvider
      theme={{
        algorithm: theme.defaultAlgorithm,
      }}
    >
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/conversations" replace />} />
          <Route path="knowledge-bases" element={<KnowledgeBaseList />} />
          <Route path="knowledge-bases/:id" element={<KnowledgeBaseDetail />} />
          <Route path="conversations" element={<ConversationList />} />
          <Route path="conversations/:id" element={<ConversationDetail />} />
        </Route>
        <Route path="*" element={<Navigate to="/conversations" replace />} />
      </Routes>
    </ConfigProvider>
  )
}

export default App