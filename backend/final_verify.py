import sys
sys.path.insert(0, r'D:\MyClaw\ci-scoring\backend')
from app import app
import json

with app.test_client() as client:
    # ===== 1. 验证词牌列表API中水龙吟的pattern_count =====
    resp = client.get('/api/cipai?keyword=水龙吟')
    data = json.loads(resp.data)
    items = data.get('data', [])
    sls_item = next((i for i in items if i.get('name') == '水龙吟'), None)
    if sls_item:
        print(f"词牌列表: 水龙吟 pattern_count = {sls_item.get('pattern_count', 'N/A')}")
    else:
        print("词牌列表: 水龙吟未找到")

    # ===== 2. 验证25个格律grid全部正常 =====
    print(f"\n===== Grid构建测试 =====")
    all_ok = True
    for i in range(25):
        resp = client.get(f'/api/cipai/74/grid?pattern={i}')
        if resp.status_code != 200:
            print(f"  Pattern {i}: HTTP {resp.status_code} ❌")
            all_ok = False
            continue
        data = json.loads(resp.data)
        d = data.get('data', {})
        grid = d.get('grid', [])
        sp = d.get('stanza_split', 0)
        tc = d.get('total_chars', 0)
        lg_count = len(d.get('line_groups', []))
        tp = d.get('total_patterns', 0)
        if len(grid) == 0:
            print(f"  Pattern {i}: 空grid ❌")
            all_ok = False
        else:
            # Verify chars total
            total_chars_in_grid = sum(g.get('char_count', 0) for g in grid)
            if total_chars_in_grid != tc:
                print(f"  Pattern {i}: {len(grid)}句, {total_chars_in_grid}字(expected {tc}) ⚠️")
            else:
                pass  # OK, don't clutter output
    
    if all_ok:
        print("  全部25个格律grid构建成功 ✅")
    
    # ===== 3. 验证代表作API =====
    print(f"\n===== 代表作API测试 =====")
    resp = client.get('/api/cipai/74/representatives')
    data = json.loads(resp.data)
    d = data.get('data', {})
    main = d.get('main', [])
    variants = d.get('variants', [])
    print(f"  正体代表作: {len(main)}首")
    for w in main:
        print(f"    {w.get('title','')} - {w.get('author','')}")
    
    # Count non-empty variants
    non_empty = 0
    for i, v in enumerate(variants):
        if isinstance(v, dict):
            vw = v.get('works', [])
            if vw:
                non_empty += 1
                for w in vw:
                    print(f"    变体{i+1}: {w.get('title','')} - {w.get('author','')}")
    print(f"  有代表作的变体: {non_empty}个 (共{len(variants)}个)")
    
    # ===== 4. 验证正体grid与代表作的一致性 =====
    print(f"\n===== 正体Grid与代表作一致性 =====")
    resp = client.get('/api/cipai/74/grid?pattern=0')
    data = json.loads(resp.data)
    d = data.get('data', {})
    grid = d.get('grid', [])
    lg = d.get('line_groups', [])
    sp = d.get('stanza_split', 0)
    
    # Count upper/lower lines
    upper_lines = 0
    lower_lines = 0
    for group in lg:
        has_upper = any(s_idx < sp for s_idx in group)
        has_lower = any(s_idx >= sp for s_idx in group)
        if has_upper:
            upper_lines += 1
        if has_lower:
            lower_lines += 1
    
    print(f"  上阕: {upper_lines}行{sp}句")
    print(f"  下阕: {lower_lines}行{len(grid)-sp}句")
    print(f"  上下阕分界: 第{sp}句 ✅" if sp == 12 else f"  上下阕分界: 第{sp}句 ⚠️")
    
    # Check rhyme positions
    rhyme_count_upper = sum(1 for g in grid[:sp] if g.get('is_rhyme'))
    rhyme_count_lower = sum(1 for g in grid[sp:] if g.get('is_rhyme'))
    print(f"  上阕韵脚: {rhyme_count_upper}个")
    print(f"  下阕韵脚: {rhyme_count_lower}个")
    
    # Expected: 双调102字，前段12句4仄韵，后段12句5仄韵
    if rhyme_count_upper == 4 and rhyme_count_lower == 5:
        print(f"  韵脚数匹配 ✅")
    else:
        print(f"  韵脚数不匹配! 预期前4后5 ⚠️")
