"""Normalize researched STS1 Watcher facts and keep design analysis explicit."""
import json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
raw=json.loads(Path('/private/tmp/watcher-reference/cards_clean.json').read_text())
source={r['name']:r for r in raw}
# [[base/upgrade]] describes a localized factual change, not a numerical model.
rows='''
Strike|打击|对单个敌人造成[[6/9]]点伤害。|伤害6→9|基础输出|初始牌；作为无条件单体攻击的基准。
Defend|防御|获得[[5/8]]点格挡。|格挡5→8|基础防御|初始牌；作为无条件格挡的基准。
Eruption|暴怒|对单个敌人造成9点伤害；进入愤怒。|费用2→1|姿态入口|先攻击再切姿态；本次攻击不自动享受新进入的愤怒倍率。
Vigilance|警惕|获得[[8/12]]点格挡；进入平静。|格挡8→12|防御／姿态入口|进入平静不直接给能量，退出平静才给。
Bowling Bash|碰撞连击|场上每有一个敌人，就对选定敌人造成一次[[7/10]]点伤害。|每击伤害7→10|多段输出|按敌人数对一个目标多次攻击，不是群攻。
Consecrate|供奉|对所有敌人造成[[5/8]]点伤害。|伤害5→8|低费群攻|0费但仍占抽牌与出牌次数。
Crescendo|渐强|保留。进入愤怒。消耗。|费用1→0|可保留姿态入口|一次性入口；需要退出手段或当回合结束战斗。
Crush Joints|粉碎关节|对单个敌人造成[[8/10]]点伤害；若上一张打出的牌是技能，施加[[1/2]]层易伤。|伤害8→10；易伤1→2|输出／减益|只检查紧邻上一张牌；易伤在本牌伤害后施加。
Cut Through Fate|斩破命运|对单个敌人造成[[7/9]]点伤害；占卜[[2/3]]；抽1张牌。|伤害7→9；占卜2→3|筛牌／抽牌／输出|先占卜后抽牌，可筛选本次要抽到的牌。
Empty Body|化体为空|获得[[7/10]]点格挡；退出当前姿态。|格挡7→10|防御／姿态出口|无姿态时不会凭空产生一次姿态切换。
Empty Fist|化拳为空|对单个敌人造成[[9/14]]点伤害；退出当前姿态。|伤害9→14|输出／姿态出口|先结算攻击，因而可享受退出前的愤怒或神格。
Evaluate|评估|获得[[6/10]]点格挡；将1张洞见洗入抽牌堆。|格挡6→10|防御／生成抽牌|升级只提高格挡，不将洞见升级。
Flurry of Blows|疾风连击|对单个敌人造成[[4/6]]点伤害；每次切换姿态时，此牌从弃牌堆回到手牌。|伤害4→6|循环输出|回收只作用于弃牌堆中的此牌；留意手牌上限。
Flying Sleeves|流云飞袖|保留。对单个敌人造成[[4/6]]点伤害，重复2次。|每击伤害4→6|保留／多段输出|总基础伤害8→12；力量按两次攻击结算。
Follow-Up|追击|对单个敌人造成[[7/11]]点伤害；若上一张打出的牌是攻击，获得1点能量。|伤害7→11|输出／能量返还|满足条件时才返能；仍需要先付出本牌费用。
Halt|停顿|获得[[3/4]]点格挡；处于愤怒时，再获得[[9/14]]点格挡。|基础格挡3→4；额外9→14|姿态条件防御|愤怒下无修正总格挡12→18；额外部分单独结算。
Just Lucky|幸运一击|占卜[[1/2]]；获得[[2/3]]点格挡；对单个敌人造成[[3/4]]点伤害。|占卜1→2；格挡2→3；伤害3→4|低费筛牌／攻防|占卜不等于抽牌；本牌自身不补充手牌。
Pressure Points|点穴|对单个敌人施加[[8/11]]层印记；所有敌人失去等于各自印记层数的生命。|印记8→11|叠层／全场兑现|生命流失不是攻击伤害；不吃愤怒、神格、力量或易伤加成。
Prostrate|五体投地|获得[[2/3]]层真言；获得4点格挡。|真言2→3|阈值资源／防御|升级不提高格挡；真言阈值需要跨牌计算。
Protect|护身|保留。获得[[12/16]]点格挡。|格挡12→16|可储存防御|用于把防御留给威胁较高的回合。
Sash Whip|腰带抽打|对单个敌人造成[[8/10]]点伤害；若上一张打出的牌是攻击，施加[[1/2]]层虚弱。|伤害8→10；虚弱1→2|输出／减益|按上一张牌类型触发，不能跳过中间的技能牌。
Third Eye|天眼|获得[[7/9]]点格挡；占卜[[3/5]]。|格挡7→9；占卜3→5|防御／筛牌|不直接抽牌；可为后续抽牌或下一回合准备。
Tranquility|安宁|保留。进入平静。消耗。|费用1→0|可保留姿态入口|可作为愤怒出口，但消耗后不能持续参与循环。
Battle Hymn|战歌|[[/固有。]]每回合开始时，将1张惩恶加入手牌。|新增固有|持续生成输出|不是打出时立刻生成；每回合生成可能挤占手牌。
Carve Reality|改造现实|对单个敌人造成[[6/10]]点伤害；将1张惩恶加入手牌。|伤害6→10|输出／生成保留攻击|升级不提高惩恶等级；惩恶需要另付1费。
Collect|收集|从下回合开始，连续[[X/X+1]]个回合在回合开始时获得1张奇迹+。消耗。|持续X→X+1回合|延迟能量／生成|投入能量决定持续回合数；每回合固定给1张奇迹+。
Conclude|结末|对所有敌人造成[[12/16]]点伤害；结束你的回合。|伤害12→16|高效群攻／回合终结|未击杀时，打出前应完成防御和退出愤怒。
Deceive Reality|欺瞒现实|获得[[4/7]]点格挡；将1张平安加入手牌。|格挡4→7|分段防御／生成|升级不提高平安等级；第一段即时，第二段可保留。
Empty Mind|化智为空|抽[[2/3]]张牌；退出当前姿态。|抽牌2→3|抽牌／姿态出口|实际先抽牌再退出；英文聚合页顺序简写与此不同。
Fasting|斋戒|获得[[3/4]]点力量和[[3/4]]点敏捷；以后每回合开始时少获得1点能量。|力量与敏捷各3→4|攻防成长／资源代价|能量惩罚从后续回合生效；需低费牌或补能支持。
Fear No Evil|不惧妖邪|对单个敌人造成[[8/11]]点伤害；若其意图包含攻击，进入平静。|伤害8→11|条件姿态入口／输出|敌人没有攻击意图时不能靠它退出愤怒。
Foreign Influence|他山之石|从3张随机的任意颜色攻击牌中选1张加入手牌。[[/它在本回合费用为0。]]消耗。|生成牌本回合变为0费|生成／临场解答|升级改变生成牌的本回合费用，不保证抽到特定攻击。
Foresight|先见之明|每回合开始时，占卜[[3/4]]。|占卜3→4|持续筛牌|每回合启动，不是额外抽牌；占卜不触发洗牌。
Indignation|义愤填膺|若已处于愤怒，对所有敌人施加[[3/5]]层易伤；否则进入愤怒。|易伤3→5|姿态入口／状态内收益|两种分支二选一；入愤怒的同一次使用不会附带易伤。
Inner Peace|内心宁静|若已处于平静，抽[[3/4]]张牌；否则进入平静。|抽牌3→4|姿态入口／状态内抽牌|入平静与抽牌为互斥分支；不能将入平静视为抽牌。
Like Water|如水|你的回合结束时，若处于平静，获得[[5/7]]点格挡。|格挡5→7|姿态条件防御|要求以平静结束回合，与立即退出平静取能形成取舍。
Meditate|冥想|从弃牌堆选[[1/2]]张牌放入手牌并保留；进入平静；结束回合。|回收1→2张|定向回收／保留／姿态入口|赋予该次回合结束的保留，不是永久增加保留关键词。
Mental Fortress|心灵堡垒|每次切换姿态，获得[[4/6]]点格挡。|每次格挡4→6|姿态切换回报|重复进入当前姿态不算切换；可以与输出循环并行产防。
Nirvana|涅槃|每次占卜，获得[[3/4]]点格挡。|每次格挡3→4|筛牌事件回报|按占卜事件次数结算，不按查看或弃掉的牌数。
Perseverance|坚韧|保留。获得[[5/7]]点格挡；每次此牌被保留，其格挡增加[[2/3]]。|基础格挡5→7；每次增长2→3|保留成长防御|成长在保留结算时发生；本战斗内持续。
Pray|祈祷|获得[[3/4]]层真言；将1张洞见洗入抽牌堆。|真言3→4|阈值资源／生成抽牌|升级不提高洞见等级；生成的抽牌有抽到它的延迟。
Reach Heaven|立地升天|对单个敌人造成[[10/15]]点伤害；将1张以暴易暴洗入抽牌堆。|伤害10→15|延迟爆发／生成|以暴易暴不直接到手；升级母牌不会升级子牌。
Rushdown|猛虎下山|每次进入愤怒，抽2张牌。|费用1→0|姿态抽牌引擎|已在愤怒时再次尝试进入愤怒，不触发入场抽牌。
Sanctity|圣洁|获得[[6/9]]点格挡；若上一张打出的牌是技能，抽2张牌。|格挡6→9|条件抽牌／防御|抽牌量不随升级增加；需要前置技能牌。
Sands of Time|时之沙|保留。对单个敌人造成[[20/26]]点伤害；每次此牌被保留，费用降低1。|伤害20→26|保留降费输出|初始费用仍为4；保留后才逐步降费。
Signature Move|招牌技|仅当它是手牌中唯一的攻击牌时可打出；对单个敌人造成[[30/40]]点伤害。|伤害30→40|手牌条件爆发|保留攻击或持续造攻击牌可能妨碍满足条件。
Simmering Fury|怒火中烧|下回合开始时，进入愤怒并额外抽[[2/3]]张牌。|额外抽牌2→3|延迟姿态入口／抽牌|提前承诺下回合进入愤怒，需要准备出口。
Study|研习|每回合结束时，将1张洞见洗入抽牌堆。|费用2→1|持续生成抽牌|回合结束生成，仍需先抽到洞见；可能稀释小牌组循环。
Swivel|旋身|获得[[8/11]]点格挡；你下一张打出的攻击牌费用为0。|格挡8→11|防御／攻击费用转换|只替代下一张攻击的费用，不能让整个回合攻击免费。
Talk to the Hand|以手拒之|对单个敌人造成[[5/7]]点伤害；此后每次攻击该敌人，获得[[2/3]]点格挡。消耗。|伤害5→7；每次格挡2→3|攻击事件回报|敌方减益可被人工制品阻挡；多段攻击按每段触发。
Tantrum|发泄|对单个敌人造成3点伤害，重复[[3/4]]次；进入愤怒；将此牌洗入抽牌堆。|次数3→4|多段输出／姿态入口|先攻击后进愤怒；返回抽牌堆，不是回手或弃牌。
Wallop|当头棒喝|对单个敌人造成[[9/12]]点伤害；获得等于未被格挡的伤害数值的格挡。|伤害9→12|攻击转防御|只按穿过敌人格挡的伤害计算，不能直接按牌面伤害算。
Wave of the Hand|摆手|本回合每次获得格挡，向所有敌人施加[[1/2]]层虚弱。|每次虚弱1→2|防御事件回报|按获得格挡的次数触发，不按格挡量触发。
Weave|迂回|对单个敌人造成[[4/6]]点伤害；每次占卜，此牌从弃牌堆回到手牌。|伤害4→6|筛牌回收／输出|空抽牌堆占卜不会回收迂回；占卜不会自行洗牌。
Wheel Kick|回旋踢|对单个敌人造成[[15/20]]点伤害；抽2张牌。|伤害15→20|输出／抽牌|2费带来即时伤害与手牌补充。
Windmill Strike|旋转打击|保留。对单个敌人造成[[7/10]]点伤害；每次此牌被保留，其伤害增加[[4/5]]。|基础伤害7→10；每次增长4→5|保留成长输出|保留次数累积成长，不是按经过任意回合数成长。
Worship|敬拜|[[/保留。]]获得5层真言。|新增保留|阈值资源|升级不增加真言；改善神格触发的可控性。
Wreath of Flame|火焰纹|下一张攻击牌每段伤害增加[[5/8]]点。|伤害加成5→8|多段攻击放大|加成用于下一张攻击，而不是只给第一段；提前打小攻击会消耗它。
Alpha|阿尔法|[[/固有。]]将1张贝塔洗入抽牌堆。消耗。|新增固有|多阶段启动|阿尔法升级不自动升级贝塔或欧米伽。
Blasphemy|渎神|[[/保留。]]进入神格；下回合死亡。消耗。|新增保留|高风险爆发入口|必须把死亡代价纳入计划；与普通真言入神格的代价不同。
Brilliance|光辉|对单个敌人造成[[12/16]]点伤害，额外加上本场战斗累计获得的真言层数。|基础伤害12→16|累计资源回报|读取累计获得量，已消耗的真言仍计入。
Conjure Blade|聚能成刃|将1张攻击次数为[[X/X+1]]的灭除之刃洗入抽牌堆。消耗。|子牌攻击次数X→X+1|能量储存／生成输出|X由施放母牌的能量投入决定；灭除之刃本身费用为1。
Deus Ex Machina|机械降神|不能被打出。抽到时，将[[2/3]]张奇迹加入手牌，然后消耗此牌。|奇迹数量2→3|抽取触发／生成能量|必须发生抽牌触发；不是打出效果，奇迹默认未升级。
Deva Form|天人形态|[[虚无。/]]每回合开始时获得额外能量，首次为1，以后每回合再增加1。|移除虚无|持续能量成长|支付3费后从后续回合回报；升级不降低费用。
Devotion|虔信|每回合开始时获得[[2/3]]层真言。|真言2→3|持续阈值资源|打出当下不立即给真言；需要回合推进。
Establishment|确立基础|[[/固有。]]每当一张牌被保留，该牌费用在本场战斗中降低1。|新增固有|保留回报／降费|普通费用最低为0；保留事件才触发，单纯停在手中不等于结算保留。
Judgment|审判|若目标当前生命不高于[[30/40]]，将其生命设为0。|斩杀阈值30→40|阈值斩杀|不是造成30或40伤害；高于阈值时没有该效果。
Lesson Learned|勤学精进|对单个敌人造成[[10/13]]点伤害；若斩杀，永久升级牌组中随机1张牌。消耗。|伤害10→13|输出／局外成长|必须由此牌满足斩杀条件；召唤物等不提供正常斩杀收益。
Master Reality|操控现实|战斗中新生成的卡牌获得升级。|费用1→0|生成牌回报|影响能力生效之后生成的牌，不追溯升级此前生成的牌。
Omniscience|通晓万物|从抽牌堆选1张牌，免费打出2次，再消耗该牌。消耗。|费用4→3|定向检索／复制结算|目标须在抽牌堆；重复结算会重复目标牌的副作用。
Ragnarok|诸神之黄昏|随机选择敌人造成[[5/6]]点伤害，重复[[5/6]]次。|每击5→6；次数5→6|多段爆发|总基础伤害25→36；多敌人时可能分散。
Scrawl|潦草急就|抽牌直到手牌达到上限。消耗。|费用1→0|爆发抽牌|通常手牌上限为10；实际抽牌数取决于剩余手牌。
Spirit Shield|精神护盾|手牌中每有1张牌，就获得[[3/4]]点格挡。|每张格挡3→4|手牌数量转防御|结算时不把已打出的精神护盾本身算作剩余手牌。
Vault|腾跃|结束当前回合，并在敌人行动前额外进行1个自己的回合。消耗。|费用3→2|回合控制／重新抽牌|会推进自己的回合开始与结束效果；不等于把手牌免费再打一遍。
Wish|许愿|三选一：获得[[6/8]]层多层护甲、[[3/4]]点力量，或[[25/30]]金币。消耗。|护甲6→8；力量3→4；金币25→30|成长／防御／经济选择|三个选项只选一个；金币属于路线经济收益。
'''.strip().splitlines()
def expand(t,side):
 return re.sub(r'\[\[([^/\]]*)/([^\]]*)\]\]',lambda m:m[side+1],t)
cards=[]
for line in rows:
 en,zh,effect,delta,role,note=line.split('|')
 s=source[en];rawtext=s['source_text']
 typ=re.search(r'Type: (\w+)',rawtext)[1]
 rare=rawtext.split()[0]
 cost=re.search(r'Cost: (.*?) Deck:',rawtext)[1]
 cm=re.fullmatch(r'(\d)(?:\((\d)\))?',cost)
 base_cost=int(cm[1]) if cm else 'X' if cost=='X' else '不可打出'
 up_cost=int(cm[2] or cm[1]) if cm else base_cost
 base,up=expand(effect,0),expand(effect,1)
 keywords=[k for k in ['保留','固有','虚无','消耗','占卜','真言','愤怒','平静','神格','易伤','虚弱','印记'] if k in base]
 cards.append(dict(en=en,name=zh,type={'Attack':'攻击','Skill':'技能','Power':'能力'}[typ],rarity={'Starter':'初始','Common':'普通','Uncommon':'罕见','Rare':'稀有'}[rare],cost=base_cost,up_cost=up_cost,base=base,upgraded=up,delta=delta,keywords='、'.join(keywords) or '—',role=role,note=note,source=s['url']))
by={r['en']:r for r in cards}
def names(ids): return '、'.join(by[x]['name'] for x in ids)
packages=[]
def pack(code,name,core,support,loop,requires,weakness,transfer):
 c=core.split(';');s=support.split(';') if support else []
 assert len(c+s)==len(set(c+s)),name
 for x in c+s: assert x in by,x
 packages.append(dict(code=code,name=name,core=c,support=s,loop=loop,requires=requires,weakness=weakness,transfer=transfer))
pack('01','姿态循环','Rushdown;Eruption;Tantrum;Inner Peace;Fear No Evil;Empty Mind;Mental Fortress;Flurry of Blows','Vigilance;Empty Fist;Empty Body;Tranquility;Meditate;Scrawl;Talk to the Hand','平静→低费入愤怒取能并抽牌→重新入平静或退出；切换同步触发攻防回报。','优先有可靠入口、出口和抽牌；无限还需循环牌可稳定重抽、能量收支不亏，以及启动和防御方案。','不惧妖邪依赖敌人意图；状态牌、手牌上限和出牌次数限制会打断循环。警惕2费不能直接替代1费平静入口。','对照霜月：入口、出口、循环回报各设职责。避免一个核心能力同时包办资源、抽牌、伤害与防御。')
pack('02','愤怒爆发','Eruption;Tantrum;Crescendo;Indignation;Simmering Fury;Wallop;Ragnarok','Bowling Bash;Consecrate;Crush Joints;Sash Whip;Follow-Up;Flying Sleeves;Conclude;Wheel Kick;Wreath of Flame;Signature Move;Empty Fist;Tranquility;Halt;Swivel;Blasphemy','先准备易伤或多段增伤，再入愤怒集中打出攻击；用出口、防御或击杀处理反击。','手牌伤害与能量须匹配；先确认攻击和切姿态的先后顺序。','未能击杀且留在愤怒会承受双倍攻击伤害；招牌技与手中其他攻击冲突；结末提前结束回合。','对照霜月：强窗口要有明确承诺与退出方式；状态内奖励可改变牌的用途，而不只是全局翻倍。')
pack('03','占卜回收','Cut Through Fate;Third Eye;Just Lucky;Foresight;Weave;Nirvana','Talk to the Hand;Scrawl;Fasting','占卜筛掉暂时不用的牌→回收迂回→低费攻击；涅槃把筛牌转成防御。','先保证抽牌和基本伤害；占卜次数与抽牌量是不同资源。','仅占卜不能直接增加手牌；空抽牌堆不会因占卜洗牌，也不能回收迂回。','对照霜月：让一个控制牌序的事件连接输出和防御；分别统计事件次数与处理牌数。')
pack('04','保留蓄力','Establishment;Meditate;Sands of Time;Windmill Strike;Perseverance;Protect','Flying Sleeves;Crescendo;Tranquility;Worship;Spirit Shield;Battle Hymn;Deceive Reality;Reach Heaven','保留关键牌跨回合等待→降费或成长→在愤怒／神格窗口集中兑现。','需要能撑过等待期的防御，控制手牌数量；冥想可将非保留牌临时保留。','等待会损失当前节奏；囤牌占用10张手牌上限；招牌技可能被保留攻击卡住。','对照霜月：可把爆发准备存于卡牌本身；明确保留一次、永久关键词与战斗内成长的区别。')
pack('05','真言神格','Prostrate;Pray;Worship;Devotion;Brilliance;Blasphemy','Sands of Time;Windmill Strike;Ragnarok;Meditate;Scrawl','积累10真言进入神格，获得能量并放大攻击；光辉读取整场累计真言。渎神提供带代价的捷径。','阈值触发时须留有攻击和手牌；控制真言获得时点，避免空过倍率窗口。','渎神本身不产真言；提前进入神格却无牌可打会浪费资源；专注攒层会牺牲生存。','对照霜月：真言是持有层数，光辉读累计获得量；两种计数分开，适合检查霜蚀与月痕的阈值设计。')
pack('06','生成升级','Master Reality;Battle Hymn;Carve Reality;Deceive Reality;Reach Heaven;Evaluate;Pray;Study','Foreign Influence;Collect;Deus Ex Machina;Conjure Blade;Establishment','先布置操控现实→生成升级后的攻击、防御或抽牌子牌→按需要保留和兑现。','母牌、生成目的地和子牌付费分开考虑；确保有手牌空间与后续能量。','母牌升级通常不升级子牌；往抽牌堆生成比直接到手更慢，也会改变抽牌分布。','对照霜月：生成牌可把一次性收益分拆成现在与未来两步；明确子牌是否触发出牌、攻击和资源回报。')
pack('07','能量与属性成长','Deva Form;Fasting;Collect;Deus Ex Machina;Conjure Blade;Wish','Ragnarok;Wreath of Flame;Scrawl;Wheel Kick;Swivel;Omniscience','先投入成长能力或延迟能量→用抽牌消化多余能量→多段攻击放大力量收益。','有启动回合的防御；能量、抽牌、可用攻击三者需要同步。','天人形态前置3费且回报延迟；斋戒每回合减能量；只堆能量没有手牌会空转。','对照霜月：每个资源引擎都应有消耗口；观察“资源过剩但无事可做”是否频繁发生。')
pack('08','格挡与减益回报','Talk to the Hand;Mental Fortress;Nirvana;Wave of the Hand;Wallop;Like Water','Halt;Spirit Shield;Perseverance;Deceive Reality;Sanctity;Sash Whip','通过攻击、姿态切换、占卜等原有动作获得格挡，再用摆手把多次格挡转换成全场虚弱。','它通常是其他输出包的防御补件，需要对应的触发动作和稳定伤害。','以手拒之是敌方减益，会被人工制品阻挡；无触发器时回报能力可能成为空牌。','对照霜月：适合观察多段月蚀与潮汐联动；区分每张牌、每段攻击、每次伤害和每次格挡事件。')
pack('09','点穴叠层','Pressure Points','Meditate;Inner Peace;Empty Mind;Sanctity;Third Eye;Like Water','反复点穴积累印记；每次使用同时兑现所有敌人各自已有的印记。','需要反复抽到或回收点穴，并用独立防御撑住前期；有多个副本只是提高出现频率。','与力量、易伤、愤怒／神格攻击倍率缺少直接协同；人工制品会挡住印记施加。','对照霜月：最接近月痕的参考。但印记每次触发不清空；月痕阈值清空会形成不同的节奏与目标选择。')
pack('10','阿尔法与全知','Alpha;Omniscience','Master Reality;Scrawl;Vault;Meditate;Third Eye;Protect;Like Water','阿尔法→抽到并使用贝塔→抽到并使用欧米伽，建立回合末群伤；全知可加速或重复关键牌结算。','无减费的三阶段合计需1+2+3费，另需两次找到生成牌；需要筛牌、抽牌和防御。','阶段准备慢；欧米伽不是攻击，不吃姿态伤害倍率。全知目标必须留在抽牌堆。','对照霜月：若加入多阶段大招，应同时定义阶段目的地、抽取延迟和前置资源，不只计算最终伤害。')
pack('11','通用支撑与过渡','Strike;Defend;Judgment;Lesson Learned;Scrawl;Vault;Sanctity;Foreign Influence;Wish','Cut Through Fate;Third Eye;Wheel Kick;Sash Whip;Empty Body','先解决当前战斗的伤害、防御和抽牌缺口，再由检索、回合控制或永久升级提高长期质量。','按当前牌组短板补件；这不是独立胜利条件，也不要求整包收齐。','过量加入功能牌会稀释核心循环；勤学精进需要留出斩杀机会，许愿有较高当回合成本。','对照霜月：纯工具牌也应解决具体短板；把立即战斗价值与整局成长价值分开。')
for c in cards:
 c['packages']=[p['name'] for p in packages if c['en'] in p['core']+p['support']]
 assert c['packages'],c['en']
 c['synergy']='；'.join(p['name']+'：'+('核心' if c['en'] in p['core'] else '补件') for p in packages if c['en'] in p['core']+p['support'])
cards.sort(key=lambda c:({'初始':0,'普通':1,'罕见':2,'稀有':3}[c['rarity']],c['en']))
generated_rows='''
Miracle|奇迹|保留。获得[[1/2]]点能量。消耗。|净水／圣水；机械降神；收集|收集直接生成奇迹+；机械降神默认生成普通奇迹。
Insight|洞见|保留。抽[[2/3]]张牌。消耗。|评估；祈祷；研习|这三张母牌默认把洞见洗入抽牌堆，而不是直接加入手牌。
Smite|惩恶|保留。对单个敌人造成[[12/16]]点伤害。消耗。|改造现实；战歌|直接加入手牌；仍需支付1能量打出。
Safety|平安|保留。获得[[12/16]]点格挡。消耗。|欺瞒现实|母牌和子牌各支付1费，可分在不同回合使用。
Through Violence|以暴易暴|保留。对单个敌人造成[[20/30]]点伤害。消耗。|立地升天|0费的延迟攻击；先洗入抽牌堆，抽到后可保留。
Expunger|灭除之刃|对单个敌人造成[[9/15]]点伤害，重复N次。|聚能成刃|N是生成时记录的X或X+1；此牌打出费用为1，且本身不消耗。
Beta|贝塔|将1张欧米伽洗入抽牌堆。消耗。|阿尔法|升级只将自身费用2→1，不自动生成欧米伽+。
Omega|欧米伽|每回合结束时，对所有敌人造成[[50/60]]点伤害。|贝塔|能力伤害，不是攻击伤害；无愤怒／神格倍率。
'''.strip().splitlines()
generated=[]
for row in generated_rows:
 en,zh,effect,origin,note=row.split('|');s=source[en];t=s['source_text']
 cost=re.search(r'Cost: (.*?) Deck:',t)[1];m=re.fullmatch(r'(\d)(?:\((\d)\))?',cost)
 generated.append(dict(en=en,name=zh,type={'Attack':'攻击','Skill':'技能','Power':'能力'}[re.search(r'Type: (\w+)',t)[1]],rarity='特殊／无色',cost=int(m[1]),up_cost=int(m[2] or m[1]),base=expand(effect,0),upgraded=expand(effect,1),origin=origin,note=note,source=s['url']))
assert len(cards)==75 and len(set(x['en'] for x in cards))==75
assert {k:sum(c['rarity']==k for c in cards) for k in ['初始','普通','罕见','稀有']}=={'初始':4,'普通':19,'罕见':35,'稀有':17}
assert set(by)=={x['name'] for x in raw if '/watcher/' in x['url']}
result={'scope':'Slay the Spire 1 PC v2.3 标准观者卡池；不含 Mod 和旧测试版卡牌。效果为中文语义整理，非逐字转录。','checked':'2026-10-03','cards':cards,'packages':packages,'generated':generated}
out=root/'data/watcher_reference.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'cards':len(cards),'packages':len(packages),'generated':len(generated),'type_counts':{t:sum(c['type']==t for c in cards) for t in ['攻击','技能','能力']},'coverage':len({x for p in packages for x in p['core']+p['support']})},ensure_ascii=False))
