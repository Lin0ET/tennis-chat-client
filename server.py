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

# 查詢知識庫中是否有相關回答
def retrieve_answer_from_db(user_question):
    conn = get_db_connection()
    cursor = conn.execute(
        'SELECT answer, image_url FROM faq WHERE question = ?',  # 使用精確匹配
        (user_question,)
    )
    result = cursor.fetchone()
    conn.close()
    if result:
        return result['answer'], result['image_url']  # 返回資料庫中存儲的回答和圖片 URL
    return None, None

# 使用 Llama 3.1 生成回答（支持上下文對話）
def generate_answer_with_llama(chat_history):
    llama_url = "http://140.115.126.192:11434/api/generate"
    headers = {"Content-Type": "application/json"}

    # 構建完整的對話歷史作為 prompt，但避免重新生成開場白
    prompt = (
        "你是經驗豐富的網球教練林小葶，專門指導網球技術和技巧。"
        "請用簡短，大約50字內的繁體中文回答，保持親切、專業且清晰的語氣，並避免過於複雜的術語。"
        "如果適合，可以提供步驟或關鍵提示來幫助學員理解。以下是使用者和你之間的對話：\n\n"
    )

    for msg in chat_history:
        if msg["role"] == "user":
            prompt += f"使用者: {msg['content']}\n"
        elif msg["role"] == "bot":
            prompt += f"林教練: {msg['content']}\n"

    prompt += "林教練: "  # 準備生成新的回答

    payload = {
        "model": "llama3.1",
        "prompt": prompt,
        "max_tokens": 150
    }

    try:
        response = requests.post(llama_url, headers=headers, json=payload, stream=True)
        response.raise_for_status()

        final_text = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode('utf-8'))
                final_text += data.get("response", "")
                if data.get("done"):
                    break

        return final_text if final_text else "抱歉，未能獲得回應。"

    except requests.exceptions.RequestException as e:
        print(f"Llama 3.1 API 請求錯誤: {e}")
        return "抱歉，無法生成回應，請稍後再試。"

# 回答用戶問題
@app.route('/api/chat', methods=['POST'])
def chat():
    chat_history = request.json['chatHistory']  # 獲取完整的對話歷史
    user_question = chat_history[-1]["content"]  # 獲取最新一條用戶問題

    # 如果是第一次打開聊天頁面，返回開場白
    if len(chat_history) == 1 and chat_history[0]["role"] == "user":
        opening_message = (
            "你好！我是你的網球教練林小葶。隨時歡迎向我詢問任何網球相關的問題！\n\n"
            "你可以試試問我以下問題：\n"
            "1. 林羿萱是誰？\n"
            "2. 最帥的網球選手？\n"
            "3. 如何正確握拍？"
        )
        return jsonify({'message': opening_message, 'image_url': None})

    # 1. 先查詢資料庫
    db_answer, image_url = retrieve_answer_from_db(user_question)
    if db_answer:
        # 如果在資料庫中找到答案，直接使用資料庫回答
        return jsonify({'message': db_answer, 'image_url': image_url or None})

    # 2. 如果資料庫無結果，使用 Llama 3.1 生成回應
    bot_response = generate_answer_with_llama(chat_history)
    return jsonify({'message': bot_response, 'image_url': None})

if __name__ == '__main__':
    app.run(port=5000)
