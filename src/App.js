import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function ChatRoom() {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const chatBoxRef = useRef(null);

  // 初始化對話框的開場白和建議問題
  useEffect(() => {
    const initialMessage = {
      role: 'bot',
      content: "你好！我是你的網球教練林小葶。隨時歡迎向我詢問任何網球相關的問題！<br /><br />" +
               "你可以試試問我以下問題：<br />" +
               "1. 林羿萱是誰？<br />" +
               "2. 最帥的網球選手？<br />" +
               "3. 如何正確握拍？"
    };
    setChatHistory([initialMessage]);
  }, []);

  const handleSendMessage = async () => {
    if (!message.trim()) return;

    const updatedHistory = [...chatHistory, { role: 'user', content: message }];
    setChatHistory(updatedHistory);
    setMessage('');

    try {
      const response = await axios.post('http://localhost:5000/api/chat', { chatHistory: updatedHistory });
      const botMessage = { role: 'bot', content: response.data.message };

      if (response.data.image_url) {
        botMessage.imageUrl = response.data.image_url;
      }

      setChatHistory((prevHistory) => [...prevHistory, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [chatHistory]);

  return (
    <div className="chat-background">
      <div className="chat-container">
        <h1 className="title">網球學習聊天室</h1>

        <div className="chat-box" ref={chatBoxRef}>
          {chatHistory.map((msg, index) => (
            <div
              key={index}
              className={`message ${msg.role === 'user' ? 'user-message' : 'bot-message'}`}
            >
              {msg.role === 'bot' ? (
                <p dangerouslySetInnerHTML={{ __html: msg.content }}></p>
              ) : (
                <p>{msg.content}</p>
              )}
              {msg.imageUrl && <img src={msg.imageUrl} alt="相關圖片" className="response-image" />}
            </div>
          ))}
        </div>

        <div className="input-section">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="輸入你的問題"
            className="message-input"
          />
          <button onClick={handleSendMessage} className="send-button">送出</button>
        </div>
      </div>
    </div>
  );
}

export default ChatRoom;
