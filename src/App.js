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
    <div className="flex justify-center items-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md bg-white p-6 rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-center text-gray-800 mb-6">網球學習聊天室</h1>

        {/* 輸入區域 */}
        <div className="flex space-x-2 mb-4">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="輸入你的問題"
            className="flex-1 p-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={handleSendMessage}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition"
          >
            送出
          </button>
        </div>

        {/* 回應區域 */}
        <div className="bg-gray-50 p-4 rounded-md">
          <p className="text-gray-700 mb-2">回應: {chatResponse}</p>
          {imageUrl && <img src={imageUrl} alt="相關圖片" className="w-full rounded-md mt-3" />}
        </div>
      </div>
    </div>
  );
}

export default ChatRoom;
