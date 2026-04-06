# -*- coding: utf-8 -*-
"""
大模型意境评分模块
接入 OpenAI 兼容接口 / 腾讯混元 进行词作意境评估
"""
import os
import json
import requests


# ======= 配置区 =======
# 可配置为 OpenAI / 百度千帆 / 腾讯混元 / 其他兼容接口
# 当前默认: 百度千帆 ERNIE-4.0-Turbo
LLM_API_URL = os.environ.get("LLM_API_URL", "https://qianfan.baidubce.com/v2/chat/completions")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "ernie-4.0-turbo-8k")
LLM_TIMEOUT = 30  # 秒


YIJING_PROMPT_TEMPLATE = """你是一位精通中国古典诗词的文学评论家和教授，擅长鉴赏词的意境之美。

请对下面这首【{cipai_name}】进行意境评分，满分100分。

词作内容：
{poem_text}

评分维度（总共100分）：
1. 意象运用（25分）：意象是否新颖、准确、富有表现力
2. 情感表达（25分）：情感是否真挚、深刻、动人
3. 意境营造（30分）：意境是否优美、深远、富有画面感
4. 语言美感（20分）：语言是否凝练、优美、有文学性

请严格按照以下JSON格式返回评分结果（只返回JSON，不要其他内容）：
{{
  "total_score": <总分，整数，0-100>,
  "dimensions": {{
    "imagery": {{"score": <分数>, "comment": "<简短评语>"}},
    "emotion": {{"score": <分数>, "comment": "<简短评语>"}},
    "artistic_conception": {{"score": <分数>, "comment": "<简短评语>"}},
    "language": {{"score": <分数>, "comment": "<简短评语>"}}
  }},
  "overall_comment": "<总体评语，100-200字>",
  "highlights": ["<亮点1>", "<亮点2>"],
  "suggestions": ["<改进建议1>", "<改进建议2>"]
}}"""


def score_yijing_with_llm(poem_text: str, cipai_name: str) -> dict:
    """
    调用大模型评估词作意境
    返回评分数据
    """
    if not LLM_API_KEY:
        # 没有配置API Key时，使用模拟评分
        return _mock_yijing_score(poem_text, cipai_name)
    
    prompt = YIJING_PROMPT_TEMPLATE.format(
        cipai_name=cipai_name,
        poem_text=poem_text
    )
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLM_API_KEY}"
    }
    
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1000
    }
    
    try:
        resp = requests.post(LLM_API_URL, headers=headers, json=payload, timeout=LLM_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        
        content = data["choices"][0]["message"]["content"].strip()
        
        # 尝试提取JSON
        # 有时模型会输出多余内容
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            content = json_match.group(0)
        
        result = json.loads(content)
        result['source'] = 'llm'
        return result
        
    except requests.exceptions.Timeout:
        return _error_response("请求大模型超时，请稍后再试")
    except requests.exceptions.RequestException as e:
        return _error_response(f"网络请求失败：{str(e)}")
    except json.JSONDecodeError:
        return _error_response("大模型返回格式异常，无法解析")
    except Exception as e:
        return _error_response(f"评分失败：{str(e)}")


def _mock_yijing_score(poem_text: str, cipai_name: str) -> dict:
    """
    模拟意境评分（未配置API Key时使用）
    基于简单规则给出参考分数
    """
    import hashlib
    # 根据文本内容生成一个伪随机但稳定的分数
    text_hash = int(hashlib.md5(poem_text.encode('utf-8')).hexdigest(), 16)
    
    # 基础分 65-85 之间
    base = 65 + (text_hash % 20)
    
    imagery = min(25, 15 + (text_hash % 10))
    emotion = min(25, 14 + ((text_hash >> 4) % 11))
    conception = min(30, 18 + ((text_hash >> 8) % 12))
    language = min(20, 12 + ((text_hash >> 12) % 8))
    total = imagery + emotion + conception + language
    
    return {
        "total_score": total,
        "dimensions": {
            "imagery": {"score": imagery, "comment": "意象选取较为恰当，有一定画面感"},
            "emotion": {"score": emotion, "comment": "情感表达较为真挚，有所触动"},
            "artistic_conception": {"score": conception, "comment": "意境营造尚可，有待进一步深化"},
            "language": {"score": language, "comment": "语言较为流畅，词句有一定美感"}
        },
        "overall_comment": f"这首{cipai_name}整体构思较为完整，意象运用得当，情感脉络清晰。词中有若干佳句，展现了作者一定的文学功底。建议在意境的深度和语言的凝练上进一步打磨，使作品更臻完善。",
        "highlights": ["意象较为新颖", "情感表达较为真实"],
        "suggestions": ["可加强意境的深度营造", "部分词句可更加凝练"],
        "source": "mock",
        "notice": "当前为演示评分模式，配置大模型API Key后可获得真实AI评分"
    }


def _error_response(msg: str) -> dict:
    return {
        "total_score": 60,
        "dimensions": {
            "imagery": {"score": 15, "comment": "评分服务暂时不可用"},
            "emotion": {"score": 15, "comment": "评分服务暂时不可用"},
            "artistic_conception": {"score": 18, "comment": "评分服务暂时不可用"},
            "language": {"score": 12, "comment": "评分服务暂时不可用"}
        },
        "overall_comment": f"意境评分暂时不可用：{msg}",
        "highlights": [],
        "suggestions": [],
        "source": "error",
        "error": msg
    }


import re
