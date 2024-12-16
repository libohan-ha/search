from flask import Flask, render_template, request, jsonify
import requests
import json
import time
from urllib.parse import quote
import random
import google.generativeai as genai
import os

app = Flask(__name__)

# 设置Gemini API密钥
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyA2W6xZHF1xo-PaqkoN7ud_qqRmJJnVoFk')
genai.configure(api_key=GEMINI_API_KEY)

def get_book_recommendations(keyword):
    try:
        # 使用 gemini-pro 模型
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # 构建提示语
        prompt = f"""
        请推荐10本与"{keyword}"相关的书籍。
        对于每本书，请提供以下信息：
        - 书名
        - 作者
        - 出版年份
        - 简短推荐语（50字以内）
        
        请以JSON格式返回，格式如下：
        {{
            "books": [
                {{
                    "title": "书名",
                    "author": "作者",
                    "year": "出版年份",
                    "description": "推荐语"
                }},
                ...
            ]
        }}
        """
        
        response = model.generate_content(prompt)
        
        # 解析JSON响应
        try:
            # 提取JSON字符串
            json_str = response.text
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
                
            data = json.loads(json_str)
            
            # 格式化返回数据
            books = []
            for book in data.get('books', []):
                books.append({
                    'title': book.get('title', '未知'),
                    'author': book.get('author', '未知作者'),
                    'year': book.get('year', '未知'),
                    'description': book.get('description', '暂无推荐语')
                })
                
            return {'success': True, 'books': books}
            
        except json.JSONDecodeError as e:
            return {'error': f'AI返回格式错误: {str(e)}', 'raw_response': response.text}
            
    except Exception as e:
        return {'error': f'获取书籍推荐失败: {str(e)}'}

def get_bilibili_videos(keyword):
    # 对关键词进行URL编码
    encoded_keyword = quote(keyword)
    
    # B站搜索API
    url = f'https://api.bilibili.com/x/web-interface/search/all/v2?keyword={encoded_keyword}&page=1'
    
    # 请求头
    headers = {
        'authority': 'api.bilibili.com',
        'method': 'GET',
        'scheme': 'https',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cache-control': 'max-age=0',
        'cookie': os.environ.get('BILIBILI_COOKIE', 'bili_jct=3f8dbfce81b3e72348b5f5acda3d2cd3; buvid3=4C62AB87-A27F-B888-BC60-BD7FCAF8ED4390625infoc; DedeUserID=672737179; SESSDATA=18a9e739%2C1746672660%2C9eeaa%2Ab2CjDesTbUfD8cl252TC1UTuyeHa_xnpbPz8Q1KdjzhdT9U7lMGDNcoS6rrNBzW-Qh8PASVlF2RE1YNnRtVk1jYklHMFZGQ2RTX2pabVNjUXpiZko4ZFFaU19WdVBlV2ZaM2gzSlB4ZUFIN1VfeEpiMlNBWjZxSE5IQ2tKRGY3d1BYc09UalZmY3FRIIEC; b_nut=1725333890'),
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return {'error': f'请求失败，状态码: {response.status_code}'}
            
        data = response.json()
        
        if 'code' in data and data['code'] != 0:
            return {'error': f'API返回错误，错误码: {data["code"]}, 信息: {data.get("message", "未知错误")}'}
            
        if 'data' not in data or 'result' not in data['data']:
            return {'error': 'API返回数据结构异常'}
            
        videos = data['data']['result']
        
        video_results = None
        for result in videos:
            if result.get('result_type') == 'video':
                video_results = result.get('data', [])
                break
        
        if not video_results:
            return {'error': '未找到视频结果'}
            
        # 获取10条视频数据
        results = []
        for video in video_results[:10]:
            results.append({
                'title': video['title'].strip(),
                'author': video['author'],
                'play_count': video['play'],
                'url': f'https://www.bilibili.com/video/{video["bvid"]}'
            })
            
        return {'success': True, 'videos': results}
            
    except Exception as e:
        return {'error': f'发送错误: {str(e)}'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    keyword = request.args.get('keyword', '')
    search_type = request.args.get('type', 'video')
    is_refresh = request.args.get('refresh', 'false') == 'true'
    
    if not keyword:
        return render_template('index.html', error='请输入搜索关键词')
    
    if search_type == 'video':
        result = get_bilibili_videos(keyword)
        if 'error' in result:
            return jsonify({'error': result['error']}) if is_refresh else render_template('index.html', error=result['error'])
        return jsonify({'success': True, 'results': result['videos']}) if is_refresh else render_template('results.html', keyword=keyword, videos=result['videos'], search_type='video')
    else:
        result = get_book_recommendations(keyword)
        if 'error' in result:
            return jsonify({'error': result['error']}) if is_refresh else render_template('index.html', error=result['error'])
        return jsonify({'success': True, 'results': result['books']}) if is_refresh else render_template('results.html', keyword=keyword, books=result['books'], search_type='book')

# Vercel 需要的 WSGI 应用
app = app 