import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Upload, List, Button, Empty, message, Tag, Modal, Input } from 'antd'
import { InboxOutlined, ArrowLeftOutlined } from '@ant-design/icons'
import type { UploadProps } from 'antd'
import { knowledgeBaseService, KnowledgeBase } from '../services/knowledgeBase'
import { documentService, Document } from '../services/document'

const { Dragger } = Upload

const KnowledgeBaseDetail = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [knowledgeBase, setKnowledgeBase] = useState<KnowledgeBase | null>(null)
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)

  const loadKnowledgeBase = async () => {
    try {
      const data = await knowledgeBaseService.get(id!)
      setKnowledgeBase(data)
    } catch (error: any) {
      message.error('加载知识库失败')
    }
  }

  const loadDocuments = async () => {
    setLoading(true)
    try {
      const data = await documentService.list(id!)
      setDocuments(data)
    } catch (error: any) {
      message.error('加载文档列表失败')
    } finally {
      setLoading(false)
    }
  }

  const handleUpload: UploadProps['customRequest'] = async (options) => {
    const { file } = options
    setUploading(true)
    try {
      await documentService.upload(id!, file as File)
      message.success('上传成功')
      loadDocuments()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '上传失败')
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (docId: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个文档吗？',
      onOk: async () => {
        try {
          await documentService.delete(docId)
          message.success('删除成功')
          loadDocuments()
        } catch (error: any) {
          message.error('删除失败')
        }
      },
    })
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success'
      case 'processing':
        return 'processing'
      case 'failed':
        return 'error'
      default:
        return 'default'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return '已完成'
      case 'processing':
        return '处理中'
      case 'failed':
        return '失败'
      default:
        return status
    }
  }

  useEffect(() => {
    loadKnowledgeBase()
    loadDocuments()
  }, [id])

  return (
    <div>
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/knowledge-bases')} style={{ marginBottom: 16 }}>
        返回
      </Button>

      <div style={{ marginBottom: 24 }}>
        <h2>{knowledgeBase?.name}</h2>
        <p style={{ color: '#666' }}>{knowledgeBase?.description || '暂无描述'}</p>
      </div>

      <div style={{ marginBottom: 24 }}>
        <h3>上传文档</h3>
        <Dragger
          name="file"
          multiple={false}
          customRequest={handleUpload}
          showUploadList={false}
          disabled={uploading}
        >
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">支持 PDF、Word、Markdown、TXT 格式</p>
        </Dragger>
      </div>

      <div>
        <h3>文档列表 ({documents.length})</h3>
        {documents.length === 0 ? (
          <Empty description="暂无文档" />
        ) : (
          <List
            loading={loading}
            dataSource={documents}
            renderItem={(doc) => (
              <List.Item
                actions={[
                  <Button type="link" danger onClick={() => handleDelete(doc.id)}>删除</Button>,
                ]}
              >
                <List.Item.Meta
                  title={
                    <Space>
                      {doc.filename}
                      <Tag color={getStatusColor(doc.status)}>{getStatusText(doc.status)}</Tag>
                    </Space>
                  }
                  description={
                    <div>
                      <div>类型: {doc.file_type} | 大小: {(doc.file_size / 1024).toFixed(2)} KB</div>
                      {doc.chunk_count > 0 && <div>分段数: {doc.chunk_count}</div>}
                      {doc.error_message && <div style={{ color: '#ff4d4f' }}>错误: {doc.error_message}</div>}
                      <div style={{ fontSize: 12, color: '#999' }}>
                        上传于: {new Date(doc.created_at).toLocaleString()}
                      </div>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </div>
    </div>
  )
}

export default KnowledgeBaseDetail