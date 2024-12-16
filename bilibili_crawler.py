import requests
import json
import time
from urllib.parse import quote
import random

def get_bilibili_videos(keyword):
    # 对关键词进行URL编码
    encoded_keyword = quote(keyword)
    
    # B站搜索API
    url = f'https://api.bilibili.com/x/web-interface/search/all/v2?keyword={encoded_keyword}&page=1'
    
    # 更完整的请求头
    headers = {
        'authority': 'api.bilibili.com',
        'method': 'GET',
        'scheme': 'https',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cache-control': 'max-age=0',
        'cookie': 'bili_jct=3f8dbfce81b3e72348b5f5acda3d2cd3; buvid3=4C62AB87-A27F-B888-BC60-BD7FCAF8ED4390625infoc; DedeUserID=672737179; SESSDATA=18a9e739%2C1746672660%2C9eeaa%2Ab2CjDesTbUfD8cl252TC1UTuyeHa_xnpbPz8Q1KdjzhdT9U7lMGDNcoS6rrNBzW-Qh8PASVlF2RE1YNnRtVk1jYklHMFZGQ2RTX2pabVNjUXpiZko4ZFFaU19WdVBlV2ZaM2gzSlB4ZUFIN1VfeEpiMlNBWjZxSE5IQ2tKRGY3d1BYc09UalZmY3FRIIEC; b_nut=1725333890',
        'dnt': '1',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    
    try:
        # 添加超时设置
        response = requests.get(url, headers=headers, timeout=10)
        
        # 检查响应状态码
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            print("响应内容:", response.text)
            return
            
        # 解析JSON
        data = response.json()
        
        # 检查返回数据结构
        if 'code' in data and data['code'] != 0:
            print(f"API返回错误，错误码: {data['code']}, 信息: {data.get('message', '未知错误')}")
            return
            
        if 'data' not in data or 'result' not in data['data']:
            print("API返回数据结构异常")
            print("完整返回数据：", data)
            return
            
        # 获取视频列表
        videos = data['data']['result']
        
        # 查找视频结果类型
        video_results = None
        for result in videos:
            if result.get('result_type') == 'video':
                video_results = result.get('data', [])
                break
        
        if not video_results:
            print("未找到视频结果")
            return
            
        # 只取前5条数据
        for i, video in enumerate(video_results[:5], 1):
            print(f"\n视频 {i}:")
            print(f"标题: {video['title'].strip()}")
            print(f"作者: {video['author']}")
            print(f"播放量: {video['play']}")
            print(f"视频链接: https://www.bilibili.com/video/{video['bvid']}")
            print("-" * 50)
            
            # 增加随机延时 1-3 秒
            time.sleep(1 + random.random() * 2)
            
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {str(e)}")
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {str(e)}")
        print("响应内容:", response.text)
    except KeyError as e:
        print(f"数据结构错误: {str(e)}")
        print("数据结构:", data)
    except Exception as e:
        print(f"其他错误: {str(e)}")

if __name__ == "__main__":
    keyword = input("请输入要搜索的关键词: ")
    get_bilibili_videos(keyword) 