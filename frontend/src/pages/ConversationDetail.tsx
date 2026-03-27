import { useState, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import { Input, Button, List, Empty, Select, Space, Spin } from 'antd'
import { SendOutlined } from '@ant-design/icons'
import { conversationService, Conversation, Message } from '../services/conversation'
import { knowledgeBaseService, KnowledgeBase } from '../services/knowledgeBase'

const ConversationDetail = () => {
  const { id } = useParams<{ id: string }>()
  const [conversation, setConversation] = useState<Conversation | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [streaming, setStreaming] = useState(false)
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([])
  const [selectedKB, setSelectedKB] = useState<string | undefined>()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const loadConversation = async () => {
    try {
      const data = await conversationService.get(id!)
      setConversation(data)
    } catch (error: any) {
      console.error('Failed to load conversation:', error)
    }
  }

  const loadMessages = async () => {
    try {
      const data = await conversationService.getMessages(id!)
      setMessages(data)
    } catch (error: any) {
      console.error('Failed to load messages:', error)
    }
  }

  const loadKnowledgeBases = async () => {
    try {
      const data = await knowledgeBaseService.list()
      setKnowledgeBases(data)
    } catch (error: any) {
      console.error('Failed to load knowledge bases:', error)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSend = async () => {
    if (!input.trim()) return

    const question = input
    setInput('')
    setStreaming(true)

    try {
      const stream = await conversationService.chat(id!, question, selectedKB)
      const reader = stream.getReader()
      const decoder = new TextDecoder()
      let fullAnswer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.chunk) {
                fullAnswer += data.chunk
                setMessages(prev => {
                  const newMessages = [...prev]
                  const lastMessage = newMessages[newMessages.length - 1]
                  if (lastMessage && lastMessage.role === 'assistant' && streaming) {
                    lastMessage.content = fullAnswer
                  } else {
                    newMessages.push({
                      id: Date.now().toString(),
                      conversation_id: id!,
                      role: 'assistant',
                      content: fullAnswer,
                      created_at: new Date().toISOString(),
                    })
                  }
                  return newMessages
                })
                scrollToBottom()
              } else if (data.done) {
                setStreaming(false)
                loadMessages()
              } else if (data.error) {
                console.error('Stream error:', data.error)
                setStreaming(false)
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e)
            }
          }
        }
      }
    } catch (error: any) {
      console.error('Failed to send message:', error)
      setStreaming(false)
    }
  }

  useEffect(() => {
    loadConversation()
    loadMessages()
    loadKnowledgeBases()
  }, [id])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <h2>{conversation?.title}</h2>
        <Select
          placeholder="选择知识库（可选）"
          style={{ width: 300 }}
          value={selectedKB}
          onChange={setSelectedKB}
          allowClear
        >
          {knowledgeBases.map(kb => (
            <Select.Option key={kb.id} value={kb.id}>{kb.name}</Select.Option>
          ))}
        </Select>
      </div>

      <div style={{ height: 'calc(100vh - 300px)', overflowY: 'auto', marginBottom: 16 }}>
        {messages.length === 0 ? (
          <Empty description="暂无消息" />
        ) : (
          <List
            dataSource={messages}
            renderItem={(msg) => (
              <List.Item style={{ display: 'block', border: 'none' }}>
                <div style={{
                  display: 'flex',
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  marginBottom: 16,
                }}>
                  <div style={{
                    maxWidth: '70%',
                    padding: 12,
                    borderRadius: 8,
                    background: msg.role === 'user' ? '#1890ff' : '#f0f0f0',
                    color: msg.role === 'user' ? '#fff' : '#000',
                  }}>
                    <pre style={{ whiteSpace: 'pre-wrap', margin: 0, fontFamily: 'inherit' }}>
                      {msg.content}
                    </pre>
                  </div>
                </div>
              </List.Item>
            )}
          />
        )}
        {streaming && (
          <div style={{ textAlign: 'center', padding: 16 }}>
            <Spin />
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div style={{ display: 'flex', gap: 8 }}>
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onPressEnter={handleSend}
          placeholder="输入您的问题..."
          disabled={streaming}
          size="large"
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSend}
          loading={streaming}
          size="large"
        >
          发送
        </Button>
      </div>
    </div>
  )
}

export default ConversationDetail