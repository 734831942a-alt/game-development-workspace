"""Reviewed gameplay summaries. Taxonomy is analyst interpretation, not upstream metadata."""
import json, re, csv, shutil
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# id | base (without common keywords) | upgrade changes | archetypes | roles | upgrade class | bridge rationale or review note
# S switch; V strength/vigor/multi-hit; D dexterity/block conversion; P concert; T thinning; G generation/co-op; U general
# g Generator; c Consumer; p Payoff; e Enabler; b Bridge; a Build-around; u Utility
DATA = '''Acting|抽2；获得1层转换人格；立即切换形态。|抽2→3；额外获得本回合2力量、2敏捷。|S|geu|混合|升级后同时支援力量与敏捷，基础版不计桥梁。
Addiction|每次实际切换形态，获得4格挡。|增加固有。|S,D|pab|功能|切换次数转化为防御，可接格挡转活力。
Alone|睦：8格挡，每3敏捷获得1力量；墨：10伤害，每3力量获得1敏捷。|格挡8→12；伤害10→15。|D,V|gpb|数值|敏捷与力量互相转化；正数层数按整数除法。
BackPersona|进入小墨；下次回合开始时保留格挡。|额外获得7格挡。|S,D|eb|功能|形态调度连接格挡存储。
Backstage|非演奏会：1演艺热情；演奏会：12格挡。|格挡12→16。|P|gpu|数值|演奏牌均有虚无、消耗；离开窗口仍能产资源。
BeatMirror|睦：3活力，目标1易伤；墨：5伤害，目标1虚弱。|易伤1→2；伤害5→8。|V|geu|数值|铺垫与伤害同卡，不因双形态自动记为跨流派桥梁。
BecomeMain|本回合禁止切换。睦：获得3能量；墨：随机敌人15伤害，15格挡。|移除消耗。|U|eu|功能|支付1后睦净得2能量；升级允许战斗内重复循环。
BrainBully|睦：2回合内，目标易伤生效时，伤害倍率额外+0.5；墨：10伤害，2回合内目标虚弱生效时，输出倍率额外-0.25。|两种额外效果持续2→4回合。|V|peu|数值|效果本身不施加易伤或虚弱；在原倍率上加减，非再次乘1.5或0.75。
BullyingYou|另一玩家获得2能量、抽1，受到3不可格挡且不受增减伤修正的伤害，并获得2易伤。|能量2→3；抽1→2。|G|gu|数值|仅多人；这里的自损走伤害事件，不能视为无事件HP扣除。
CantPlayAtAll|睦：永久4力量、失去1敏捷；墨：永久4敏捷、失去1力量。|力量4→6；敏捷4→5。|V,D|gb|数值|同一能力根据打出形态选择攻击或防御成长。
Catharsis|睦：本回合6力量；墨：7伤害×2。|睦额外4活力；每段伤害7→9。|V|gcp|混合|一条攻击命令的多段攻击；新增活力属于资源维度变化。
ChaseCat|睦：抽2；墨：3伤害×3，每段独立随机目标。|抽2→3；每段3→4。|V|cpu|数值|多段兑现力量与活力，抽牌提供低配用途。
Comedian|每实际切换2次形态，为下回合积累1能量。|费用3→2。|S|gpa|费用|每份能力独立计数；能量延迟到账。
Contemplate|睦：9格挡；墨：弃牌堆选1张回手。|格挡9→13；回手的牌获得保留。|U|u|混合|回收不限定某个机制，按纯Utility统计。
Crumble|睦：目标6易伤；墨：对目标造成(3+目标易伤层数)伤害×3。|易伤6→8；攻击次数3→4。|V|gcp|数值|将易伤层数再次作为基础伤害系数。
CryInRain|按打出前本战斗切换次数，每次获得本回合1力量。睦：目标1易伤并进入墨；墨：5伤害。|每次切换对应临时力量1→2。|S,V|gpb|数值|切换历史变成攻击成长；本牌随后造成的切换不计入本次快照。
CutLine|回合结束前，每1层若叶睦临时力量获得2活力。|每层2→3活力；增加固有。|V|gpa|混合|在临时力量清理前结算，将当回合投资带入后续回合。
DeathLake|以小墨开始回合时获得2永久力量。|移除虚无。|V|ga|功能|要求回合起始形态，不是打出时形态。
DevourSelf|睦：获得当前敏捷×2活力，进入墨；墨：造成当前敏捷×3伤害，进入睦。|活力倍率2→3；伤害倍率3→4。|S,D,V|gcpb|数值|敏捷投资可转换成攻击回报，并推进切换。
Disharmony|每次结算对全体造成0基础伤害×2；设置BaseReplayCount=2。|每次结算追加1次0基础格挡。|V|cp|功能|由古老牙齿把睦头人出击转换得到；总重放行为需游戏运行验证，勿只读本地化。
Disintegration|每次实际切换，随机给本战斗1张尚无虚无的牌添加虚无。|费用1→0。|S,T|eab|费用|切换推进牌堆压缩；虚无不等于立即消耗，也可能移除关键牌。
Distort|睦：本回合失去2敏捷，获得1能量，进入墨；墨：随机敌人5伤害。|敏捷损失2→1；伤害5→6。|S|geu|数值|以暂时防御代价换切换和能量。
DollHeart|此后每打出1张能力牌，获得1力量。|增加固有。|V|ga|功能|安装能力的这张牌自身不触发新加的能力，Power显式跳过一次。
DollWaltz|X费；随机0基础伤害×floor(1.5X)，获得0基础格挡X次。|攻击次数floor(1.5X)→2X。|V,D|cpab|数值|通过多段伤害和多次格挡同时放大力量与敏捷。
Emptiness|获得本回合(3+此牌本局累计打出次数)敏捷；打出后永久增加获得量1。|费用2→1。|D|ga|费用|源码BaseDex=3；注释写4已过时；成长跨战斗保存。
Encore|演奏会回合结束获得1演艺热情；该能力总回补上限2。|回补1→2，上限仍2。|P|gpa|数值|多份安可不能无限提高回补量。
Ensemble|所有其他存活玩家进入睦，各向抽牌堆随机位置加入(1+此牌本战斗先前打出次数)张随机不同演奏牌。|初始生成数1→2。|P,G,S|geb|数值|多人协作连接演奏、生成和切换；单次不同模板，无足够候选则少生成。
Escape|获得本回合3敏捷；进入睦。|敏捷3→5。|S,D|geb|数值|切换行动同时准备防御属性。
FallIntoAbyss|抽2，获得2能量、12活力；本战斗禁止再进入睦。|抽2→3；活力12→20。|V|gea|数值|打出时不会自动进入墨；从睦打出仍需另行转入墨；封锁切换流。
FearlessOfDeath|本战斗下一次死亡时以1生命复活。|复活生命1→20。|U|u|数值|一次性死亡保护；未在游戏中验证时序。
FightForBody|按本回合非起手抽牌数N：睦获得4N格挡并进入墨；墨造成5N伤害并进入睦。|费用2→1。|S,D|pb|费用|额外抽牌历史连接防御兑现和切换；N不含正常回合抽牌。
FrontPersona|进入睦；获得1能量。|额外获得4活力。|S|ge|功能|升级新增攻击铺垫；初始遗物生成，基础版不计Bridge。
FunnyFace|造成7伤害；进入墨。|伤害7→10。|S|eu|数值|已经是墨时不发生实际切换。
GhostScream|睦：每已有4活力再获得2活力；墨：12伤害并施加2虚弱。|费用2→1。|V|gpu|费用|睦增量为floor(活力/4)×2，0活力不会凭空起动。
GreenhouseGirl|睦：8格挡；墨：从弃牌堆选择至多2张消耗。|格挡8→10；最多消耗2→3张。|T|eu|数值|有选择的牌堆压缩，普通格挡提供兜底用途。
GuitarSmash|睦：目标2易伤，本回合4力量；墨：12伤害后抽2。|费用2→1。|V|geu|费用|攻击投资与过牌在同卡两种形态中分工。
Harmony|先抽1。睦：8格挡；墨：8伤害。|格挡8→11；伤害8→9；墨额外再抽1。|U|u|混合|无专属资源依赖，按纯Utility统计。
HeartResonance|所有存活玩家进入睦；各在手牌、抽牌堆、弃牌堆生成1张随机角色牌，第一次打出0费。|费用2→1。|G,S|geb|费用|源码限制仅多人；包含自己；生成排除禁止生成及模式不符的牌。
HideHeart|下回合获得2能量。睦：5格挡；墨：进入睦。|下回合能量2→3；格挡5→7。|S|geu|数值|切换与跨回合能量调度。
HollowActor|X费；获得X层转换人格，下回合开始逐层切换。|层数X→X+1。|S|gep|数值|X=0时升级版仍给1层；单张牌可批量制造切换。
HugThigh|清除另一玩家的力量、敏捷、活力，自己获得对应层数的2倍；给该玩家弃牌堆加入本牌复制品。|复制品改放抽牌堆随机位置，并继承升级。|G,V,D|gpb|功能|仅多人；StealPower包含负层数转移，0层才跳过。
Imitate|睦：12格挡，目标2虚弱；墨：以目标第一项攻击意图的总伤害作为本次基础伤害，无攻击则1。|费用2→1。|U|u|费用|是单次攻击，非逐段复制；意图值与本次攻击增减伤分开计算。
InnerNoise|向手牌生成3张随机0费角色牌。|费用1→0。|G|gu|费用|排除X费、禁止生成和模式不符的牌，不是给任意牌降费。
Kneel|睦：受到的伤害减半1回合；墨：4覆甲，进入睦。|减伤1→2回合；覆甲4→6。|S|eu|数值|减伤Power具体乘区及衰减时机见关联源码。
LittleCucumber|睦：回复7生命并失去2力量；墨：失去至多4生命且最低留1，获得2力量和2能量。|回复7→10；自损上限4→2；能量2→3。|V|gu|数值|自损走Unblockable/Unpowered伤害；当前HP不足不影响后续奖励。
LookAway|移除自身易伤、虚弱、脆弱。|增加保留。|U|u|功能|通用净化，不清理所有负面状态。
Madness|第k次先前使用后费用为1+k、先获得k能量。睦再获2能量并进入墨；墨抽3+k并进入睦；使用后费用及成长计数+1。|睦额外能量2→3；墨基础抽牌3→4。|S|gea|数值|k是本战斗同实例先前打出次数；高费用仍须先付，不能只看净能量。
MaskedPlay|非演奏会：1热情；演奏会睦：抽3；演奏会墨：获得3能量。|抽3→4；能量3→4。|P|gpu|数值|窗口内的过牌或能量续航。
Megaphone|按打出时形态安装能力：睦为每回合多抽1；墨为回合起始随机手牌本回合0费。|费用2→1。|U|u|费用|收益分支在打出时固定，后续切换不会改变已装能力；纯Utility。
MemoryOfBand|获得5演艺热情。|费用3→2。|P|ge|费用|达到阈值安排回合末后的演奏会，不是立即切换窗口。
MirrorDoll|睦：获得2能量、6格挡并进入墨；墨：3伤害×(2+本回合此前睦出牌数)，再进入睦。|格挡6→9；每段3→5。|S,V|gcpab|数值|睦出牌历史变成墨攻击段数，随后返回睦续循环。
MoonForestUniform|以睦开始回合时，获得本回合2敏捷。|临时敏捷2→4。|D|ga|数值|回合开始检查形态。
MortisCard|每次实际切换形态，对所有敌人造成8不受力量等修正的伤害。|费用2→1。|S|pa|费用|Power使用Move与Unpowered，非一次攻击牌打出，不能当成活力多段攻击。
MoveCard|睦：3格挡，弃牌堆选1回手；墨：抽2。|格挡3→5；抽2→3。|U|u|数值|基础循环的通用回收工具。
MuBurn|获得2力量。|力量2→3。|V|g|数值|简洁的长期攻击成长。
MuCourage|睦：4伤害×2；墨：7格挡。|增加保留。|V|cpu|功能|在睦形态也能兑现多段攻击，避免固定睦只铺垫。
MuDefend|睦：6格挡；墨：先3格挡，再获得本回合1敏捷。|睦格挡6→9；墨格挡3→5、敏捷1→2。|D|gu|数值|顺序重要，刚获得的敏捷不加成本牌先前格挡。
MuGrandFinale|非演奏会：1热情；演奏会且打出后手牌为0：全体5伤害×4，否则无伤害。|每段5→8。|P,V|gcpb|数值|演奏窗口和清空手牌共同约束高段数回报。
MuMask|获得1热情；切换形态。|费用1→0。|S,P|geb|费用|同一张牌推进两个独立循环。
MuMonologue|非演奏会：1热情；演奏会：5伤害×2。|次数2→3。|P,V|gcpb|数值|演奏会把资源牌变成多段攻击。
MuOneForAll|所有其他存活玩家进入睦，并各向抽牌堆加入使用者整副永久卡组的复制品，保留升级次数。|费用2→1。|G,S|geb|费用|仅多人；不复制所有SavedProperty，不等于原封不动复制成长状态。
MuStrike|睦：4活力与本回合1力量；墨：7伤害。|活力4→5、临时力量1→2；伤害7→10。|V|gcp|数值|起始牌直接承担铺垫与兑现。
MultipleMonster|获得等于本战斗实际切换总次数的转换人格层数。|移除虚无。|S|gpa|功能|没有额外固定基础层数；0次切换则获得0。
Mutsumi|睦：4格挡×2，进入墨；墨：全体1虚弱，本回合3敏捷，进入睦。|睦额外本回合2力量；墨全体虚弱1→2。|S,D|gepb|混合|多次格挡放大敏捷，同时在两形态间周转。
MutsumiCharge|对目标造成0基础伤害×2。|额外获得0基础格挡×2。|V|cp|功能|升级后接敏捷；0基础值仍可承接属性修正，不是没有效果。
NeverHappyInBand|将消耗堆全部演奏牌移到抽牌堆，再把战斗各牌堆的全部演奏牌变为随机角色牌。|替换牌全部升级。|P,G|eb|功能|把演奏组件转换成生成牌路线，转换只限本战斗。
NoStayingUp|睦：每已有3力量再获得1力量；墨：下一次攻击保留活力。|移除消耗。|V|gepa|功能|升级改变可重复成长与活力保留次数的上限。
NobleHouse|回合开始，每1当前热情获得3格挡。|增加固有。|P,D|pab|功能|热情存量转防御；格挡不受敏捷修正，可接格挡转活力。
Opening|非演奏会：1热情；演奏会睦：本回合7力量；演奏会墨：全体20伤害。|力量7→9；伤害20→25。|P,V|gpb|数值|演奏会先投资力量，再用其他多段演奏牌兑现。
OutOfControl|睦：6活力；墨：12伤害；然后随机进入睦或墨。|活力6→8；伤害12→15。|S,V|gpeb|数值|活力投资/兑现与随机形态推进；随机留在原形态不算切换。
Performance|睦：7格挡、目标1虚弱，进入墨；墨：10伤害，进入睦。|格挡7→10；虚弱1→2；伤害10→14。|S|eu|数值|普通牌承担双向切换和生存。
PerformancePassion|抽2；获得1热情。|抽2→3。|P|gu|数值|资源发生器附带过牌，减少构筑税。
PhantomPersona|移除正层数的若叶睦临时敏捷状态，已得到的敏捷本战斗不再因此失去。|向弃牌堆加入本牌带虚无的升级复制品。|D|epa|功能|清除的是到期扣除标记，不是敏捷本体；负层数标记不会移除。
PlantCucumber|每回合开始按当前形态：睦获得6格挡；墨获得4活力。|格挡6→8；活力4→6。|D,V|gb|数值|一份能力覆盖防御存量与下一次攻击资源；每份能力独立实例。
PlayDoubleMoon|非演奏会：1热情；演奏会：抽4，随后切换形态。|抽4→6。|P,S|geb|数值|演奏窗口内过牌同时触发切换引擎。
PlayHaruhikage|非演奏会：1热情；演奏会睦：1无实体；演奏会墨：全体8伤害×2。|睦额外10格挡；每段8→12。|P,V|gcpb|混合|同一窗口牌提供紧急防御或多段兑现。
PlayKillkiss|非演奏会：1热情；演奏会睦：7覆甲；演奏会墨：24伤害。|覆甲7→9；伤害24→30。|P|gpu|数值|演奏会的防御或单次伤害回报。
Pluck|获得1热情。睦：4活力；墨：8伤害。|活力4→6；伤害8→12。|P,V|gpb|数值|产热情同时推进活力攻击链。
Rebellion|把手牌、抽牌堆、弃牌堆所有带Strike标签的牌变为随机无色牌。|替换牌全部升级。|G|eu|功能|只变本战斗副本，消耗堆不在扫描范围。
Reborn|移除坠入深渊；对所有敌人造成35伤害；获得10格挡。|费用4→3。|S|eu|费用|解除切换锁，但不会自动切到睦；卡牌类型为Skill而执行攻击命令。
Reminisce|睦：全体1虚弱、1易伤，进入墨；墨：全体9伤害，进入睦。|两种减益1→2；伤害9→12。|S,V|gebu|数值|切换同时布置易伤，连接下一轮攻击。
SelfIsolate|睦：5格挡；墨：获得1能量、自身1虚弱、进入睦。|格挡5→8；取消自身虚弱。|S|geu|混合|取消负面效果使出牌顺序更自由。
Sidekick|睦：给至多2张手牌添加虚无；墨：12伤害。|最多选2→3；伤害12→14。|T|eu|数值|主动设置回合结束压缩，不是立刻消耗选中牌。
Silence|睦：抽(1+本回合此前墨出牌数)；墨：5格挡并进入睦。|每张墨牌额外抽牌1→2；格挡5→8。|S|gpu|数值|墨的出牌历史补充睦的手牌，再继续转换。
StairsTumble|睦：5活力、目标1易伤；墨：4伤害×2。|活力5→7；易伤1→2；每段4→7。|V|gcp|数值|普通牌同时提供攻击链的资源和多段出口。
Surveillance|睦：本回合每次获得格挡同时获得等量活力；墨：随机敌人5伤害、本回合3敏捷、进入睦。|睦额外保留格挡至下次回合开始；伤害5→7、敏捷3→4。|D,V,S|epab|混合|明确把格挡变成活力，防御体系可以给攻击供能。
SwitchPersona|获得本回合2力量、2敏捷；切换形态。|费用1→0。|S,V,D|geb|费用|初始牌就连接形态与两种属性。
TearMaskGold|睦：2格挡×4；墨：获得1能量、5活力并进入睦。|每次格挡2→3；能量1→2。|D,V,S|gpb|数值|多次格挡放大敏捷；另一分支补充活力与切换。
ThousandthPersona|每次实际切换，获得本回合2力量和2敏捷。|增加固有。|S,V,D|gpab|功能|先古稀有度，禁止随机生成；本次未找到源码内的直接获得路径。
Tune|获得1热情。睦：8格挡；墨：目标2虚弱。|格挡8→12；虚弱2→3。|P,D|gbu|数值|热情积累自带防御，能支撑名门或格挡转活力。
TwinForms|每回合开始：若睦，随机敌人15伤害后进入墨；若墨，随机敌人2虚弱、2易伤后进入睦。|伤害15→25；两种减益2→4。|S|epa|数值|每份独立触发；单一分支在触发时检查。
WakabaFortune|按打出前本战斗切换总次数，记录每次4金币，于胜利后获得。|额外抽1。|S|pu|功能|收益是打出时快照，不会持续监听后续切换。
WontLastLong|睦：25活力并进入墨，此后每打出1张牌本回合-1力量；墨：3无实体并进入睦，此后每打出1张牌本回合-1敏捷。|两种负面计数均改为每2张触发。|S,V|geab|数值|本牌自身不计入新负面计数；计数器可跨回合延续，扣属性在回合末恢复。'''

ARCH = dict(S='切换引擎', V='力量活力多段', D='敏捷格挡转化', P='演奏会', T='虚无压缩', G='生成协作', U='泛用')
ROLE = dict(g='Generator', c='Consumer', p='Payoff', e='Enabler', b='Bridge', a='Build-around', u='Utility')
KEYWORDS = dict(Retain='保留', Exhaust='消耗', Ethereal='虚无', Perform='演奏')

def main():
    raw = json.loads((ROOT/'data/reference_extracted.json').read_text())
    source = {r['id']:r for r in raw['cards']}
    records=[]
    for line in DATA.splitlines():
        ident, base, upgrade, arch, roles, up_kind, note = line.split('|')
        s=source[ident]
        ctor=re.fullmatch(r'(\d+), CardType\.(\w+), CardRarity\.(\w+), TargetType\.(\w+)(.*)',s['constructor'])
        assert ctor, (ident,s['constructor'])
        cost, typ, rarity, target, _=ctor.groups()
        scope = '普通奖励' if rarity in ('Common','Uncommon','Rare') else {'Basic':'初始','Token':'生成牌','Ancient':'先古特殊'}[rarity]
        keywords=[KEYWORDS[x] for x in s['keywords']]
        text_base = base + ('【'+ '、'.join(keywords)+'】' if keywords else '')
        record=dict(id=ident,name=s['name'],cost='X' if s['x_cost'] else int(cost), type=typ, rarity=rarity,
                    target=target,scope=scope,multiplayer_only=s['multiplayer_only'],
                    base_effect=text_base, upgrade_effect='基础效果同左，应用以下变化：'+upgrade, upgrade_delta=upgrade,
                    keywords='、'.join(keywords) or '无固定关键词',archetypes=[ARCH[x] for x in arch.split(',')],
                    roles=[ROLE[x] for x in roles], upgrade_kind=up_kind, interpretation=note,
                    source_url=s['url']+'#L'+str(s['lines']['constructor']), source_sha256=s['sha256'],
                    analysis_kind='静态源码效果；构筑与设计职责为研究者标注')
        record['pure_utility'] = roles=='u'
        record['reward_singleplayer']=scope=='普通奖励' and not s['multiplayer_only']
        records.append(record)
    assert len(records)==len(source)==93
    assert len({r['id'] for r in records})==93
    # Preserve upstream terms/implementation for audit, including the MIT notice.
    shutil.copyfile('/private/tmp/frostmoon-mzm-reference/LICENSE', ROOT/'data/LICENSE-reference.txt')
    out={k:v for k,v in raw.items() if k!='cards'}
    out['method']='All 93 card classes reviewed against OnPlay, OnUpgrade, constructors, keywords, and relevant powers. Not compiled or runtime-tested.'
    out['cards']=records
    (ROOT/'data/reference_cards.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
    fields=['id','name','cost','type','rarity','scope','multiplayer_only','base_effect','upgrade_effect','keywords','archetypes','roles','upgrade_kind','pure_utility','interpretation','source_url']
    with (ROOT/'data/reference_cards.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in records:
            w.writerow({k:'、'.join(r[k]) if isinstance(r[k],list) else r[k] for k in fields})
    stats={}
    for label, pool in [('all',records),('reward',[r for r in records if r['scope']=='普通奖励']),('solo',[r for r in records if r['reward_singleplayer']])]:
        stats[label]={'count':len(pool),'rarity':dict(Counter(r['rarity'] for r in pool)),
                      'types':dict(Counter(r['type'] for r in pool)),
                      'roles':dict(Counter(v for r in pool for v in r['roles'])),
                      'archetypes':dict(Counter(v for r in pool for v in r['archetypes'])),
                      'upgrades':dict(Counter(r['upgrade_kind'] for r in pool)),
                      'pure_utility':sum(r['pure_utility'] for r in pool),
                      'by_rarity':{rar:{'count':sum(r['rarity']==rar for r in pool),
                        'bridge':sum(r['rarity']==rar and 'Bridge' in r['roles'] for r in pool),
                        'pure_utility':sum(r['rarity']==rar and r['pure_utility'] for r in pool),
                        'roles':dict(Counter(v for r in pool if r['rarity']==rar for v in r['roles']))}
                        for rar in ['Common','Uncommon','Rare']}}
    (ROOT/'data/reference_stats.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2))
    print(json.dumps(stats,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
