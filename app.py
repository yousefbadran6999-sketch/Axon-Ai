from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# المفتاح بيجيلك من Environment Variables (مش موجود في الكود)
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        image = data.get('image')
        model = data.get('model', 'pro')
        
        # بناء الرسالة
        if image:
            messages = [{
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': message or 'حلل هذه الصورة بالتفصيل'},
                    {'type': 'image_url', 'image_url': {'url': image}}
                ]
            }]
            model_name = 'llama-3.2-11b-vision-preview'
        else:
            messages = [{'role': 'user', 'content': message}]
            if model == 'flash':
                model_name = 'llama-3.1-8b-instant'
            elif model == 'vision':
                model_name = 'llama-3.2-11b-vision-preview'
            else:
                model_name = 'llama-3.3-70b-versatile'
        
        # الاتصال بـ Groq
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {GROQ_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': model_name,
                'messages': messages,
                'temperature': 0.7,
                'max_tokens': 2000
            },
            timeout=60
        )
        
        if response.status_code != 200:
            return jsonify({'success': False, 'error': 'فشل الاتصال بـ Groq'}), 500
        
        result = response.json()
        return jsonify({
            'success': True,
            'content': result['choices'][0]['message']['content']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
