import sys
sys.path.insert(0, r'D:\MyClaw\ci-scoring\backend')
from app import app
import json

with app.test_client() as client:
    # 1. 测试词牌列表API (正确路径: /api/cipai/list)
    resp = client.get('/api/cipai/list')
    print(f"List API status: {resp.status_code}")
    if resp.status_code == 200:
        data = json.loads(resp.data)
        items = data.get('data', [])
        print(f"词牌列表: {len(items)}个词牌")
        
        # 检查水龙吟和几个词牌的pattern_count
        for name in ['水调歌头', '念奴娇', '水龙吟', '沁园春']:
            item = next((i for i in items if i.get('name') == name), None)
            if item:
                print(f"  {name}: id={item.get('id')}, pattern_count={item.get('pattern_count', 'MISSING')}")
            else:
                print(f"  {name}: 未找到!")
    else:
        print(f"Response: {resp.data.decode('utf-8')[:300]}")
    
    # 2. 测试词牌详情API
    resp = client.get('/api/cipai/74')
    print(f"\nDetail API status: {resp.status_code}")
    if resp.status_code == 200:
        data = json.loads(resp.data)
        d = data.get('data', {})
        patterns = d.get('patterns', [])
        print(f"  水龙吟: {len(patterns)}个格律")
        if patterns:
            for i, p in enumerate(patterns[:3]):
                print(f"    Pattern[{i}]: {p.get('name')} - {p.get('description', 'NO DESC')[:50]}")
    else:
        print(f"Response: {resp.data.decode('utf-8')[:300]}")
    
    # 3. 测试grid API (核心功能)
    print(f"\nGrid API测试:")
    for pid in [1, 2, 74]:
        resp = client.get(f'/api/cipai/{pid}/grid?pattern=0')
        if resp.status_code == 200:
            data = json.loads(resp.data)
            d = data.get('data', {})
            grid = d.get('grid', [])
            name = d.get('cipai_name', '')
            print(f"  cipai_id={pid} ({name}): grid={len(grid)}句 ✅")
        else:
            print(f"  cipai_id={pid}: HTTP {resp.status_code} ❌")
            try:
                print(f"    Error: {resp.data.decode('utf-8')[:200]}")
            except:
                pass
    
    # 4. 测试水龙吟全部25个格律
    print(f"\n水龙吟全部格律Grid测试:")
    errors = []
    for i in range(25):
        resp = client.get(f'/api/cipai/74/grid?pattern={i}')
        if resp.status_code != 200:
            errors.append((i, f"HTTP {resp.status_code}"))
            continue
        data = json.loads(resp.data)
        d = data.get('data', {})
        grid = d.get('grid', [])
        if len(grid) == 0:
            errors.append((i, "空grid"))
    
    if errors:
        print(f"  ❌ 失败: {errors}")
    else:
        print(f"  ✅ 全部25个格律grid正常")
