import { useState, useEffect, useRef } from 'react'
import './App.css'
import io from 'socket.io-client'

function App() {
  const [messages, setMessages] = useState([])
  const [notifications, setNotifications] = useState([])
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [theme, setTheme] = useState('light')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }

  useEffect(() => {
    if (messages.length > 0) {
      scrollToBottom()
    }
  }, [messages])

  useEffect(() => {
    const socket = io('http://localhost:5000')
    socket.on('notification', (notification) => {
      setNotifications(prev => [...prev, notification])
    })
    socket.on('typing', () => {
      setIsTyping(true)
      setTimeout(() => setIsTyping(false), 3000)
    })
    return () => socket.disconnect()
  }, [])

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
    document.documentElement.setAttribute('data-theme', newTheme)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!question.trim() || loading) return

    setLoading(true)
    try {
      const response = await fetch('http://localhost:5000/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      })
      const data = await response.json()
      
      if (response.ok) {
        setMessages(prev => [...prev, { type: 'question', content: question }, { type: 'answer', content: data.response }])
      } else {
        throw new Error(data.error || 'Failed to get response')
      }
    } catch (error) {
      setMessages(prev => [...prev, { type: 'question', content: question }, { type: 'error', content: error.message }])
    } finally {
      setQuestion('')
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <button className="theme-toggle" onClick={toggleTheme}>
        {theme === 'light' ? '🌙' : '☀️'}
      </button>
      <div className="chat-container">
        <div className="messages-area">
          {messages && messages.length > 0 ? (
            messages.map((message, index) => (
              <div key={index} className={`message ${message.type}`}>
                {message.type === 'question' && <div className="avatar user">👤</div>}
                {message.type === 'answer' && <div className="avatar agent">🤖</div>}
                <div className="content">{message.content}</div>
              </div>
            ))
          ) : (
            <div className="empty-chat">
              <p>No messages yet. Start a conversation!</p>
            </div>
          )}
          {isTyping && (
            <div className="typing-indicator">
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <form onSubmit={handleSubmit} className="input-area">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question..."
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Thinking...' : 'Send'}
          </button>
        </form>
      </div>
      <div className="notifications-panel">
        <h3>Agent Activity</h3>
        <div className="notifications-list">
          {notifications.map((notification, index) => (
            <div key={index} className={`notification ${notification.type}`}>
              <span className="timestamp">{notification.timestamp}</span>
              <span className="description">{notification.description}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default App
