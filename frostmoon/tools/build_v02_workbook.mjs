import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const d=JSON.parse(await fs.readFile(path.join(root,'v02/design.json'),'utf8'));
const rules=JSON.parse(await fs.readFile(path.join(root,'v02/rules.json'),'utf8'));
const audit=JSON.parse(await fs.readFile(path.join(root,'v02/audit.json'),'utf8'));
const output=path.resolve(root,'../outputs/01a1009b-46b5-7492-aa6a-c58b009ff7e0/霜月三形态卡池v0.2.xlsx');
const qa=path.resolve(root,'../artifacts/frostmoon-v02-qa');await fs.mkdir(qa,{recursive:true});
const wb=Workbook.create();
const summary=wb.worksheets.add('方案与规则');
const cards=wb.worksheets.add('64张卡牌');
const review=wb.worksheets.add('逐组审阅');
const decks=wb.worksheets.add('样例卡组');
const params=wb.worksheets.add('参数与算术');
const extra=wb.worksheets.add('衍生与来源');
const C={navy:'#29334D',purple:'#65518C',ink:'#253047',muted:'#657087',line:'#D8DDE6',pale:'#F1EDF7',white:'#FFFFFF',alt:'#F5F7FA',ice:'#E8F2F6',blood:'#F6E9ED',input:'#FFF1CC'};
function col(i){let s='';for(i++;i;i=Math.floor((i-1)/26))s=String.fromCharCode(65+(i-1)%26)+s;return s;}
function base(s,r){s.getRange(r).format={font:{name:'Arial',size:11,color:C.ink},wrapText:true,verticalAlignment:'center',rowHeight:25};}
function head(s,r,color=C.navy){s.getRange(r).format={fill:color,font:{name:'Arial',size:11,bold:true,color:C.white},horizontalAlignment:'center',verticalAlignment:'center',rowHeight:32,wrapText:true};}
function note(s,cell,text){s.getRange(cell).values=[[text]];s.getRange(cell).format={font:{name:'Arial',size:11,italic:true,color:C.muted},wrapText:false,rowHeight:25};}
function title(s,text,scope,last='G',width=300){s.showGridLines=false;s.tabColor=C.purple;base(s,`A1:${last}4`);s.getRange('A1:A4').format.columnWidthPx=185;s.getRange(`B1:${last}4`).format.columnWidthPx=width;s.getRange('A1').values=[[text]];s.getRange('A1').format={font:{name:'Arial',size:16,bold:true,color:C.navy},wrapText:false,rowHeight:32};note(s,'A2',scope);s.getRange(`A3:${last}3`).format.borders={bottom:{style:'thin',color:C.line}};}
function wlen(v){return [...String(v??'')].reduce((a,c)=>a+(c.codePointAt(0)>255?2:1),0);}
function height(s,row,values,widths,last,min=26){const lines=Math.max(1,...values.map((v,i)=>String(v??'').split('\n').reduce((a,x)=>a+Math.max(1,Math.ceil(wlen(x)/((widths[i]-24)/7.5))),0)));s.getRange(`A${row}:${last}${row}`).format.rowHeight=Math.max(min,lines*16+12);}
function grid(s,start,headers,rows,widths){const last=col(headers.length-1),end=start+rows.length;base(s,`A${start}:${last}${end}`);s.getRange(`A${start}:${last}${end}`).values=[headers,...rows];widths.forEach((w,i)=>s.getRange(`${col(i)}${start}:${col(i)}${end}`).format.columnWidthPx=w);head(s,`A${start}:${last}${start}`);rows.forEach((r,i)=>{let n=start+1+i;height(s,n,r,widths,last);if(i%2)s.getRange(`A${n}:${last}${n}`).format.fill=C.alt;});return{last,end};}
function matrix(s,start,attrs,items,width=310){const last=col(items.length),end=start+attrs.length-1;const values=attrs.map(([label,key])=>[label,...items.map(x=>Array.isArray(x[key])?x[key].join('、'):x[key]??'')]);base(s,`A${start}:${last}${end}`);s.getRange(`A${start}:${last}${end}`).values=values;s.getRange(`A${start}:A${end}`).format.columnWidthPx=185;s.getRange(`B${start}:${last}${end}`).format.columnWidthPx=width;values.forEach((r,i)=>{let n=start+i;if(i%2)s.getRange(`A${n}:${last}${n}`).format.fill=C.alt;s.getRange(`A${n}`).format={fill:C.pale,font:{name:'Arial',size:11,bold:true,color:C.purple}};height(s,n,r,[185,...items.map(()=>width)],last);});head(s,`A${start}:${last}${start}`);return{last,end};}
const attrs=[['卡牌名','name'],['ID','id'],['稀有度','rarity'],['类型','type'],['费用 · 基础','cost'],['费用 · 升级','up_cost'],['基础效果','base'],['升级后完整效果','upgraded'],['升级改动','delta'],['机制','mechanics'],['设计职责','role'],['适配方向','builds'],['时序／审阅重点','note'],['实现批次','phase'],['审阅状态 · 可改','review'],['审阅意见 · 可填','review_notes'],['修订基础费用 · 可填','revised_cost'],['修订升级费用 · 可填','revised_up_cost'],['修订效果 · 可填','revised_effect']];
const fieldRow=Object.fromEntries(attrs.map(([label,key],i)=>[key,5+i]));
const by=Object.fromEntries(d.cards.map((c,i)=>[c.id,{...c,index:i}]));
title(cards,'霜月 v0.2 · 64 张原创牌','2026-10-06｜全部是待审阅的设计种子｜属性纵排、每张卡占一列｜黄色格用于你的修改','BM',310);
note(cards,'A4','“霜”“月痕”“回生”与血月时序见方案页。原始数值保留；修订栏不自动改写其他页的种子快照。');
const master=matrix(cards,5,attrs,d.cards,310);
cards.getRange(`B9:${master.last}10`).setNumberFormat('0');cards.getRange(`B9:${master.last}10`).format.horizontalAlignment='right';
cards.getRange(`A13:${master.last}13`).format.fill=C.ice;
cards.getRange(`B19:${master.last}23`).format.fill=C.input;
cards.getRange(`B19:${master.last}19`).dataValidation={rule:{type:'list',values:['待审阅','保留','修改','删除']}};
cards.getRange(`B21:${master.last}22`).setNumberFormat('0');
cards.getRange(`A20:${master.last}20`).format.rowHeight=65;cards.getRange(`A23:${master.last}23`).format.rowHeight=90;
cards.freezePanes.freezeRows(5);cards.freezePanes.freezeColumns(1);

title(review,'霜月 v0.2 · 逐组审阅','每组六张以内，纵向阅读全部64张。这里引用主卡池，修改意见请填写“64张卡牌”的黄色行。','G',290);
note(review,'A4','按初始、普通、罕见、稀有顺序排列；此页无重复收录。所有效果遵循同一套三形态规则。');
const rattrs=attrs.slice(0,14);let next=6;const blocks=[];
for(let i=0;i<d.cards.length;i+=6){const selected=d.cards.slice(i,i+6);const start=next+1,last=col(selected.length);base(review,`A${next}:G${next}`);review.getRange(`A${next}:G${next}`).format.fill=C.purple;review.getRange(`A${next}`).values=[[`卡牌 ${i+1}—${Math.min(i+6,64)}  ·  ${selected[0].id} 至 ${selected.at(-1).id}`]];review.getRange(`A${next}`).format={font:{name:'Arial',size:11,bold:true,color:C.white},wrapText:false,rowHeight:28};matrix(review,start,rattrs,selected,290);rattrs.forEach(([label,key],off)=>review.getRange(`B${start+off}:${last}${start+off}`).formulas=[selected.map(c=>`='64张卡牌'!${col(by[c.id].index+1)}${fieldRow[key]}`)]);review.getRange(`B${start+4}:${last}${start+5}`).setNumberFormat('0');review.getRange(`A${start+8}:${last}${start+8}`).format.fill=C.ice;blocks.push({heading:next,start,end:start+rattrs.length-1,ids:selected.map(x=>x.id)});next=start+rattrs.length+2;}
for(const b of blocks)review.getRange(`B${b.start+4}:G${b.start+5}`).format.horizontalAlignment='center';
review.freezePanes.freezeRows(4);review.freezePanes.freezeColumns(1);

title(summary,'霜月 v0.2 · 冰 月 血月','推荐：冰月用卡牌主动切换，血月在低生命时自动触发｜64张角色牌 + 2张衍生牌 + 4套20张样例','D',320);
note(summary,'A4','先审形态、恢复和触发时序，再改单卡。当前不保留旧版自动进入超然的第四状态。');
grid(summary,6,['形态','主要动作','收益与边界'],[
 ['冰','打技能蓄霜，利用月蚀恢复','前2张技能各产1霜；首次月蚀回生2。'],
 ['月','付少量血并花霜加速叠痕','前2张单体攻击各付1生命补1痕；若消耗1霜，再补1痕。'],
 ['血月','兑现已准备的攻击与月蚀','攻击和月蚀×2，只持续本回合；结束回冰，下回合获得余烬覆雪。']], [180,310,700]);
summary.getRange('A7:C7').format.fill=C.ice;summary.getRange('A9:C9').format.fill=C.blood;
grid(summary,12,['规则主题','决定','完整口径'],rules.rules,[180,310,700]);
note(summary,'A33','数值与卡池自检：28项规格和清单检查通过；未接入游戏、未测胜率。完整设计理由与时序例子见配套说明文档。');
grid(summary,35,['稀有度','牌种数','职责'],[['初始',null,'10张初始实体牌由4种牌构成'],['普通',null,'基础供给、转换、攻防和抽牌'],['罕见',null,'构筑支点与有限触发回报'],['稀有',null,'成长、检索、击数变化与爆发'],['合计',null,'不含2张衍生牌；升级版不另计一种']],[180,310,700]);
for(let i=0;i<4;i++)summary.getRange(`B${36+i}`).formulas=[[`=COUNTIF('64张卡牌'!B7:BM7,A${36+i})`]];
summary.getRange('B40').formulas=[['=SUM(B36:B39)']];summary.getRange('B36:B40').setNumberFormat('0');
grid(summary,43,['方案','好处','代价／决定'],rules.alternatives.map(x=>[x[0],x[1],x[2]+' '+x[3]]),[180,310,700]);
summary.freezePanes.freezeRows(6);summary.freezePanes.freezeColumns(1);

title(decks,'霜月 v0.2 · 4 套 20 张样例','人为构造的首轮对照样本；全部不含稀有牌｜按“升级”列使用种子版本｜相同ID有多份时同时升级','H',160);
note(decks,'A4','数量列可修改，合计会更新。卡面审阅修订不自动替换这里的种子版本；4套样例均使用同一套核心规则。');
let dr=6;const deckRanges=[];
for(const dk of d.decks){
 base(decks,`A${dr}:H${dr+2}`);decks.getRange(`A${dr}`).values=[[dk.name]];decks.getRange(`A${dr}`).format={font:{name:'Arial',size:14,bold:true,color:C.navy},wrapText:false,rowHeight:30};note(decks,`A${dr+1}`,dk.purpose);const start=dr+3;
 const records=dk.entries.map(x=>{const c=by[x.id];return[x.id,c.name,x.count,x.upgrade?'是':'否',x.upgrade?c.up_cost:c.cost,c.type,c.role,c.note];});
 const dims=grid(decks,start,['ID','卡名','数量 · 可改','升级','采用费用','类型','职责','使用边界'],records,[80,170,105,75,90,80,210,480]);
 records.forEach((x,i)=>{const n=start+1+i;const c=by[x[0]],cc=col(c.index+1);decks.getRange(`B${n}`).formulas=[[`='64张卡牌'!${cc}5`]];decks.getRange(`E${n}`).formulas=[[`='64张卡牌'!${cc}${x[3]==='是'?10:9}`]];});
 decks.getRange(`C${start+1}:C${dims.end}`).format.fill=C.input;decks.getRange(`C${start+1}:C${dims.end}`).setNumberFormat('0');decks.getRange(`E${start+1}:E${dims.end}`).setNumberFormat('0');decks.getRange(`C${start+1}:C${dims.end}`).dataValidation={rule:{type:'whole',operator:'between',formula1:0,formula2:10}};
 let total=dims.end+1;decks.getRange(`B${total}`).values=[['当前总张数']];decks.getRange(`C${total}`).formulas=[[`=SUM(C${start+1}:C${dims.end})`]];base(decks,`A${total}:H${total+4}`);decks.getRange(`B${total}:E${total}`).format.fill=C.pale;
 note(decks,`A${total+2}`,dk.route);note(decks,`A${total+3}`,dk.warning);deckRanges.push({start,end:dims.end,total,name:dk.name});dr=total+6;
}
for(const b of deckRanges)decks.getRange(`E${b.start+1}:E${b.end}`).format.horizontalAlignment='center';
decks.freezePanes.freezeRows(4);decks.freezePanes.freezeColumns(2);

title(params,'霜月 v0.2 · 参数与局部算术','黄色格可改。这里只重算阈值、月蚀和资源算术；卡面与说明文档仍是v0.2种子快照。','D',250);
note(params,'A4','每次只改一类参数。先看阈值可控性与资源收支，不把局部伤害计算当作战斗胜率。');
const parameterRows={};d.parameters.forEach((x,i)=>parameterRows[x[0]]=7+i);
grid(params,6,['参数','数值 · 可改','建议对照','调整时观察'],d.parameters.map(x=>[x[1],x[2],x[3],x[4]]),[275,135,225,625]);
params.getRange('B7:B26').format.fill=C.input;params.getRange('B7:B26').setNumberFormat('0');
params.getRange('B7:B26').dataValidation={rule:{type:'whole',operator:'between',formula1:0,formula2:999}};
for(const id of ['blood_low','blood_high']){let n=parameterRows[id];params.getRange(`B${n}`).setNumberFormat('0%');params.getRange(`B${n}`).dataValidation={rule:{type:'decimal',operator:'between',formula1:0,formula2:1}};}
const cell=id=>`B${parameterRows[id]}`;
const calcs=[
 ['血月低线',`=IF(AND(ISNUMBER(${cell('max_hp')}),ISNUMBER(${cell('blood_low')}),${cell('max_hp')}>0,${cell('blood_low')}>0,${cell('blood_low')}<1),ROUNDDOWN(${cell('max_hp')}*${cell('blood_low')},0),"请检查生命与比例")`,'生命不高于此值时才满足低血条件'],
 ['重新蓄势高线',`=IF(AND(ISNUMBER(${cell('max_hp')}),ISNUMBER(${cell('blood_high')}),${cell('max_hp')}>0,${cell('blood_high')}>0,${cell('blood_high')}<=1),ROUNDUP(${cell('max_hp')}*${cell('blood_high')},0),"请检查生命与比例")`,'退出血月后，须达到该值才能再次蓄势'],
 ['两条线间隔',`=IF(AND(ISNUMBER(B30),ISNUMBER(B31),B31>B30),B31-B30,"高线须大于低线")`,'这个差值决定回血与再次压血的幅度'],
 ['完整月蚀基础伤害',`=${cell('eclipse_damage')}*${cell('eclipse_hits')}`,'目标存活且无格挡、无伤害上限的基础值'],
 ['血月中的完整月蚀',`=B33*${cell('blood_mult')}`,'倍率不增加击数'],
 ['潮汐基础版一次格挡',`=${cell('eclipse_hits')}`,'每击1格挡；目标提前死亡需减少击数'],
 ['碎月成星基础版伤害',`=MAX(1,${cell('eclipse_damage')}-1)*(${cell('eclipse_hits')}+2)`,'单个未升级能力，无其他修正'],
 ['碎月成星升级版伤害',`=${cell('eclipse_damage')}*(${cell('eclipse_hits')}+2)`,'单个已升级能力，无其他修正']
];
grid(params,29,['局部指标','计算结果','成立条件'],calcs.map(x=>[x[0],null,x[2]]),[275,135,850]);
calcs.forEach((x,i)=>params.getRange(`B${30+i}`).formulas=[[x[1]]]);params.getRange('B30:B37').setNumberFormat('0');
grid(params,40,['回生算术','数值 · 可改','说明'],[['当前生命',31,'不高于最大生命'],['可回收生命',7,'仅未被恢复抵消的本场主动支付'],['回生请求',6,'牌面提出的恢复量'],['实际恢复',null,'受到额度与缺失生命双重限制'],['恢复后生命',null,'不代表完整战斗模拟'],['恢复后额度',null,'真正治疗也要冲销额度']],[275,135,850]);
params.getRange('B41:B43').format.fill=C.input;params.getRange('B41:B46').setNumberFormat('0');
params.getRange('B44').formulas=[[`=IF(AND(ISNUMBER(B41),ISNUMBER(B42),ISNUMBER(B43),B41>0,B41<=${cell('max_hp')},B42>=0,B43>=0),MIN(B43,B42,${cell('max_hp')}-B41),"输入无效")`]];
params.getRange('B45').formulas=[['=IF(ISNUMBER(B44),B41+B44,"输入无效")']];params.getRange('B46').formulas=[['=IF(ISNUMBER(B44),MAX(0,B42-B44),"输入无效")']];
note(params,'A48','本表不实现抽牌、敌人意图、格挡、伤害管线或战斗结算；用于审查设计参数之间的算术关系。');
params.freezePanes.freezeRows(6);params.freezePanes.freezeColumns(1);

title(extra,'霜月 v0.2 · 衍生牌与灵感来源','衍生牌不计入64张角色卡池。下方资料是机制启发；全部卡牌和数值为本次原创设计。','D',340);
note(extra,'A4','起始牌：寒锋×4、凝霜×4、映月×1、归冬×1。初始遗物：双相佩。');
matrix(extra,5,[['衍生卡名','name'],['ID','id'],['费用','cost'],['基础效果','base'],['升级后效果','upgraded'],['来源与时点','origin'],['边界','note']],d.tokens,340);
grid(extra,14,['起始项目','值','说明'],[['最大生命',72,'起测值'],['基础能量',3,'每回合'],['基础抽牌',5,'每回合'],['初始形态','冰','所有战斗默认进入冰；低血时在自己的开始检查点可进血月'],['初始遗物','双相佩',d.starter.relic]],[180,340,670]);
grid(extra,22,['参考','机制启发','本案取舍','资料链接'],d.sources.map(x=>[x[0],x[2],x[3],x[1]]),[180,340,520,600]);
note(extra,'A32','资料核对日期：2026-10-06。旧若叶睦研究固定在已有提交，未宣称它代表该Mod的最新版本。');
extra.freezePanes.freezeRows(5);extra.freezePanes.freezeColumns(1);

wb.recalculate();
const totals=summary.getRange('B36:B40').values;
if(JSON.stringify(totals)!==JSON.stringify([[4],[20],[28],[12],[64]]))throw Error('Inventory mismatch');
for(const x of deckRanges)if(decks.getRange(`C${x.total}`).values[0][0]!==20)throw Error('Deck count mismatch');
const expected=[28,40,12,16,32,4,18,24];
if(JSON.stringify(params.getRange('B30:B37').values.map(x=>x[0]))!==JSON.stringify(expected))throw Error('Parameter arithmetic mismatch');
if(JSON.stringify(params.getRange('B44:B46').values)!==JSON.stringify([[6],[37],[1]]))throw Error('Recovery arithmetic mismatch');
// Exercise live inputs, then restore authoritative seeds before final export.
params.getRange(cell('max_hp')).values=[[73]];
if(params.getRange('B30').values[0][0]!==29||params.getRange('B31').values[0][0]!==41)throw Error('Threshold edit did not propagate');
params.getRange(cell('max_hp')).values=[[72]];
params.getRange('B42').values=[[0]];if(params.getRange('B44').values[0][0]!==0)throw Error('Zero recovery balance');params.getRange('B42').values=[[7]];
params.getRange('B41').values=[[null]];if(params.getRange('B44').values[0][0]!=='输入无效')throw Error('Blank recovery input');params.getRange('B41').values=[[31]];
wb.recalculate();
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:100},maxChars:4000});
await fs.writeFile(path.join(qa,'formula-errors.ndjson'),errors.ndjson);
await fs.writeFile(path.join(qa,'workbook-checks.json'),JSON.stringify({inventory:totals,deckRanges,blocks,arithmetic:params.getRange('B30:B37').values,recovery:params.getRange('B44:B46').values,specification_checks:audit.count},null,2));
await(await SpreadsheetFile.exportXlsx(wb)).save(output);
try{await fs.rename(output+'.inspect.ndjson',path.join(qa,'export.inspect.ndjson'));}catch(e){if(e.code!=='ENOENT')throw e;}
const previews=[['summary','方案与规则','A6:C9'],['rules','方案与规则','A13:C18'],['cards','64张卡牌','A5:D17'],['review','逐组审阅','A6:D20'],['decks','样例卡组','A6:G15'],['params','参数与算术','A29:C37'],['extra','衍生与来源','A5:C11'],['review-inputs','64张卡牌','A18:D23']];
previews.push(['long-cards','逐组审阅','B109:E121'],['rare-cards','逐组审阅','B160:E172']);
const wanted=new Set(process.argv.slice(2));
for(const [name,sheetName,range] of previews){if(wanted.size&&!wanted.has(name))continue;const blob=await wb.render({sheetName,range,scale:1.2,format:'png'});await fs.writeFile(path.join(qa,name+'.png'),new Uint8Array(await blob.arrayBuffer()));}
console.log(JSON.stringify({output,qa,sheets:6,cards:64,decks:4,specification_checks:audit.count}));
