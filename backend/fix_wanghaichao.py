# -*- coding: utf-8 -*-
"""修复望海潮(id=36)的三首代表作标点"""
import json

path = 'd:/MyClaw/ci-scoring/backend/representative_works.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

key = '36'

# 正确原文
data[key]['main'] = [
    {
        "title": "东南形胜",
        "author": "柳永",
        "dynasty": "宋",
        "text": "东南形胜，三吴都会，钱塘自古繁华。烟柳画桥，风帘翠幕，参差十万人家。云树绕堤沙，怒涛卷霜雪，天堑无涯。市列珠玑，户盈罗绮，竞豪奢。\n\n重湖叠巘清嘉，有三秋桂子，十里荷花。羌管弄晴，菱歌泛夜，嬉嬉钓叟莲娃。千骑拥高牙，乘醉听箫鼓，吟赏烟霞。异日图将好景，归去凤池夸。",
        "zi": "耆卿",
        "hao": "柳三变"
    },
    {
        "title": "梅英疏淡",
        "author": "秦观",
        "dynasty": "宋",
        "text": "梅英疏淡，冰澌溶泄，东风暗换年华。金谷俊游，铜驼巷陌，新晴细履平沙。长记误随车，正絮翻蝶舞，芳思交加。柳下桃蹊，乱分春色到人家。\n\n西园夜饮鸣笳。有华灯碍月，飞盖妨花。兰苑未空，行人渐老，重来是事堪嗟。烟暝酒旗斜。但倚楼极目，时见栖鸦。无奈归心，暗随流水到天涯。",
        "zi": "少游",
        "hao": "太虚"
    },
    {
        "title": "上兰州守",
        "author": "邓千江",
        "dynasty": "金",
        "text": "云雷天堑，金汤地险，名藩自古皋兰。营屯绣错，山形米聚，喉襟百二秦关。鏖战血犹殷。见阵云冷落，时有雕盘。静塞楼头晓月，依旧玉弓弯。\n\n看看，定远西还。有元戎阃命，上将斋坛。区脱昼空，兜零夕举，甘泉又报平安。吹笛虎牙闲。且宴陪珠履，歌按云鬟。招取英灵毅魄，长绕贺兰山。",
        "zi": "",
        "hao": ""
    }
]

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("望海潮代表作已修复！")
# 验证
with open(path, 'r', encoding='utf-8') as f:
    d2 = json.load(f)
for w in d2[key]['main']:
    print(f"  {w['title']} - {w['author']} ({w['dynasty']})")
    print(f"  字数: {len(w['text'].replace(chr(10), ''))}")
