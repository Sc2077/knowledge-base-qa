import { useState, useEffect } from 'react'
import { List, Button, Empty, Modal, Input, message } from 'antd'
import { PlusOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { conversationService, Conversation } from '../services/conversation'

const ConversationList = () => {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [newTitle, setNewTitle] = useState('')
  const navigate = useNavigate()

  const loadConversations = async () => {
    setLoading(true)
    try {
      const data = await conversationService.list()
      setConversations(data)
    } catch (error: any) {
      message.error('加载对话列表失败')
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    if (!newTitle.trim()) {
      message.warning('请输入对话标题')
      return
    }
    try {
      const conversation = await conversationService.create({ title: newTitle })
      message.success('创建成功')
      setModalVisible(false)
      setNewTitle('')
      navigate(`/conversations/${conversation.id}`)
    } catch (error: any) {
      message.error('创建失败')
    }
  }

  const handleDelete = async (id: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个对话吗？',
      onOk: async () => {
        try {
          await conversationService.delete(id)
          message.success('删除成功')
          loadConversations()
        } catch (error: any) {
          message.error('删除失败')
        }
      },
    })
  }

  useEffect(() => {
    loadConversations()
  }, [])

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h2>对话列表</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
          新建对话
        </Button>
      </div>

      {conversations.length === 0 ? (
        <Empty description="暂无对话" />
      ) : (
        <List
          loading={loading}
          dataSource={conversations}
          renderItem={(item) => (
            <List.Item
              actions={[
                <Button type="link" onClick={() => handleDelete(item.id)}>删除</Button>,
              ]}
              onClick={() => navigate(`/conversations/${item.id}`)}
              style={{ cursor: 'pointer' }}
            >
              <List.Item.Meta
                title={item.title}
                description={`创建于: ${new Date(item.created_at).toLocaleString()}`}
              />
            </List.Item>
          )}
        />
      )}

      <Modal
        title="新建对话"
        open={modalVisible}
        onOk={handleCreate}
        onCancel={() => setModalVisible(false)}
      >
        <Input
          placeholder="请输入对话标题"
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          onPressEnter={handleCreate}
        />
      </Modal>
    </div>
  )
}

export default ConversationList