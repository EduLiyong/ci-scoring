import sys
sys.path.insert(0, 'd:/MyClaw/ci-scoring/backend')
import cipai_data as cp

for i, c in enumerate(cp.CIPAI_DATABASE):
    if c.get('id') in [36, 50]:
        print('index=%d, id=%s, name=%s' % (i, c.get('id'), c.get('name')))