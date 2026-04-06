import json

d = json.load(open('d:/MyClaw/ci-scoring/backend/representative_works.json', 'r', encoding='utf-8'))

# 唐多令 ID 72
d['72'] = {
    "main": [
        {
            "title": "芦叶满汀洲",
            "author": "刘过",
            "dynasty": "宋",
            "text": "芦叶满汀洲，寒沙带浅流。二十年重过南楼。柳下系船犹未稳，能几日，又中秋。黄鹤断矶头，故人曾到否？旧江山浑是新愁。欲买桂花同载酒，终不似，少年游。",
            "zi": "改之",
            "hao": "龙洲道人"
        },
        {
            "title": "何处合成愁",
            "author": "吴文英",
            "dynasty": "宋",
            "text": "何处合成愁？离人心上秋。纵芭蕉不雨也飕飕。都道晚凉天气好，有明月、怕登楼。年事梦中休，花空烟水流。燕辞归、客尚淹留。垂柳不萦裙带住，漫长是、系行舟。",
            "zi": "君特",
            "hao": "梦窗"
        },
        {
            "title": "重过何氏",
            "author": "刘辰翁",
            "dynasty": "宋",
            "text": "何氏翠微深，重来路欲迷。惊心时序速，满眼故人稀。古木号寒鸟，空山叫夜狸。老怀悲不尽，归马更迟迟。",
            "zi": "会孟",
            "hao": "须溪"
        }
    ],
    "variants": []
}

json.dump(d, open('d:/MyClaw/ci-scoring/backend/representative_works.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print("唐多令修复完成")

# 验证
v = json.load(open('d:/MyClaw/ci-scoring/backend/representative_works.json','r',encoding='utf-8'))['72']
for w in v['main']:
    print(f"  [{w['author']}] {w['title']}: {w['text'][:30]}...")
