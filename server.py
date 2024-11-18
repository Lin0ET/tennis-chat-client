from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import requests
import json

app = Flask(__name__)
CORS(app)  # 允許跨域訪問

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

# 使用 Llama 3.1 生成回答（流式回應支持）
def generate_answer_with_llama(user_question):
    llama_url = "http://140.115.126.192:11434/api/generate"  # 正確的 Llama 3.1 API 路徑
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "llama3.1",       # 指定模型名稱
        "prompt": user_question,   # 用戶問題
        "max_tokens": 100          # 可以根據需求調整回答的長度
    }
    
    try:
        response = requests.post(llama_url, headers=headers, json=payload, stream=True)
        response.raise_for_status()  # 確認 HTTP 請求成功

        # 累積生成的回應文字
        final_text = ""
        
        # 逐行讀取流式回應
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode('utf-8'))
                
                # 累加生成的回應片段
                final_text += data.get("response", "")
                
                # 檢查是否已完成回應
                if data.get("done"):
                    break

        return final_text if final_text else "抱歉，未能獲得回應。"

    except requests.exceptions.RequestException as e:
        print(f"Llama 3.1 API 請求錯誤: {e}")
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
