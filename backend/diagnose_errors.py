import json, re
import cipai_data

with open('representative_works.json', 'r', encoding='utf-8') as f:
    reps = json.load(f)

def count_cjk(text):
    return len(re.sub(r'[^\u4e00-\u9fff]', '', text))

error_ids = [7,10,12,13,14,15,18,19,20,21,22,26,30,31,33,34,37,39,40,41,42,43,44,45,46,56,60,64,65,68,69,70,73,75,76,77,78,79,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,97,98,99]
for cid in error_ids:
    entry = next((e for e in cipai_data.CIPAI_DATABASE if isinstance(e, dict) and e.get('id') == cid), None)
    if entry and str(cid) in reps:
        # Get total_chars from first pattern
        patterns = entry.get('patterns', [])
        total = patterns[0].get('total_chars', 'N/A') if patterns else 'N/A'
        works = reps[str(cid)]['main']
        for w in works:
            actual = count_cjk(w['text'])
            diff = actual - total if isinstance(total, int) else 0
            if isinstance(total, int) and abs(diff) > 0:
                print(f'ID {cid:3d} {entry["name"]:8s} 声称{total}字 | {w["author"]}《{w["title"]}》实际{actual}字 (差{diff:+d})')
    elif not entry:
        print(f'ID {cid} not found in cipai_data!')
