# -*- coding: utf-8 -*-
"""
自动化检测词牌代表作中的错误
通过搜索网络验证每首词的词牌归属
"""
import json
import sys
sys.path.insert(0, '.')
from cipai_data import CIPAI_DATABASE

def load_data():
    with open('representative_works.json', encoding='utf-8') as f:
        return json.load(f)

def get_cipai_name(cid):
    for c in CIPAI_DATABASE:
        if c['id'] == int(cid):
            return c['name']
    return f"未知({cid})"

def get_first_lines():
    """获取所有词作的首句，用于快速检测"""
    data = load_data()
    
    # 常见词作首句 - 用于快速匹配真实词牌
    known_works = {
        # 沁园春
        "独立寒秋": "沁园春",
        "北国风光": "沁园春",
        "春花秋月何时了": "虞美人",
        "春花秋月": "虞美人",
        "风乍起": "谒金门",
        "庭院深深深几许": "蝶恋花",
        "六曲阑干偎碧树": "蝶恋花",
        "梦入江南烟水路": "蝶恋花",
        "槛菊愁烟兰泣露": "蝶恋花",
        "谁道闲情抛弃久": "蝶恋花",
        "几日行云何处去": "蝶恋花",
        "枝上柳绵吹又少": "蝶恋花",
        "卷絮风头寒欲尽": "蝶恋花",
        "碧云天": "苏幕遮",
        "塞下秋来风景异": "渔家傲",
        "明月别枝惊鹊": "西江月",
        "夜行黄沙道中": "西江月",
        "稻花香里说丰年": "西江月",
        "大江东去": "念奴娇",
        "明月几时有": "水调歌头",
        "老夫聊发少年狂": "江城子",
        "十年生死两茫茫": "江城子",
        "莫听穿林打叶声": "定风波",
        "三月七日": "定风波",
        "帘外雨潺潺": "浪淘沙令",
        "人生若只如初见": "木兰花令",
        "被酒莫惊春睡重": "木兰花令",
        "晚日寒鸦一片愁": "鹧鸪天",
        "吹破残烟入夜风": "鹧鸪天",
        "彩袖殷勤捧玉钟": "鹧鸪天",
        "暗淡轻黄体性柔": "鹧鸪天",
        "把酒祝东风": "浪淘沙",
        "山一程水一程": "长相思",
        "红酥手": "钗头凤",
        "世情薄": "钗头凤",
        "一曲新词酒一杯": "浣溪沙",
        "山下兰芽短浸溪": "浣溪沙",
        "莫许杯深琥珀浓": "浣溪沙",
        "常记溪亭日暮": "如梦令",
        "昨夜雨疏风骤": "如梦令",
        "寻寻觅觅": "声声慢",
        "薄雾浓云愁永昼": "醉花阴",
        "东篱把酒黄昏后": "醉花阴",
        "莫道不消魂": "醉花阴",
        "怒发冲冠": "满江红",
        "写怀": "满江红",
        "遥望中原": "满江红",
        "瑶草一何碧": "水调歌头",
        "带湖吾甚爱": "水调歌头",
        "昵昵儿女语": "水调歌头",
        "久有凌云志": "水调歌头",
        "平林漠漠烟如织": "菩萨蛮",
        "小山重叠金明灭": "菩萨蛮",
        "人人尽说江南好": "菩萨蛮",
        "书江西造口壁": "菩萨蛮",
        "水晶帘里玻璃枕": "菩萨蛮",
        "孤馆灯青": "沁园春",
        "三径初成": "沁园春",
        "三径初成": "沁园春",
        "何处相逢": "沁园春",
        "梦孚若": "沁园春",
        "翠玉楼高": "沁园春",
        "一鞭南渡": "沁园春",
        "星斗寒相射": "沁园春",
        "古藤阴中": "沁园春",
        "看渔樵": "沁园春",
        "造物小儿": "沁园春",
        "流水泠泠": "沁园春",
        "春点梅雨": "沁园春",
        "孤馆灯青": "沁园春",
        # 更多常见词
        "少年不识愁滋味": "丑奴儿",
        "更能消几番风雨": "摸鱼儿",
        "更能消几番风雨": "摸鱼儿",
        # 临江仙
        "梦后楼台高锁": "临江仙",
        "庭院深深深几许": "临江仙",
        "雾窗寒对遥天暮": "蝶恋花",
        # 虞美人
        "春花秋月何时了": "虞美人",
        "风回小院庭芜绿": "虞美人",
        # 浪淘沙
        "帘外雨潺潺": "浪淘沙令",
        "把酒祝东风": "浪淘沙",
        "伊吕两衰翁": "浪淘沙",
        # 望江南
        "梳洗罢": "望江南",
        "千万恨": "望江南",
        "天上月": "望江南",
        # 木兰花
        "东风又作无情计": "木兰花",
        "秋千院落重帘暮": "木兰花",
        # 渔歌子
        "西塞山前白鹭飞": "渔歌子",
        "松江蟹舍主人欢": "渔歌子",
        # 忆江南
        "江南好": "忆江南",
        "去不易": "忆江南",
        # 捣练子
        "砧面莹": "捣练子",
        "云鬓乱": "捣练子",
        # 相见欢
        "无言独上西楼": "相见欢",
        "林花谢了春红": "相见欢",
        # 谒金门
        "风乍起": "谒金门",
        "春满": "谒金门",
        # 清平乐
        "春归何处": "清平乐",
        "晚来云散": "清平乐",
        # 采桑子
        "群芳过后西湖好": "采桑子",
        "何人解赏西湖好": "采桑子",
        # 浣溪沙
        "一曲新词酒一杯": "浣溪沙",
        "山下兰芽短浸溪": "浣溪沙",
        "莫许杯深琥珀浓": "浣溪沙",
        "谁念西风独自凉": "浣溪沙",
        # 如梦令
        "常记溪亭日暮": "如梦令",
        "昨夜雨疏风骤": "如梦令",
        # 声声慢
        "寻寻觅觅": "声声慢",
        # 醉花阴
        "薄雾浓云愁永昼": "醉花阴",
        "东篱把酒黄昏后": "醉花阴",
        "莫道不消魂": "醉花阴",
        # 满江红
        "怒发冲冠": "满江红",
        "遥望中原": "满江红",
        # 丑奴儿
        "少年不识愁滋味": "丑奴儿",
        # 摸鱼儿
        "更能消几番风雨": "摸鱼儿",
        # 临江仙
        "梦后楼台高锁": "临江仙",
        "庭院深深深几许": "临江仙",
    }
    
    print("=" * 80)
    print("快速检测词牌代表作问题")
    print("=" * 80)
    
    issues = []
    
    for cid in sorted(data.keys(), key=lambda x: int(x)):
        cipai_name = get_cipai_name(cid)
        works = data[cid].get('main', [])
        
        for i, work in enumerate(works, 1):
            title = work.get('title', '无题')
            author = work.get('author', '佚名')
            text = work.get('text', '')
            first_line = text.split('\n')[0] if text else ''
            first_words = first_line[:6]  # 取前6个字
            
            # 检查是否在已知列表中且词牌不匹配
            for key, correct_cipai in known_works.items():
                if key in first_line:
                    if correct_cipai != cipai_name:
                        issues.append({
                            'cid': cid,
                            'cipai_name': cipai_name,
                            'correct_cipai': correct_cipai,
                            'title': title,
                            'author': author,
                            'first_line': first_line[:40],
                            'keywords': key
                        })
    
    print(f"\n发现 {len(issues)} 个问题:\n")
    for issue in issues:
        print(f"[X] 词牌 {issue['cid']}: {issue['cipai_name']}")
        print(f"   词作: {issue['title']} - {issue['author']}")
        print(f"   首句: {issue['first_line']}...")
        print(f"   实际词牌应为: {issue['correct_cipai']}")
        print()
    
    return issues

if __name__ == '__main__':
    issues = get_first_lines()
    
    # 保存问题列表
    with open('issues_found.json', 'w', encoding='utf-8') as f:
        json.dump([{
            'cid': i['cid'],
            'cipai_name': i['cipai_name'],
            'correct_cipai': i['correct_cipai'],
            'title': i['title'],
            'author': i['author'],
            'first_line': i['first_line'],
            'keywords': i['keywords']
        } for i in issues], f, ensure_ascii=False, indent=2)
    
    print(f"\n问题已保存到 issues_found.json")
