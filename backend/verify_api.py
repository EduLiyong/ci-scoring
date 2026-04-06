#!/usr/bin/env python3
"""
验证夜飞鹊API响应
"""

import requests
import json

def test_yefeique_api():
    # 测试夜飞鹊API
    url = "http://localhost:5000/api/cipai/84/representatives"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            
            if not response_data.get('success'):
                print(f"[ERROR] API返回失败: {response_data.get('message')}")
                return
                
            data = response_data.get('data', {})
            print(f"词牌名称: {data.get('name', '未知')}")
            print(f"夜飞鹊代表作数量: {len(data.get('main', []))}")
            print(f"夜飞鹊变体代表作数量: {len(data.get('variants', []))}")
            
            if data.get('main'):
                print("\n夜飞鹊代表作详情:")
                for i, work in enumerate(data['main'], 1):
                    print(f"\n作品 #{i}:")
                    print(f"  标题: {work.get('title', '无')}")
                    print(f"  作者: {work.get('author', '无')}")
                    print(f"  朝代: {work.get('dynasty', '无')}")
                    print(f"  字号: {work.get('zi', '无')}")
                    print(f"  号: {work.get('hao', '无')}")
                    print(f"  字数: {len(work.get('text', ''))}")
                    
                    # 检查文本格式
                    text = work.get('text', '')
                    if '\n\n' in text:
                        print(f"  格式: 有上下阕分隔符 [√]")
                    else:
                        print(f"  格式: 无上下阕分隔符 [×]")
                    
                    # 显示前100字符
                    preview = text[:100]
                    if len(text) > 100:
                        preview += "..."
                    print(f"  预览: {preview}")
            
            print("\n[OK] API验证通过！")
        else:
            print(f"[ERROR] API错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] API请求失败: {e}")

if __name__ == "__main__":
    test_yefeique_api()