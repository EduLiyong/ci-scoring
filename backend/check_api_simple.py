import urllib.request, json

try:
    req = urllib.request.urlopen('http://localhost:5000/api/cipai/list', timeout=5)
    raw = req.read().decode('utf-8')
    data = json.loads(raw)
    print("API词牌数量:", data.get('total', 0))
    names = [c['name'] for c in data.get('data', [])[:5]]
    print("前5个:", names)
except Exception as e:
    print("ERROR:", e)
