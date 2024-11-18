from flask import Flask, request, jsonify
from flask_cors import CORS  # 新增 CORS 導入
import sqlite3
import requests


app = Flask(__name__)
CORS(app)  # 啟用 CORS，允許所有來源訪問
# 若只想允許特定的來源，例如 React 頁面所在的 localhost:3000，可以這樣設置：
# CORS(app, origins=["http://localhost:3000"])

# 連接 SQLite 資料庫
def get_db_connection():
    conn = sqlite3.connect('knowledge_base.db')
    conn.row_factory = sqlite3.Row
    return conn

# 查詢知識庫
def retrieve_answer_from_db(user_question):
    conn = get_db_connection()
    cursor = conn.execute(
        'SELECT answer, image_url FROM faq WHERE question LIKE ?', 
        ('%' + user_question + '%',)
    )
    result = cursor.fetchone()
    conn.close()
    if result:
        return result['answer'], result['image_url']
    return None, None

# 使用 Llama 3.1 生成回答
def generate_answer_with_llama(user_question):
    # 生成的 API 請求 URL
    llama_url = "http://140.115.126.192:11434/generate"  # 替換為提供的 Llama 3.1 API URL
    headers = {"Content-Type": "application/json"}
    payload = {
        "prompt": user_question,
        "max_tokens": 100  # 可以根據需求調整回答的長度
    }
    
    response = requests.post(llama_url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json().get("generated_text", "")
    else:
        return "抱歉，無法生成回應，請稍後再試。"

# 回答用戶問題
@app.route('/api/chat', methods=['POST'])
def chat():
    user_question = request.json['message']
    
    # 檢索知識庫
    retrieved_answer, image_url = retrieve_answer_from_db(user_question)

    # 若知識庫有結果，直接返回檢索的答案
    if retrieved_answer:
        return jsonify({'message': retrieved_answer, 'image_url': image_url})
    
    # 若知識庫無結果，使用 Llama 3.1 生成回覆
    else:
        bot_response = generate_answer_with_llama(user_question)
        return jsonify({'message': bot_response, 'image_url': None})

if __name__ == '__main__':
    app.run(port=5000)
