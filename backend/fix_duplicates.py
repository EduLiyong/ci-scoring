# -*- coding: utf-8 -*-
"""
修复重复词牌：将ID 36(望海潮重复)替换为沁园春，ID 50(谒金门重复)替换为水龙吟
"""

import sys, json
sys.path.insert(0, 'd:/MyClaw/ci-scoring/backend')
from cipai_data import CIPAI_DATABASE

# ============================================================
# 沁园春 - 114字 (ID 36替换)
# ============================================================
qinyuanchun_entry = {
    "alias": ["寿星明", "东仙", "洞庭春色"],
    "description": "双调一百十四字，前段十三句四平韵，后段十二句五平韵",
    "dynasty": "宋",
    "id": 36,
    "name": "沁园春",
    "patterns": [
        {
            "id": "沁园春_zhengti",
            "description": "正体，114字",
            "name": "正体",
            "total_chars": 114,
            "rhyme_scheme": "",
            "sentences": [
                {"chars": 7, "rhyme": True,  "rhyme_type": "平", "tone": "中仄平平仄仄平平"},
                {"chars": 7, "rhyme": False, "tone": "仄仄平平仄仄仄平"},
                {"chars": 7, "rhyme": True,  "rhyme_type": "平", "tone": "仄仄平平仄仄平"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "平", "tone": "中仄平平"},
                {"chars": 7, "rhyme": False, "tone": "中平中仄中仄平平中仄平"},
                {"chars": 5, "rhyme": True,  "rhyme_type": "平", "tone": "平平仄仄平平"},
                {"chars": 4, "rhyme": False, "tone": "仄中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "平", "tone": "中仄平平"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "平", "tone": "仄平仄仄"},
                {"chars": 7, "rhyme": True,  "rhyme_type": "平", "tone": "仄中仄平平中仄平"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "平", "tone": "中仄平平"},
                {"chars": 7, "rhyme": False, "tone": "中平中仄中仄平平中仄平"},
                {"chars": 5, "rhyme": True,  "rhyme_type": "平", "tone": "平平仄仄平平"},
                {"chars": 4, "rhyme": False, "tone": "仄中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "平", "tone": "中仄平平"},
            ]
        },
        {
            "id": "沁园春_bianti_shiguo",
            "description": "变体一，刘过体，句法疏放",
            "name": "刘过体",
            "total_chars": 114,
            "rhyme_scheme": "",
            "sentences": [
                {"chars": 4, "rhyme": False, "tone": "仄仄平平"},
                {"chars": 7, "rhyme": True,  "rhyme_type": "平", "tone": "中仄平平仄仄平平"},
                {"chars": 4, "rhyme": False, "tone": "平平仄仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "平", "tone": "中仄平平"},
                {"chars": 7, "rhyme": False, "tone": "中平中仄中仄平平中仄平"},
                {"chars": 5, "rhyme": True,  "rhyme_type": "平", "tone": "平平仄仄平平"},
                {"chars": 4, "rhyme": False, "tone": "仄中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "平", "tone": "中仄平平"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "平", "tone": "仄平仄仄"},
                {"chars": 7, "rhyme": True,  "rhyme_type": "平", "tone": "仄中仄平平中仄平"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "平", "tone": "中仄平平"},
                {"chars": 7, "rhyme": False, "tone": "中平中仄中仄平平中仄平"},
                {"chars": 5, "rhyme": True,  "rhyme_type": "平", "tone": "平平仄仄平平"},
                {"chars": 4, "rhyme": False, "tone": "仄中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "平", "tone": "中仄平平"},
            ]
        },
        {
            "id": "沁园春_bianti_qinshao",
            "description": "变体二，秦观减字体，名《洞庭春色》",
            "name": "秦观减字体",
            "total_chars": 112,
            "rhyme_scheme": "",
            "sentences": [
                {"chars": 6, "rhyme": True,  "rhyme_type": "平", "tone": "仄仄平平仄仄平"},
                {"chars": 7, "rhyme": False, "tone": "平平仄仄仄仄平平"},
                {"chars": 7, "rhyme": True,  "rhyme_type": "平", "tone": "仄仄平平仄仄平"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "平", "tone": "中仄平平"},
                {"chars": 7, "rhyme": False, "tone": "中平中仄中仄平平中仄平"},
                {"chars": 5, "rhyme": True,  "rhyme_type": "平", "tone": "平平仄仄平平"},
                {"chars": 4, "rhyme": False, "tone": "仄中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "平", "tone": "中仄平平"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "平", "tone": "仄平仄仄"},
                {"chars": 7, "rhyme": True,  "rhyme_type": "平", "tone": "仄中仄平平中仄平"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "平", "tone": "中仄平平"},
                {"chars": 7, "rhyme": False, "tone": "中平中仄中仄平平中仄平"},
                {"chars": 5, "rhyme": True,  "rhyme_type": "平", "tone": "平平仄仄平平"},
                {"chars": 4, "rhyme": False, "tone": "仄中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "平", "tone": "中仄平平"},
            ]
        }
    ]
}

# ============================================================
# 水龙吟 - 102字 (ID 50替换)
# ============================================================
shuilongyin_entry = {
    "alias": ["龙吟曲", "鼓笛慢", "小楼连苑", "丰年瑞"],
    "description": "双调一百零二字，前后段各十一句四仄韵",
    "dynasty": "宋",
    "id": 50,
    "name": "水龙吟",
    "patterns": [
        {
            "id": "水龙吟_zhengti",
            "description": "正体，苏轼体，102字",
            "name": "正体",
            "total_chars": 102,
            "rhyme_scheme": "",
            "sentences": [
                {"chars": 6, "rhyme": False, "tone": "中平中仄平平"},
                {"chars": 7, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄仄平平"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中仄平平"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
                {"chars": 5, "rhyme": False, "tone": "仄中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中平仄仄平平仄"},
                {"chars": 6, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄中平中仄"},
                {"chars": 7, "rhyme": True,  "rhyme_type": "仄", "tone": "仄平平仄仄平平"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中仄平平"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
                {"chars": 5, "rhyme": False, "tone": "仄平平仄仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "仄平平仄"},
            ]
        },
        {
            "id": "水龙吟_bianti_qinguan",
            "description": "变体一，秦观体，起句六字次句七字",
            "name": "秦观体",
            "total_chars": 102,
            "rhyme_scheme": "",
            "sentences": [
                {"chars": 6, "rhyme": False, "tone": "中平中仄平平"},
                {"chars": 7, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄仄平平"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中仄平平"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
                {"chars": 5, "rhyme": False, "tone": "仄中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中平仄仄平平仄"},
                {"chars": 6, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄中平中仄"},
                {"chars": 7, "rhyme": True,  "rhyme_type": "仄", "tone": "仄平平仄仄平平"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中仄平平"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
                {"chars": 5, "rhyme": False, "tone": "仄平平仄仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "仄平平仄"},
            ]
        },
        {
            "id": "水龙吟_bianti_zhangjie",
            "description": "变体二，章楶体，杨花词",
            "name": "章楶体",
            "total_chars": 102,
            "rhyme_scheme": "",
            "sentences": [
                {"chars": 7, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄仄平平"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中仄平平"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
                {"chars": 5, "rhyme": False, "tone": "仄中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中平仄仄平平仄"},
                {"chars": 6, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄中平中仄"},
                {"chars": 7, "rhyme": True,  "rhyme_type": "仄", "tone": "仄平平仄仄平平"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
                {"chars": 4, "rhyme": False, "tone": "中仄平平"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
                {"chars": 5, "rhyme": False, "tone": "仄平平仄仄"},
                {"chars": 4, "rhyme": False, "tone": "中平中仄"},
                {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "仄平平仄"},
            ]
        }
    ]
}

# ============================================================
# 1. 修改 cipai_data.py 中的 ID 36 和 ID 50
# ============================================================
new_db = []
for c in CIPAI_DATABASE:
    cid = c.get('id')
    if cid == 36:
        new_db.append(qinyuanchun_entry)
        print(f'ID 36 替换为: 沁园春')
    elif cid == 50:
        new_db.append(shuilongyin_entry)
        print(f'ID 50 替换为: 水龙吟')
    else:
        new_db.append(c)

# 验证
for c in new_db:
    if c.get('id') in [36, 50]:
        print(f'  ID {c["id"]}: {c["name"]}, patterns: {len(c["patterns"])}')

print(f'\n总词牌数: {len(new_db)}')

# ============================================================
# 2. 更新 representative_works.json
# ============================================================
rep_file = 'd:/MyClaw/ci-scoring/backend/representative_works.json'
rep_data = json.load(open(rep_file, 'r', encoding='utf-8'))

# 沁园春 ID 36 - 5首正体 + 3首变体
rep_data['36'] = {
    "name": "沁园春",
    "cipai_id": 36,
    "main": [
        {
            "title": "孤馆灯青",
            "author": "苏轼",
            "dynasty": "宋",
            "text": "孤馆灯青，野店鸡号，旅枕梦残。\n渐月华收练，晨霜耿耿；云山摛锦，朝露漙漙。\n世路无穷，劳生有限，似此区区长鲜欢。\n微吟罢，凭征鞍无语，往事千端。\n\n当时共客长安，似二陆初来俱少年。\n有笔头千字，胸中万卷；致君尧舜，此事何难？\n用舍由时，行藏在我，袖手何妨闲处看。\n身长健，但优游卒岁，且斗尊前。"
        },
        {
            "title": "宿霭迷空",
            "author": "秦观",
            "dynasty": "宋",
            "text": "宿霭迷空，腻云笼日，昼景渐长。\n正兰皋泥润，谁家燕喜；蜜脾香少，触处蜂忙。\n尽日无人帘幕挂，更风递游丝时过墙。\n微雨后，有桃愁杏怨，红泪淋浪。\n\n风流寸心易感，但依依伫立，回尽柔肠。\n念小奁瑶鉴，重匀绛蜡；玉笼金斗，时熨沈香。\n柳下相将游冶处，便回首青楼成异乡。\n相忆事，纵蛮笺万叠，难写微茫。"
        },
        {
            "title": "将止酒",
            "author": "辛弃疾",
            "dynasty": "宋",
            "text": "杯汝来前！老子今朝，点检形骸。\n甚长年抱渴，咽如焦釜；于今喜睡，气似奔雷。\n汝说刘伶，古今达者，醉后何妨死便埋。\n浑如此，叹汝于知己，真少恩哉！\n\n更凭歌舞为媒。算合作人间鸩毒猜。\n况怨无大小，生于所爱；物无美恶，过则为灾。\n与汝成言：勿留亟退，吾力犹能肆汝杯。\n杯再拜，道麾之即去，招则须来。"
        },
        {
            "title": "斗酒彘肩",
            "author": "刘过",
            "dynasty": "宋",
            "text": "斗酒彘肩，风雨渡江，岂不快哉！\n被香山居士，约林和靖，与东坡老，驾勒吾回。\n坡谓：西湖，正如西子，浓抹淡妆临镜台。\n二公者，皆掉头不顾，只管衔杯。\n\n白云：天竺飞来。图画里、峥嵘楼观开。\n爱东西双涧，纵横水绕，两峰南北，高下云堆。\n逋曰：不然，暗香浮动，争似孤山先探梅。\n须晴去，访稼轩未晚，且此徘徊。"
        },
        {
            "title": "孤鹤归飞",
            "author": "陆游",
            "dynasty": "宋",
            "text": "孤鹤归飞，再过辽天，换尽旧人。\n念累累枯冢，茫茫梦境，王侯蝼蚁，毕竟成尘。\n载酒园林，寻花巷陌，当日何曾轻负春。\n流年改，叹围腰带剩，点鬓霜新。\n\n交亲散落如云，又岂料如今馀此身。\n幸眼明身健，茶甘饭软，非惟我老，更有人贫。\n躲尽危机，消残壮志，短艇湖中闲采莼。\n吾何恨，有渔翁共醉，溪友为邻。"
        }
    ],
    "variant": [
        {
            "name": "刘过体（斗酒彘肩）",
            "works": [
                {
                    "title": "斗酒彘肩（疏荡体）",
                    "author": "刘过",
                    "dynasty": "宋",
                    "text": "斗酒彘肩，风雨渡江，岂不快哉！\n被香山居士，约林和靖，与东坡老，驾勒吾回。\n坡谓：西湖，正如西子，浓抹淡妆临镜台。\n二公者，皆掉头不顾，只管衔杯。\n\n白云：天竺飞来。图画里、峥嵘楼观开。\n爱东西双涧，纵横水绕，两峰南北，高下云堆。\n逋曰：不然，暗香浮动，争似孤山先探梅。\n须晴去，访稼轩未晚，且此徘徊。"
                }
            ]
        },
        {
            "name": "秦观减字体（洞庭春色）",
            "works": [
                {
                    "title": "洞庭春色",
                    "author": "秦观",
                    "dynasty": "宋",
                    "text": "宿霭迷空，腻云笼日，昼景渐长。\n正兰皋泥润，谁家燕喜；蜜脾香少，触处蜂忙。\n尽日无人帘幕挂，更风递游丝时过墙。\n微雨后，有桃愁杏怨，红泪淋浪。\n\n风流寸心易感，但依依伫立，回尽柔肠。\n念小奁瑶鉴，重匀绛蜡；玉笼金斗，时熨沈香。\n柳下相将游冶处，便回首青楼成异乡。\n相忆事，纵蛮笺万叠，难写微茫。"
                }
            ]
        },
        {
            "name": "吴渊体（寿弟相国）",
            "works": [
                {
                    "title": "寿弟相国",
                    "author": "吴渊",
                    "dynasty": "宋",
                    "text": "玉带猩袍，遥望翠华，马去似龙。\n拥貂蝉争出，千官鳞集；貔貅不断，万骑云从。\n细柳营开，觚棱天近，淡淡春山如画。\n知否来栖，鸣鸠唤雨，唤回晓光多少。\n\n台衮兼将相，运筹帷幄，ellini久更深算。\n未免怀忧，聊将清酌，为兄勋阀娣缌。\n人间祸福难论，付乾坤、羊裘乐渔钓。\n待归来长啸，金鱼换酒，醉忘秦赵。"
                }
            ]
        }
    ]
}

# 水龙吟 ID 50 - 5首正体 + 3首变体
rep_data['50'] = {
    "name": "水龙吟",
    "cipai_id": 50,
    "main": [
        {
            "title": "次韵章质夫杨花词",
            "author": "苏轼",
            "dynasty": "宋",
            "text": "似花还似非花，也无人惜从教坠。\n抛家傍路，思量却是，无情有思。\n萦损柔肠，困酣娇眼，欲开还闭。\n梦随风万里，寻郎去处，又还被、莺呼起。\n\n不恨此花飞尽，恨西园、落红难缀。\n晓来雨过，遗踪何在？一池萍碎。\n春色三分，二分尘土，一分流水。\n细看来，不是杨花，点点是离人泪。"
        },
        {
            "title": "登建康赏心亭",
            "author": "辛弃疾",
            "dynasty": "宋",
            "text": "楚天千里清秋，水随天去秋无际。\n遥岑远目，献愁供恨，玉簪螺髻。\n落日楼头，断鸿声里，江南游子。\n把吴钩看了，栏杆拍遍，无人会，登临意。\n\n休说鲈鱼堪脍，尽西风，季鹰归未？\n求田问舍，怕应羞见，刘郎才气。\n可惜流年，忧愁风雨，树犹如此！\n倩何人唤取，红巾翠袖，揾英雄泪？"
        },
        {
            "title": "小楼连苑横空",
            "author": "秦观",
            "dynasty": "宋",
            "text": "小楼连苑横空，下窥绣毂雕鞍骤。\n朱帘半卷，单衣初试，清明时候。\n破暖轻风，弄晴微雨，欲无还有。\n卖花声过尽，斜阳院落，红成阵、飞鸳甃。\n\n玉佩丁东别后，怅佳期、参差难又。\n名缰利锁，天还知道，和天也瘦。\n花下重门，柳边深巷，不堪回首。\n念多情但有，当时皓月，向人依旧。"
        },
        {
            "title": "甲辰岁寿韩南涧尚书",
            "author": "辛弃疾",
            "dynasty": "宋",
            "text": "渡江天马南来，几人真是经纶手？\n长安父老，新亭风景，可怜依旧！\n夷甫诸人，神州沉陆，几曾回首！\n算平戎万里，功名本是，真儒事、君知否？\n\n况有文章山斗，对桐阴、满庭清昼。\n当年堕地，而今试看，风云奔走。\n绿野风烟，平泉草木，东山歌酒。\n待他年，整顿乾坤事了，为先生寿。"
        },
        {
            "title": "放船千里凌波去",
            "author": "朱敦儒",
            "dynasty": "宋",
            "text": "放船千里凌波去，略为吴山留顾。\n云屯水府，涛随神女，九江东注。\n北客翩然，壮心偏感，年华将暮。\n念伊嵩旧隐，巢由故友，南柯梦，遽如许。\n\n回首妖氛未扫，问人间、英雄何处？\n奇谋报国，可怜无用，尘昏白羽。\n铁锁横江，锦帆冲浪，孙郎良苦。\n但愁敲桂棹，悲吟梁父，泪流如雨。"
        }
    ],
    "variant": [
        {
            "name": "章楶体（杨花）",
            "works": [
                {
                    "title": "杨花",
                    "author": "章楶",
                    "dynasty": "宋",
                    "text": "燕忙莺懒芳残，正堤上、柳花飘坠。\n轻飞乱舞，点画青林，全无才思。\n闲趁游丝，静临深院，日长门闭。\n傍珠帘散漫，垂垂欲下，依前被、风扶起。\n\n兰帐玉人睡觉，怪春衣、雪沾琼缀。\n绣床旋满，香球无数，才圆却碎。\n时见蜂儿，仰粘轻粉，鱼吞池水。\n望章台路杳，金鞍游荡，有盈盈泪。"
                }
            ]
        },
        {
            "name": "秦观体（小楼连苑）",
            "works": [
                {
                    "title": "小楼连苑横空",
                    "author": "秦观",
                    "dynasty": "宋",
                    "text": "小楼连苑横空，下窥绣毂雕鞍骤。\n朱帘半卷，单衣初试，清明时候。\n破暖轻风，弄晴微雨，欲无还有。\n卖花声过尽，斜阳院落，红成阵、飞鸳甃。\n\n玉佩丁东别后，怅佳期、参差难又。\n名缰利锁，天还知道，和天也瘦。\n花下重门，柳边深巷，不堪回首。\n念多情但有，当时皓月，向人依旧。"
                }
            ]
        },
        {
            "name": "陈亮体（春恨）",
            "works": [
                {
                    "title": "春恨",
                    "author": "陈亮",
                    "dynasty": "宋",
                    "text": "闹花深处层楼，画帘半卷东风软。\n春归翠陌，平莎茸嫩，垂杨金浅。\n迟日催花，淡云阁雨，轻寒轻暖。\n恨芳菲世界，游人未赏，都付与、莺和燕。\n\n寂寞凭高念远，向南楼、一声归雁。\n金钗斗草，青丝勒马，风流云散。\n罗绶分香，翠绡封泪，几多幽怨？\n正销魂，又是疏烟淡月，子规声断。"
                }
            ]
        }
    ]
}

# 保存
with open(rep_file, 'w', encoding='utf-8') as f:
    json.dump(rep_data, f, ensure_ascii=False, indent=2)

print('\nrepresentative_works.json 已更新')
print(f'  ID 36 沁园春: main={len(rep_data["36"]["main"])}部, variant={len(rep_data["36"]["variant"])}组')
print(f'  ID 50 水龙吟: main={len(rep_data["50"]["main"])}部, variant={len(rep_data["50"]["variant"])}组')
print(f'  总代表作词牌数: {len(rep_data)}')

# 验证无其他重复名称
names_check = {}
for c in new_db:
    n = c.get('name', '')
    if n not in names_check:
        names_check[n] = []
    names_check[n].append(c.get('id'))

dups = {k: v for k, v in names_check.items() if len(v) > 1}
print(f'\n剩余重复词牌数: {len(dups)}')
for k, v in dups.items():
    print(f'  {k}: IDs {v}')
print('\n完成！')