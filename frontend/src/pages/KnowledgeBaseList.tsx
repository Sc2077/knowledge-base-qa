import { useState, useEffect } from 'react'
import { List, Button, Empty, Modal, Input, message } from 'antd'
import { PlusOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { knowledgeBaseService, KnowledgeBase, CreateKnowledgeBaseData } from '../services/knowledgeBase'

const KnowledgeBaseList = () => {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [formData, setFormData] = useState<CreateKnowledgeBaseData>({ name: '', description: '' })
  const navigate = useNavigate()

  const loadKnowledgeBases = async () => {
    setLoading(true)
    try {
      const data = await knowledgeBaseService.list()
      setKnowledgeBases(data)
    } catch (error: any) {
      message.error('加载知识库列表失败')
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    if (!formData.name.trim()) {
      message.warning('请输入知识库名称')
      return
    }
    try {
      await knowledgeBaseService.create(formData)
      message.success('创建成功')
      setModalVisible(false)
      setFormData({ name: '', description: '' })
      loadKnowledgeBases()
    } catch (error: any) {
      message.error('创建失败')
    }
  }

  const handleDelete = async (id: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个知识库吗？这将同时删除所有相关文档。',
      onOk: async () => {
        try {
          await knowledgeBaseService.delete(id)
          message.success('删除成功')
          loadKnowledgeBases()
        } catch (error: any) {
          message.error('删除失败')
        }
      },
    })
  }

  useEffect(() => {
    loadKnowledgeBases()
  }, [])

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h2>知识库列表</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
          新建知识库
        </Button>
      </div>

      {knowledgeBases.length === 0 ? (
        <Empty description="暂无知识库" />
      ) : (
        <List
          loading={loading}
          dataSource={knowledgeBases}
          renderItem={(item) => (
            <List.Item
              actions={[
                <Button type="link" onClick={() => navigate(`/knowledge-bases/${item.id}`)}>详情</Button>,
                <Button type="link" danger onClick={() => handleDelete(item.id)}>删除</Button>,
              ]}
              onClick={() => navigate(`/knowledge-bases/${item.id}`)}
              style={{ cursor: 'pointer' }}
            >
              <List.Item.Meta
                title={item.name}
                description={
                  <div>
                    <div>{item.description || '暂无描述'}</div>
                    <div style={{ fontSize: 12, color: '#999' }}>
                      创建于: {new Date(item.created_at).toLocaleString()}
                    </div>
                  </div>
                }
              />
            </List.Item>
          )}
        />
      )}

      <Modal
        title="新建知识库"
        open={modalVisible}
        onOk={handleCreate}
        onCancel={() => setModalVisible(false)}
      >
        <Input
          placeholder="请输入知识库名称"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          style={{ marginBottom: 16 }}
        />
        <Input.TextArea
          placeholder="请输入知识库描述（可选）"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          rows={4}
        />
      </Modal>
    </div>
  )
}

export default KnowledgeBaseList