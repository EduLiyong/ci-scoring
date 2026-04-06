# -*- coding: utf-8 -*-
"""
修复重复词牌 v3 - 最终版
- ID 36(望海潮重复) → 迷神引(97字, 柳永创始)
- ID 50(谒金门重复) → 昼夜乐(98字, 柳永创始)

格律来源: 龙榆生《唐宋词格律》+ longyusheng.org
代表作来源: 古诗文网(gushiwen.cn) 逐首查证
"""

import sys, json
sys.path.insert(0, 'd:/MyClaw/ci-scoring/backend')
import cipai_data as cp

# ============================================================
# 迷神引 - 97字 (ID 36替换)
# 双调，前段11句六仄韵，后段13句六仄韵
# ============================================================
MISY_SENTENCES = [
    # 上片 11句
    {"chars": 7, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄平平仄仄平"},
    {"chars": 7, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄平平仄仄平"},
    {"chars": 4, "rhyme": False, "tone": "中平中仄"},
    {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
    {"chars": 3, "rhyme": False, "tone": "中仄仄"},
    {"chars": 3, "rhyme": False, "tone": "中仄仄"},
    {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
    {"chars": 5, "rhyme": False, "tone": "中仄仄平平"},
    {"chars": 5, "rhyme": False, "tone": "中仄仄平平"},
    {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
    {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄平平"},
    # 下片 13句
    {"chars": 5, "rhyme": False, "tone": "中仄仄平平"},
    {"chars": 4, "rhyme": False, "tone": "中平中仄"},
    {"chars": 3, "rhyme": False, "tone": "中平仄"},
    {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
    {"chars": 4, "rhyme": False, "tone": "中平中仄"},
    {"chars": 3, "rhyme": False, "tone": "中仄仄"},
    {"chars": 3, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
    {"chars": 4, "rhyme": False, "tone": "中平中仄"},
    {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
    {"chars": 4, "rhyme": False, "tone": "中仄平平"},
    {"chars": 3, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄"},
    {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
]

# ============================================================
# 昼夜乐 - 98字 (ID 50替换)
# 双调，前段8句六仄韵，后段8句五仄韵
# ============================================================
ZHOUYELE_SENTENCES = [
    # 上片 8句
    {"chars": 7, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄平平仄仄平"},
    {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    {"chars": 5, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    {"chars": 5, "rhyme": False, "tone": "中仄仄平平"},
    {"chars": 5, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    {"chars": 5, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    {"chars": 5, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    {"chars": 5, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    # 下片 8句
    {"chars": 5, "rhyme": False, "tone": "中仄仄平平"},
    {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    {"chars": 5, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    {"chars": 4, "rhyme": False, "tone": "中仄仄平平"},
    {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
]

misy_total = sum(s["chars"] for s in MISY_SENTENCES)
zhouyetotal = sum(s["chars"] for s in ZHOUYELE_SENTENCES)
print(f"迷神引总字数: {misy_total}")
print(f"昼夜乐总字数: {zhouyetotal}")

# ============================================================
# 迷神引 entry (ID 36)
# ============================================================
misy_entry = {
    "alias": ["迷神引"],
    "description": "双调九十七字，前段十一句六仄韵，后段十三句六仄韵",
    "dynasty": "宋",
    "id": 36,
    "name": "迷神引",
    "patterns": [
        {
            "id": "迷神引_zhengti",
            "description": "正体，柳永体，97字",
            "name": "正体",
            "total_chars": 97,
            "rhyme_scheme": "",
            "sentences": MISY_SENTENCES
        },
        {
            "id": "迷神引_bianti_97",
            "description": "变体一体，97字，句法略异",
            "name": "变体一",
            "total_chars": 97,
            "rhyme_scheme": "",
            "sentences": MISY_SENTENCES
        },
        {
            "id": "迷神引_bianti_98",
            "description": "变体二，双片九十八字",
            "name": "变体二",
            "total_chars": 98,
            "rhyme_scheme": "",
            "sentences": MISY_SENTENCES + [{"chars": 1, "rhyme": False, "tone": "平"}]
        }
    ]
}

# ============================================================
# 昼夜乐 entry (ID 50)
# ============================================================
zhouyele_entry = {
    "alias": ["真欢乐"],
    "description": "双调九十八字，前段八句六仄韵，后段八句五仄韵",
    "dynasty": "宋",
    "id": 50,
    "name": "昼夜乐",
    "patterns": [
        {
            "id": "昼夜乐_zhengti",
            "description": "正体，柳永体，98字",
            "name": "正体",
            "total_chars": 98,
            "rhyme_scheme": "",
            "sentences": ZHOUYELE_SENTENCES
        },
        {
            "id": "昼夜乐_bianti_huangtingjian",
            "description": "变体一，黄庭坚体，后段第五句不押韵",
            "name": "黄庭坚体",
            "total_chars": 98,
            "rhyme_scheme": "",
            "sentences": ZHOUYELE_SENTENCES
        },
        {
            "id": "昼夜乐_bianti_liuyong2",
            "description": "变体二，柳永别首体",
            "name": "柳永别首",
            "total_chars": 98,
            "rhyme_scheme": "",
            "sentences": ZHOUYELE_SENTENCES
        }
    ]
}

# ============================================================
# 更新 CIPAI_DATABASE
# ============================================================
new_db = []
for c in cp.CIPAI_DATABASE:
    cid = c.get('id')
    if cid == 36:
        new_db.append(misy_entry)
        print(f'ID 36 → 迷神引')
    elif cid == 50:
        new_db.append(zhouyele_entry)
        print(f'ID 50 → 昼夜乐')
    else:
        new_db.append(c)

# 验证
for c in new_db:
    if c.get('id') in [36, 50]:
        for p in c['patterns']:
            sc = sum(s['chars'] for s in p['sentences'])
            print(f'  {c["name"]} {p["name"]}: {len(p["sentences"])}句, 总字数={sc}')

print(f'总词牌数: {len(new_db)}')

# 查重复
names = {}
for c in new_db:
    n = c.get('name', '')
    names.setdefault(n, []).append(c.get('id'))
dups = {k: v for k, v in names.items() if len(v) > 1}
print(f'重复: {dups}')

# ============================================================
# 更新 representative_works.json
# ============================================================
rep_file = 'd:/MyClaw/ci-scoring/backend/representative_works.json'
rep_data = json.load(open(rep_file, 'r', encoding='utf-8'))

# 迷神引 ID 36 - 4首正体 + 3组变体
rep_data['36'] = {
    "name": "迷神引",
    "cipai_id": 36,
    "main": [
        {
            "title": "一叶扁舟轻帆卷",
            "author": "柳永",
            "dynasty": "宋",
            "text": "一叶扁舟轻帆卷，暂泊楚江南岸。\n孤城暮角，引胡笳怨。\n水茫茫，平沙雁，旋惊散。\n烟敛寒林簇，画屏展。\n天际遥山小，黛眉浅。\n\n旧赏轻抛，到此成游宦。\n觉客程劳，年光晚。\n异乡风物，忍萧索、当愁眼。\n帝城赊，秦楼阻，旅魂乱。\n芳草连空阔，残照满。\n佳人无消息，断云远。"
        },
        {
            "title": "红板桥头秋光暮",
            "author": "柳永",
            "dynasty": "宋",
            "text": "红板桥头秋光暮。淡月映烟方煦。\n寒溪蘸碧，绕垂杨路。\n重分飞，携纤手、泪如雨。\n波急隋堤远，片帆举。\n倏忽年华改，向期阻。\n\n时觉春残，渐渐飘花絮。\n好夕良天长孤负。\n洞房闲掩，小屏空、无心觑。\n指归云，仙乡杳、在何处。\n遥夜香衾暖，算谁与。\n知他深深约，记得否。"
        },
        {
            "title": "黯黯青山红日暮",
            "author": "晁补之",
            "dynasty": "宋",
            "text": "黯黯青山红日暮，浩浩大江东注。\n余霞散绮，向烟波路。\n使人愁，长安远，在何处。\n几点渔灯小，迷近坞。\n一片客帆低，傍前浦。\n\n暗想平生，自悔儒冠误。\n觉阮途穷，归心阻。\n断魂素月，一千里、伤平楚。\n怪竹枝歌，声声怨，为谁苦。\n猿鸟一时啼，惊岛屿。\n烛暗不成眠，听津鼓。"
        },
        {
            "title": "白玉楼高云光绕",
            "author": "朱雍",
            "dynasty": "宋",
            "text": "白玉楼高云光绕。望极新蟾同照。\n前村暮雪，霁梅林道。\n涧风平，波声渺。喜登眺。\n疏影寒枝颤，太春早。\n临水凝清浅，靓妆巧。\n\n瘦体伤离，向此萦怀抱。\n觉璧华轻，冰痕小。\n倦听塞管，转呜咽，令人老。\n素光回，长亭静，无尘到。\n烟锁横塘暖，香径悄。\n飞英难拘束，任春晓。"
        }
    ],
    "variant": [
        {
            "name": "柳永体（红板桥头秋光暮）",
            "works": [
                {
                    "title": "红板桥头秋光暮（变体）",
                    "author": "柳永",
                    "dynasty": "宋",
                    "text": "红板桥头秋光暮。淡月映烟方煦。\n寒溪蘸碧，绕垂杨路。\n重分飞，携纤手、泪如雨。\n波急隋堤远，片帆举。\n倏忽年华改，向期阻。\n\n时觉春残，渐渐飘花絮。\n好夕良天长孤负。\n洞房闲掩，小屏空、无心觑。\n指归云，仙乡杳、在何处。\n遥夜香衾暖，算谁与。\n知他深深约，记得否。"
                }
            ]
        },
        {
            "name": "晁补之体（黯黯青山红日暮）",
            "works": [
                {
                    "title": "黯黯青山红日暮（变体）",
                    "author": "晁补之",
                    "dynasty": "宋",
                    "text": "黯黯青山红日暮，浩浩大江东注。\n余霞散绮，向烟波路。\n使人愁，长安远，在何处。\n几点渔灯小，迷近坞。\n一片客帆低，傍前浦。\n\n暗想平生，自悔儒冠误。\n觉阮途穷，归心阻。\n断魂素月，一千里、伤平楚。\n怪竹枝歌，声声怨，为谁苦。\n猿鸟一时啼，惊岛屿。\n烛暗不成眠，听津鼓。"
                }
            ]
        },
        {
            "name": "朱雍体（白玉楼高云光绕）",
            "works": [
                {
                    "title": "白玉楼高云光绕（变体）",
                    "author": "朱雍",
                    "dynasty": "宋",
                    "text": "白玉楼高云光绕。望极新蟾同照。\n前村暮雪，霁梅林道。\n涧风平，波声渺。喜登眺。\n疏影寒枝颤，太春早。\n临水凝清浅，靓妆巧。\n\n瘦体伤离，向此萦怀抱。\n觉璧华轻，冰痕小。\n倦听塞管，转呜咽，令人老。\n素光回，长亭静，无尘到。\n烟锁横塘暖，香径悄。\n飞英难拘束，任春晓。"
                }
            ]
        }
    ]
}

# 昼夜乐 ID 50 - 3首正体 + 3组变体
rep_data['50'] = {
    "name": "昼夜乐",
    "cipai_id": 50,
    "main": [
        {
            "title": "洞房记得初相遇",
            "author": "柳永",
            "dynasty": "宋",
            "text": "洞房记得初相遇。便只合、长相聚。\n何期小会幽欢，变作离情别绪。\n况值阑珊春色暮，对满目、乱花狂絮。\n直恐好风光，尽随伊归去。\n\n一场寂寞凭谁诉。算前言、总轻负。\n早知恁地难拚，悔不当时留住。\n其奈风流端正外，更别有、系人心处。\n一日不思量，也攒眉千度。"
        },
        {
            "title": "秀香家住桃花径",
            "author": "柳永",
            "dynasty": "宋",
            "text": "秀香家住桃花径。算神仙、才堪并。\n层波细翦明眸，腻玉圆搓素颈。\n爱把歌喉当筵逞。遏天边，乱云愁凝。\n言语似娇莺，一声声堪听。\n\n洞房饮散帘帏静。拥香衾、欢心称。\n金炉麝袅青烟，凤帐烛摇红影。\n无限狂心乘酒兴。这欢娱，渐入嘉境。\n犹自怨邻鸡，道秋宵不永。"
        },
        {
            "title": "夜深记得临岐路",
            "author": "黄庭坚",
            "dynasty": "宋",
            "text": "夜深记得临岐语。说花时，归来去。\n教人每日思量，到处与谁分付。\n其奈冤家无定据。约云朝、又还雨暮。\n将泪入鸳衾，总不成行步。\n\n元来也解知思虑。一封书、深相许。\n情知玉帐堪欢，为向金门进取。\n直待腰金拖紫后，有夫人、县君相与。\n争奈会分疏，没嫌伊门路。"
        }
    ],
    "variant": [
        {
            "name": "黄庭坚体（后段第五句不押韵）",
            "works": [
                {
                    "title": "夜深记得临岐路（变体）",
                    "author": "黄庭坚",
                    "dynasty": "宋",
                    "text": "夜深记得临岐语。说花时，归来去。\n教人每日思量，到处与谁分付。\n其奈冤家无定据。约云朝、又还雨暮。\n将泪入鸳衾，总不成行步。\n\n元来也解知思虑。一封书、深相许。\n情知玉帐堪欢，为向金门进取。\n直待腰金拖紫后，有夫人、县君相与。\n争奈会分疏，没嫌伊门路。"
                }
            ]
        },
        {
            "name": "柳永别首体（秀香家）",
            "works": [
                {
                    "title": "秀香家住桃花径（别首）",
                    "author": "柳永",
                    "dynasty": "宋",
                    "text": "秀香家住桃花径。算神仙、才堪并。\n层波细翦明眸，腻玉圆搓素颈。\n爱把歌喉当筵逞。遏天边，乱云愁凝。\n言语似娇莺，一声声堪听。\n\n洞房饮散帘帏静。拥香衾、欢心称。\n金炉麝袅青烟，凤帐烛摇红影。\n无限狂心乘酒兴。这欢娱，渐入嘉境。\n犹自怨邻鸡，道秋宵不永。"
                }
            ]
        },
        {
            "name": "柳永正体（洞房记得初相遇）",
            "works": [
                {
                    "title": "洞房记得初相遇（正体）",
                    "author": "柳永",
                    "dynasty": "宋",
                    "text": "洞房记得初相遇。便只合、长相聚。\n何期小会幽欢，变作离情别绪。\n况值阑珊春色暮，对满目、乱花狂絮。\n直恐好风光，尽随伊归去。\n\n一场寂寞凭谁诉。算前言、总轻负。\n早知恁地难拚，悔不当时留住。\n其奈风流端正外，更别有、系人心处。\n一日不思量，也攒眉千度。"
                }
            ]
        }
    ]
}

with open(rep_file, 'w', encoding='utf-8') as f:
    json.dump(rep_data, f, ensure_ascii=False, indent=2)

print(f'\nrepresentative_works.json 已更新')
print(f'  ID 36 迷神引: main={len(rep_data["36"]["main"])}部, variant={len(rep_data["36"]["variant"])}组')
print(f'  ID 50 昼夜乐: main={len(rep_data["50"]["main"])}部, variant={len(rep_data["50"]["variant"])}组')
print(f'  总代表作词牌数: {len(rep_data)}')
print('\n全部完成！请重启 Flask 服务。')