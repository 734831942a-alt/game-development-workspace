"""Executable specification checks only; not a game engine or balance simulation."""
from dataclasses import dataclass
from math import floor,ceil
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]/'v02'
d=json.loads((root/'design.json').read_text());p={r[0]:r[2] for r in d['parameters']}
checks=[]
def check(name,condition):
 assert condition,name
 checks.append({'case':name,'result':'通过'})
@dataclass
class State:
 hp:int=72
 maximum:int=72
 frost:int=0
 recoverable:int=0
 form:str='冰'
 turn:int=1
 armed:bool=True
 blocked_through:int=-1
 ember_turn:int|None=None
 moon_uses:int=0
 @property
 def low(self):return floor(self.maximum*p['blood_low'])
 @property
 def high(self):return ceil(self.maximum*p['blood_high'])
 def rearm(self):
  if self.hp>0 and self.form!='血月' and self.hp>=self.high:self.armed=True
 def pay(self,n):
  if n<0 or self.hp<=n:raise ValueError('生命不足以非致命全额支付')
  self.hp-=n;self.recoverable+=n
 def enemy_loss(self,n):self.hp=max(0,self.hp-n)
 def heal(self,n):
  actual=min(n,self.maximum-self.hp) if self.hp>0 else 0
  self.hp+=actual;self.recoverable=max(0,self.recoverable-actual);self.rearm();return actual
 def recover(self,n):return self.heal(min(n,self.recoverable))
 def safe_check(self,own_turn=True):
  self.rearm()
  if own_turn and self.hp>0 and self.form!='血月' and self.armed and self.turn>self.blocked_through and self.hp<=self.low:
   self.form='血月';self.armed=False;self.blocked_through=self.turn+p['blood_recovery'];return True
  return False
 def leave_blood(self,to='冰'):
  if self.form!='血月':return
  self.form=to;self.ember_turn=self.turn+1;self.rearm()
 def moon_start(self,mandatory_pay=0):
  if self.hp<=mandatory_pay:raise ValueError('牌面支付不足')
  if self.form!='月' or self.moon_uses>=p['moon_attack_limit'] or self.hp<=mandatory_pay+p['moon_hp']:return 0
  self.pay(p['moon_hp']);self.moon_uses+=1;bonus=p['moon_mark']
  if self.frost>0:self.frost-=1;bonus+=p['moon_frost_bonus']
  return bonus

def eclipse_apply(mark,addition,hp,block=0,blood=False):
 mark+=addition;hits=events=damage=0
 while mark>=p['mark_threshold'] and hp>0:
  mark-=p['mark_threshold'];events+=1
  for _ in range(p['eclipse_hits']):
   if hp<=0:break
   hit=p['eclipse_damage']*(p['blood_mult'] if blood else 1)
   absorbed=min(block,hit);block-=absorbed
   real=min(hp,hit-absorbed);hp-=real;damage+=real;hits+=1
 if hp<=0:mark=0
 return dict(mark=mark,hp=hp,block=block,hits=hits,events=events,damage=damage)

s=State();check('72最大生命的低线28 高线40',(s.low,s.high)==(28,40))
s=State(maximum=73,hp=73);check('非整百分比向下与向上取整',(s.low,s.high)==(29,41))
s=State(hp=31,frost=3,recoverable=7,form='月',turn=3)
bonus=s.moon_start(2);s.pay(2)
check('支付发生时不在牌中途切血月',(s.hp,s.form,s.frost,bonus)==(28,'月',2,2))
check('牌末检查低线才进入血月',s.safe_check() and s.form=='血月')
check('血月暂停月的额外烧血',s.moon_start()==0 and s.hp==28)
e=eclipse_apply(6,2,100,blood=True)
check('血月月蚀为4击每击8 共32',e['hits']==4 and e['damage']==32)
s.recover(6);check('血月中回血不提前退出',(s.hp,s.recoverable,s.form)==(34,4,'血月'))
s.leave_blood();check('退出默认冰并预约下回合衍生牌',(s.form,s.ember_turn,s.blocked_through)==('冰',4,4))
s.turn=4;s.recover(3);s.heal(4)
check('恢复到41后可蓄势且冲销全部额度',s.hp==41 and s.armed and s.recoverable==0)
s.pay(13);check('恢复回合即使再次低血也不触发',not s.safe_check() and s.form=='冰')
s.turn=5;check('时间间隔结束且已蓄势可再次触发',s.safe_check())
s=State(hp=20);s.safe_check();s.leave_blood();s.turn=3
check('一直低血不能逐回合重复进入',not s.safe_check() and not s.armed)
s=State(hp=31);s.enemy_loss(11)
check('敌人回合跨线不立即开启',not s.safe_check(False) and s.form=='冰')
s.turn+=1;check('下个自身回合可以获得完整窗口',s.safe_check())
s=State(hp=31);s.pay(4);s.recover(4)
check('一张牌内先跨线再恢复不入场',not s.safe_check() and s.hp==31)
s=State(hp=72);s.pay(3);s.enemy_loss(5);n=s.recover(6)
check('回生不能超过主动自损额度',(n,s.hp,s.recoverable)==(3,67,0))
s=State(hp=72);s.pay(3);s.enemy_loss(5);s.heal(4)
check('真正治疗先抵消已有可回收额度',s.hp==68 and s.recoverable==0 and s.recover(8)==0)
s=State(hp=2);before=(s.hp,s.recoverable)
try:s.pay(2);raise AssertionError('应当拒绝致命支付')
except ValueError:pass
check('不足支付没有部分扣款',(s.hp,s.recoverable)==before)
s=State(hp=3,form='月',frost=2);b=s.moon_start(2);s.pay(2)
check('只够牌面支付时跳过整个月被动',(b,s.hp,s.frost,s.moon_uses)==(0,1,2,0))
s=State(hp=0,recoverable=8)
check('血月与回生都不复活玩家',not s.safe_check() and s.recover(8)==0)
s=State(hp=72,form='月',frost=5)
for _ in range(2):s.moon_start()
s.form='冰';s.form='月'
check('切形态不刷新月攻击次数',s.moon_start()==0 and s.moon_uses==2)
e=eclipse_apply(0,17,100)
check('17月痕扣16 保留1并引爆两次',(e['events'],e['mark'],e['damage'])==(2,1,32))
e=eclipse_apply(0,8,5)
check('5生命目标只结算两击 取消剩余击数',(e['hits'],e['damage'],e['hp'])==(2,5,0))
e=eclipse_apply(0,8,100,16)
check('四击全被挡仍有四次已结算事件',(e['hits'],e['damage'],e['block'])==(4,0,0))
check('标准月蚀与碎月变体算术',4*4==16 and (4-1)*(4+2)==18 and 4*(4+2)==24)
ids={c['id'] for c in d['cards']}
check('64个唯一卡牌和所有升级均有效',len(ids)==64 and all(c['base']!=c['upgraded'] or c['cost']!=c['up_cost'] for c in d['cards']))
check('四套样例都是20张且引用真实ID',all(sum(r['count'] for r in x['entries'])==20 and all(r['id'] in ids for r in x['entries']) for x in d['decks']))
check('初始牌组10张且包含两个入口',sum(r['count'] for r in d['starter']['cards'])==10 and {'B03','B04'}.issubset(r['id'] for r in d['starter']['cards']))
out={'scope':'规格模型与清单检查，不是宿主游戏测试或胜率模拟','count':len(checks),'checks':checks}
(root/'audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':len(checks),'scope':out['scope']},ensure_ascii=False))
