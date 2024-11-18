import React, { useState } from 'react';
import axios from 'axios';

function ChatRoom() {
  const [message, setMessage] = useState('');
  const [chatResponse, setChatResponse] = useState('');
  const [imageUrl, setImageUrl] = useState('');

  const handleSendMessage = async () => {
    try {
      const response = await axios.post('http://localhost:5000/api/chat', { message });
      setChatResponse(response.data.message);
      setImageUrl(response.data.image_url || '');  // 如果有圖片 URL，則顯示
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  return (
    <div className="ChatRoom">
      <h1>網球學習聊天室</h1>
      <div>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="輸入你的問題"
        />
        <button onClick={handleSendMessage}>送出</button>
      </div>
      <p>回應: {chatResponse}</p>
      {imageUrl && <img src={imageUrl} alt="相關圖片" style={{ maxWidth: '100%', height: 'auto' }} />}
    </div>
  );
}

export default ChatRoom;
