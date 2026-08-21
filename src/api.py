import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from src.agent import PCAgent
import logging
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

agent = PCAgent(use_voice=False)

# HTML-шаблон для веб-интерфейса
WEB_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fuck_By_Daylight_AI – Web</title>
    <style>
        body { background: #0a0a1a; color: #e0e0e0; font-family: Arial, sans-serif; }
        .container { max-width: 600px; margin: 20px auto; padding: 20px; }
        .chat { height: 400px; overflow-y: auto; border: 1px solid #ff6b81; padding: 10px; border-radius: 10px; }
        .msg { margin: 5px 0; padding: 8px 12px; border-radius: 16px; }
        .user { background: #ff6b81; color: #000; align-self: flex-end; text-align: right; }
        .bot { background: #1a1a2e; color: #ff6b81; }
        .input-area { display: flex; margin-top: 10px; }
        .input-area input { flex: 1; padding: 8px; border-radius: 20px; border: 1px solid #ff6b81; background: #1a1a2e; color: #fff; }
        .input-area button { padding: 8px 20px; border-radius: 20px; border: none; background: #ff6b81; color: #000; margin-left: 10px; }
        .actions { display: flex; flex-wrap: wrap; gap: 6px; margin: 10px 0; }
        .actions button { background: rgba(255,107,129,0.2); border: 1px solid #ff6b81; color: #ff6b81; border-radius: 12px; padding: 4px 10px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🤖 Вадим (Web)</h2>
        <div class="chat" id="chat"></div>
        <div class="input-area">
            <input id="msg" placeholder="Напишите команду..." />
            <button onclick="send()">🚀</button>
        </div>
        <div class="actions">
            <button onclick="sendCmd('статистика системы')">📊 Статистика</button>
            <button onclick="sendCmd('погода Москва')">🌤️ Погода</button>
            <button onclick="sendCmd('открой стим')">🎮 Steam</button>
            <button onclick="sendCmd('температура')">🌡️ Температура</button>
            <button onclick="sendCmd('список торрентов')">🧲 Торренты</button>
        </div>
    </div>
    <script>
        function addMsg(sender, text) {
            const div = document.createElement('div');
            div.className = 'msg ' + sender;
            div.textContent = text;
            document.getElementById('chat').appendChild(div);
            const chat = document.getElementById('chat');
            chat.scrollTop = chat.scrollHeight;
        }
        async function send() {
            const input = document.getElementById('msg');
            const msg = input.value;
            if (!msg) return;
            input.value = '';
            addMsg('user', msg);
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: msg})
            });
            const data = await response.json();
            addMsg('bot', data.response || 'Ошибка');
        }
        function sendCmd(cmd) {
            document.getElementById('msg').value = cmd;
            send();
        }
        document.getElementById('msg').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') send();
        });
        addMsg('bot', 'Привет! Я Вадим. Чем могу помочь?');
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(WEB_HTML)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        if not message:
            return jsonify({'error': 'Пустое сообщение'}), 400
        logger.info(f"📩 Запрос: {message[:50]}...")
        response = agent.think_and_act(message)
        logger.info(f"📤 Ответ: {response[:50]}...")
        return jsonify({'response': response})
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/speak', methods=['POST'])
def speak():
    try:
        data = request.json
        text = data.get('text', '')
        if text:
            agent.speak(text)
            return jsonify({'status': 'ok'})
        return jsonify({'error': 'Нет текста'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def stats():
    try:
        return jsonify(agent.get_stats())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    return jsonify({'status': 'online', 'name': 'Вадим'})

@app.route('/mode', methods=['POST'])
def set_mode():
    try:
        data = request.json
        mode = data.get('mode', '')
        modes = {
            'record': agent.imitation.start_recording,
            'self_play': agent.imitation.start_self_learning,
            'clone': agent.imitation.start_cloning,
            'free': agent.imitation.start_free_mode,
            'stop': agent.imitation.stop_all
        }
        if mode in modes:
            result = modes[mode]()
            return jsonify({'response': result})
        return jsonify({'error': f'Неизвестный режим: {mode}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_api():
    logger.info("🚀 Запуск API сервера на http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)

if __name__ == '__main__':
    run_api()