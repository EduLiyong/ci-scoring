import json

d = json.load(open('d:/MyClaw/ci-scoring/backend/representative_works.json', 'r', encoding='utf-8'))

d['79'] = {
    "main": [
        {
            "title": "簟枕邀凉",
            "author": "姜夔",
            "dynasty": "宋",
            "text": "吴兴号水晶宫，荷花盛丽。陈简斋云：'今年何以报君恩，一路荷花相送到青墩。'亦可见矣。丁未之夏，予游千岩，数往来红香中，自度此曲，以无射宫歌之。\n\n簟枕邀凉，琴书换日，睡余无力。细洒冰泉，并刀破甘碧。墙头唤酒，谁问讯、城南诗客。岑寂，高柳晚蝉，说西风消息。\n\n虹梁水陌，鱼浪吹香，红衣半狼藉。维舟试望，故国渺天北。可惜渚边沙外，不共美人游历。问甚时同赋，三十六陂秋色？"
        },
        {
            "title": "余从姜石帚游苕霅间三十五年矣，重来伤今感昔，聊以咏怀",
            "author": "吴文英",
            "dynasty": "宋",
            "text": "鹭老秋丝，苹愁暮雪，鬓那不白。倒柳移栽，如今暗溪碧。乌衣细语，伤绊惹、茸红曾约。南陌。前度刘郎，寻流花踪迹。\n\n朱楼水侧。雪面波光，汀莲沁颜色。当时醉近绣箔，夜吟寂。三十六矶重到，清梦冷云南北。买钓舟溪上，庆有烟蓑相识。"
        },
        {
            "title": "赠伎双波",
            "author": "张炎",
            "dynasty": "宋",
            "text": "两剪秋痕，平分水影，炯然冰洁。未识新愁，眉心倩人贴。无端醉里，通一笑、柔花盈睫。痴绝。不解送情，倚银屏斜瞥。\n\n长歌短舞，换羽移宫，飘飘步回雪。扶娇倚扇，欲把艳怀说。杜郎重到，只虑空江桃叶。但数峰犹在，如傍那家风月。"
        },
        {
            "title": "寄弁阳翁",
            "author": "李莱老",
            "dynasty": "宋",
            "text": "笛送西泠，帆过杜曲。昼阴芳绿。门巷清风，还寻故人屋。苍华发冷，笑瘦影、相看如竹。幽谷。烟树晚莺，诉经年愁独。\n\n残阳古木。书画归船，匆匆又南北。苹洲鸥鹭素熟。旧盟续。甚日浩歌招隐，听雨弁阳同宿。料重来时候，香荡几湾红玉。"
        }
    ],
    "variants": []
}

json.dump(d, open('d:/MyClaw/ci-scoring/backend/representative_works.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print("惜红衣修复完成，共4首宋代代表作")

# 验证
v = json.load(open('d:/MyClaw/ci-scoring/backend/representative_works.json','r',encoding='utf-8'))['79']
for w in v['main']:
    print(f"  [{w['dynasty']} {w['author']}] {w['title']}: {w['text'][:40]}...")
