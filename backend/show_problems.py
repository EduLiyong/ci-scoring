# -*- coding: utf-8 -*-
import json
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open('representative_works.json', 'r', encoding='utf-8') as f:
    reps = json.load(f)

# Show problematic entries
problem_ids = [14, 15, 30, 48, 56, 57, 74, 77, 81, 82, 83, 85, 86, 87, 88, 89, 92, 94, 96]

for pid in problem_ids:
    data = reps.get(str(pid), {})
    main = data.get('main', [])
    print(f"\n{'='*60}")
    print(f"ID {pid}: {main[0]['title'] if main else 'N/A'}")
    for i, w in enumerate(main[:2]):
        print(f"  [{i}] {w['title']} - {w['author']} ({w.get('dynasty','')})")
        print(f"      Text: {w['text'][:100]}...")
