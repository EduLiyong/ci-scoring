import json

d = json.load(open('d:/MyClaw/ci-scoring/backend/representative_works.json', 'r', encoding='utf-8'))

d['76'] = {
    "main": [
        {
            "title": "旧时月色",
            "author": "姜夔",
            "dynasty": "宋",
            "text": "旧时月色，算几番照我、梅边吹笛？唤起玉人，不管清寒与攀摘。何逊而今渐老，都忘却、春风词笔。但怪得、竹外疏花，香冷入瑶席。\n江国，正寂寂。叹寄与路遥，夜雪初积。翠尊易泣，红萼无言耿相忆。长记曾携手处，千树压、西湖寒碧。又片片、吹尽也，几时见得？"
        },
        {
            "title": "送魏句滨宰吴县解组分韵得阖字",
            "author": "吴文英",
            "dynasty": "宋",
            "text": "县花谁葺。记满庭燕麦，朱扉斜阖。妙手作新，公馆青红晓云湿。天际疏星趁马，帘昼隙、冰弦三叠。尽换却、吴水吴烟，桃李靓春靥。\n风急。送帆叶。正雁水夜清，卧虹平帖。软红路接。涂粉闱深早催入。怀暖天香宴果，花队簇、轻轩银蜡。更问讯、湖上柳，两堤翠匝。"
        },
        {
            "title": "为毅斋知院赋",
            "author": "赵以夫",
            "dynasty": "宋",
            "text": "冰花炯炯。记那回占断，春风鳌顶。独抱寒香，得意西湖酒初醒。为问玉堂富贵，争得似、山中深靓。向岁晚，竹翠松苍，闲伴一枝冷。\n南浦，水万顷。想月湿断矶，云弄疏影。粉英落尽。孤鹤长鸣夜方永。将见青青似豆，又迤逦、传黄风景。听报道、催去也，再调玉鼎。"
        },
        {
            "title": "晓霜一色",
            "author": "吴潜",
            "dynasty": "宋",
            "text": "晓霜一色。正恁时陇上，征人横笛。驿使不来，借问孤芳为谁折。休说和羹未晚，都付与、逋仙吟笔。算只是，野店疏篱，樵子共争席。\n寒圃，众籁寂。想暗里度香，万斛堆积。恼他鼻观，巡檐还无最堪忆。萼绿堂前一笑，封老干、苔青莓碧。春漏也，应念我、要归未得。"
        },
        {
            "title": "占春压一",
            "author": "吴文英",
            "dynasty": "宋",
            "text": "占春压一。卷峭寒万里，平沙飞雪。数点酥钿，凌晓东风吹裂。独曳横梢瘦影，入广平、裁冰词笔。记五湖、清夜推篷，临水一痕月。\n何逊扬州旧事，五更梦半醒，胡调吹彻。若把南枝，图入凌烟，香满玉楼琼阙。相将初试红盐味，到烟雨、青黄时节。想雁空、北落冬深，澹墨晚天云阔。"
        }
    ],
    "variants": []
}

json.dump(d, open('d:/MyClaw/ci-scoring/backend/representative_works.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print("暗香修复完成")

# 验证
v = json.load(open('d:/MyClaw/ci-scoring/backend/representative_works.json','r',encoding='utf-8'))['76']
for w in v['main']:
    print(f"  [{w['author']}] {w['title']}: {w['text'][:40]}...")
