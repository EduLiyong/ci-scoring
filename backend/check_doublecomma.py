with open('d:/MyClaw/ci-scoring/backend/cipai_data.py', encoding='utf-8') as f:
    lines = f.readlines()
print('总行数:', len(lines))
for i, l in enumerate(lines):
    stripped = l.rstrip()
    if '},,' in stripped:
        print('行%d: %s' % (i+1, stripped))