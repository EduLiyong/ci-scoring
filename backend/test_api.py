import sys, time
sys.path.insert(0, 'd:/MyClaw/ci-scoring/backend')

# 等待 Flask 启动
import urllib.request
for i in range(10):
    try:
        r = urllib.request.urlopen('http://localhost:5000/api/cipai/36', timeout=2)
        data = r.read().decode('utf-8')
        import json
        c = json.loads(data)
        print('API OK: ID 36 = %s' % c.get('name'))
        break
    except Exception as e:
        print('等待 Flask 启动... (%d)' % (i+1))
        time.sleep(1)
else:
    print('Flask 未响应')

# 测试代表作 API
try:
    r2 = urllib.request.urlopen('http://localhost:5000/api/cipai/36/representatives', timeout=2)
    rep = json.loads(r2.read().decode('utf-8'))
    print('代表作 API OK: %s, main=%d, variant=%d' % (
        rep.get('name'), len(rep.get('main',[])), len(rep.get('variant',[]))))
    for w in rep.get('main', []):
        print('  - [%s] %s: %s' % (w.get('dynasty'), w.get('author'), w.get('title')))
except Exception as e:
    print('代表作 API 错误:', e)