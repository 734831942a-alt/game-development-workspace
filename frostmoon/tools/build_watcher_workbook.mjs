import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const outDir=path.resolve(root,'../outputs/01a1009b-46b5-7492-aa6a-c58b009ff7e0');
const qa=path.resolve(root,'../artifacts/watcher-qa');
await fs.mkdir(outDir,{recursive:true});await fs.mkdir(qa,{recursive:true});
const d=JSON.parse(await fs.readFile(path.join(root,'data/watcher_reference.json'),'utf8'));
const wb=Workbook.create();
const overview=wb.worksheets.add('构筑包总览');
const all=wb.worksheets.add('75张卡牌');
const grouped=wb.worksheets.add('分包卡牌');
const extra=wb.worksheets.add('衍生牌与规则');
const C={navy:'#29334D',purple:'#65518C',ink:'#253047',muted:'#647087',line:'#D5DAE5',pale:'#F1EDF7',white:'#FFFFFF',alt:'#F6F7FA',green:'#EAF3F0'};
const by=Object.fromEntries(d.cards.map((c,i)=>[c.en,{...c,index:i}]));
function col(i){let s='';for(i++;i;i=Math.floor((i-1)/26))s=String.fromCharCode(65+(i-1)%26)+s;return s;}
function base(s,range){s.getRange(range).format={font:{name:'Arial',size:11,color:C.ink},verticalAlignment:'center',wrapText:true,rowHeight:24};}
function header(s,range,color=C.navy){s.getRange(range).format={fill:color,font:{name:'Arial',size:11,bold:true,color:C.white},horizontalAlignment:'center',verticalAlignment:'center',wrapText:true,rowHeight:30,borders:{right:{style:'thin',color:C.white}}};}
function note(s,cell,text){s.getRange(cell).values=[[text]];s.getRange(cell).format={font:{name:'Arial',size:11,italic:true,color:C.muted},wrapText:false,rowHeight:25};}
function title(s,text,noteText,last='G',width=300){
 s.showGridLines=false;s.tabColor=C.purple;base(s,`A1:${last}4`);
 s.getRange(`A1:A4`).format.columnWidthPx=180;
 s.getRange(`B1:${last}4`).format.columnWidthPx=width;
 s.getRange('A1').values=[[text]];s.getRange('A1').format={font:{name:'Arial',size:16,bold:true,color:C.navy},wrapText:false,rowHeight:31};
 note(s,'A2',noteText);s.getRange(`A3:${last}3`).format.borders={bottom:{style:'thin',color:C.line}};
}
function weight(text){return [...String(text??'')].reduce((n,c)=>n+(c.codePointAt(0)>255?2:1),0);}
function fitRow(s,n,values,width,last,min=25){
 // Conservative capacity for CJK at 11 pt; retain readable font size.
 const cap=(width-24)/7.7;
 const lines=Math.max(1,...values.map(v=>String(v??'').split('\n').reduce((sum,x)=>sum+Math.max(1,Math.ceil(weight(x)/cap)),0)));
 s.getRange(`A${n}:${last}${n}`).format.rowHeight=Math.max(min,lines*16+12);
}
function matrix(s,start,attrs,items,width=300){
 const last=col(items.length);const end=start+attrs.length-1;
 const values=attrs.map(([label,key])=>[label,...items.map(x=>x[key]??'—')]);
 base(s,`A${start}:${last}${end}`);s.getRange(`A${start}:${last}${end}`).values=values;
 s.getRange(`A${start}:A${end}`).format.columnWidthPx=180;
 s.getRange(`B${start}:${last}${end}`).format.columnWidthPx=width;
 for(let i=0;i<attrs.length;i++){
  const n=start+i;if(i%2===1)s.getRange(`A${n}:${last}${n}`).format.fill=C.alt;
  s.getRange(`A${n}`).format={fill:C.pale,font:{name:'Arial',size:11,bold:true,color:C.purple}};
  fitRow(s,n,values[i].slice(1),width,last,25);
 }
 header(s,`A${start}:${last}${start}`);
 return {last,end,values};
}
const attrs=[['卡牌名','name'],['英文名','en'],['类型','type'],['稀有度','rarity'],['费用 · 基础','cost'],['费用 · 升级','up_cost'],['基础效果','base'],['升级后完整效果','upgraded'],['升级改动','delta'],['关键词 · 基础','keywords'],['设计职责 · 分析','role'],['适配构筑包 · 分析','synergy'],['时序／使用边界','note'],['英文效果来源','source']];
const masterRows=Object.fromEntries(attrs.map((a,i)=>[a[1],5+i]));
title(all,'观者 · 75 张完整卡池','STS1 PC v2.3 标准卡池｜属性纵排、每张卡一列｜向右滚动；左侧属性和卡名已冻结','BX');
note(all,'A4','按初始→普通→罕见→稀有排列。费用为能量；X=投入全部当前能量；“不可打出”不等于0费。');
const master=matrix(all,5,attrs,d.cards,300);
all.getRange(`B9:${master.last}10`).setNumberFormat('0');
all.getRange(`B9:${master.last}10`).format.horizontalAlignment='right';
all.getRange(`A13:${master.last}13`).format.fill=C.green;
all.getRange(`A16:${master.last}17`).format.verticalAlignment='top';
all.getRange(`B18:${master.last}18`).format.font.color='#325F95';
all.freezePanes.freezeRows(5);all.freezePanes.freezeColumns(1);
note(all,'A20','数据核对：2026-10-03。效果按游戏语义重新表述；能力生效时序已展开。分析字段是设计参考，不是官方分组或强度排名。');
note(all,'A21','中文卡名与稀有度：18183 75张观者卡牌图鉴；生成牌中文名、化智为空时序：灰机中文维基；数值与升级：英文单卡页／日文表。');
all.getRange('A22:B25').values=[
 ['中文卡名目录','https://www.18183.com/gonglue/202207/4064601.html'],
 ['中文规则交叉核对','https://sts.huijiwiki.com/wiki/紫色牌'],
 ['升级数值交叉核对','https://wikiwiki.jp/slaythespire/ウォッチャーのカード一覧'],
 ['英文卡池目录','https://www.slaythespire.gg/cards/watcher']
];base(all,'A22:B25');all.getRange('B22:B25').format.wrapText=false;all.getRange('B22:B25').format.font.color='#325F95';

// A reading view grouped by build component. Each section has at most six cards.
// Card facts are direct references to the authoritative 75-card matrix.
title(grouped,'观者 · 按构筑包逐组看牌','每组六张以内，纵向浏览；核心在前、补件在后。重复出现代表可混搭，卡牌事实引用“75张卡牌”。','G',270);
note(grouped,'A4','可用 Excel 查找包编号（如 09）或卡名；各包的起始位置见“构筑包总览”第15行。');
grouped.freezePanes.freezeRows(4);grouped.freezePanes.freezeColumns(1);
const groupedAttrs=[['卡牌名','name'],['包内职责 · 分析','packageRole'],['英文名','en'],['类型／稀有度','typeRarity'],['费用 · 基础','cost'],['费用 · 升级','up_cost'],['基础效果','base'],['升级后完整效果','upgraded'],['升级改动','delta'],['关键词 · 基础','keywords'],['设计职责 · 分析','role'],['时序／使用边界','note']];
let next=6;const packageStarts={},groupBlocks=[];
for(const p of d.packages){
 packageStarts[p.code]=next;
 const ids=[...p.core,...p.support];
 for(let j=0;j<ids.length;j+=6){
  const selected=ids.slice(j,j+6).map(x=>({...by[x],packageRole:p.core.includes(x)?'核心组件':'可选补件',typeRarity:by[x].type+' / '+by[x].rarity}));
  const heading=next,start=next+1,last=col(selected.length);
  base(grouped,`A${heading}:G${heading}`);grouped.getRange(`A${heading}`).values=[[`${p.code}  ${p.name}  ·  ${j+1}—${Math.min(j+6,ids.length)} / ${ids.length}`]];
  grouped.getRange(`A${heading}:G${heading}`).format.fill=C.purple;
  grouped.getRange(`A${heading}`).format={font:{name:'Arial',size:11,bold:true,color:C.white},wrapText:false,rowHeight:28};
  matrix(grouped,start,groupedAttrs,selected,270);
  groupedAttrs.forEach(([label,key],k)=>{
   if(['packageRole','typeRarity'].includes(key))return;
   grouped.getRange(`B${start+k}:${last}${start+k}`).formulas=[selected.map(c=>`='75张卡牌'!${col(c.index+1)}${masterRows[key]}`)];
  });
  grouped.getRange(`B${start+4}:${last}${start+5}`).setNumberFormat('0');
  grouped.getRange(`B${start+4}:${last}${start+5}`).format.horizontalAlignment='right';
  grouped.getRange(`A${start+8}:${last}${start+8}`).format.fill=C.green;
  grouped.getRange(`B${start+1}:${last}${start+1}`).format.font.color=C.purple;
  groupBlocks.push({package:p.code,heading,start,end:start+groupedAttrs.length-1,ids:selected.map(x=>x.en)});
  next=start+groupedAttrs.length+2;
 }
}

title(overview,'观者 · 构筑包参考','75 张紫色牌全收录 + 8 张固定衍生牌｜11 个设计分析包可以混搭，不是官方固定套牌，也不是穷举所有组合','L',320);
note(overview,'A4','先看资源循环与限制，再在“分包卡牌”逐张对照；各卡基础费用、升级费用和完整效果分行列出。');
const pItems=d.packages.map(p=>({
 name:`${p.code}  ${p.name}`,kind:p.code==='11'?'跨构筑的通用支撑':p.code==='08'?'防御与减益补充模块':'构筑机制／输出方向',
 core:p.core.map(x=>by[x].name).join('、'),support:p.support.map(x=>by[x].name).join('、'),
 loop:p.loop,requires:p.requires,weakness:p.weakness,transfer:p.transfer,
 first:`分包卡牌!A${packageStarts[p.code]}`,coreCount:p.core.length,total:p.core.length+p.support.length
}));
const pAttrs=[['构筑包','name'],['包的性质','kind'],['核心牌','core'],['可选补件','support'],['如何运转','loop'],['启动／成立条件','requires'],['限制与冲突','weakness'],['对霜月的参考 · 分析','transfer'],['核心牌种数','coreCount'],['本包列示牌种数','total'],['分包页起始位置','first']];
matrix(overview,5,pAttrs,pItems,320);
overview.getRange('B13:L14').setNumberFormat('0');overview.getRange('B13:L14').format.horizontalAlignment='right';
overview.getRange('A12:L12').format.fill=C.green;overview.getRange('B7:L12').format.verticalAlignment='top';
overview.freezePanes.freezeRows(5);overview.freezePanes.freezeColumns(1);
note(overview,'A17','读表口径：核心＝直接驱动该机制的牌；补件＝改善启动、生存或兑现的牌。包内不是拿牌清单，重复归属不能加总成卡池张数。');
base(overview,'A19:D28');
overview.getRange('A19:D19').values=[['完整性核对','实际牌种数','目录口径','说明']];header(overview,'A19:D19');
[['初始',4],['普通',19],['罕见',35],['稀有',17]].forEach(([rare,expected],i)=>{
 const r=20+i;overview.getRange(`A${r}:D${r}`).values=[[rare,null,expected,rare==='初始'?'4种初始牌；初始牌组有10张实体卡':'不含无色衍生牌']];
 overview.getRange(`B${r}`).formulas=[[`=COUNTIF('75张卡牌'!B8:BX8,A${r})`]];
});
overview.getRange('A24:D25').values=[['紫色牌合计',null,75,'按卡牌种类计数；升级版不额外计一种'],['固定衍生牌',null,8,'与紫色牌分开；许愿的3个选项已写在母牌效果中']];
overview.getRange('B24').formulas=[['=SUM(B20:B23)']];overview.getRange('B25').formulas=[["=COUNTA('衍生牌与规则'!B5:I5)"]];
overview.getRange('A24:D25').format.fill=C.pale;overview.getRange('B20:C25').setNumberFormat('0');
overview.getRange('D20:D25').format.wrapText=true;overview.getRange('A20:D25').format.rowHeight=44;
note(overview,'A27','建议参考顺序：姿态循环 → 真言神格 → 点穴叠层 → 格挡回报。最贴近霜蚀入超然、月痕引爆和混合路线的职责拆分。');
note(overview,'A28','全部分包与“对霜月的参考”均为本次分析；未模拟胜率，不应直接把观者倍率或阈值照搬为霜月平衡参数。');

title(extra,'观者 · 衍生牌与规则','8 张固定衍生牌单列；不计入 75 张紫色牌。基础／升级描述的是子牌自身等级，不代表母牌升级就会生成升级版。','I',300);
note(extra,'A4','生成位置与来源分行列出。许愿的三个选择见主卡池；他山之石的随机跨颜色结果不在这里穷举。');
matrix(extra,5,[['衍生卡名','name'],['英文名','en'],['类型','type'],['归属','rarity'],['费用 · 基础','cost'],['费用 · 升级','up_cost'],['基础效果','base'],['升级后完整效果','upgraded'],['生成来源','origin'],['使用边界','note'],['效果来源','source']],d.generated,300);
extra.getRange('B9:I10').setNumberFormat('0');extra.getRange('B9:I10').format.horizontalAlignment='right';
extra.getRange('B15:I15').format.font.color='#325F95';
extra.freezePanes.freezeRows(5);extra.freezePanes.freezeColumns(1);
note(extra,'A17','衍生牌中文名：灰机中文维基“无色特殊攻击牌／技能牌”；Miracle 英文页能量图标缺失，按中文资料核为1→2能量。');
extra.getRange('A18:B19').values=[['中文攻击衍生牌','https://sts.huijiwiki.com/wiki/无色特殊攻击牌'],['中文技能衍生牌','https://sts.huijiwiki.com/wiki/无色特殊技能牌']];base(extra,'A18:B19');extra.getRange('B18:B19').format.wrapText=false;extra.getRange('B18:B19').format.font.color='#325F95';
const rules=[
 ['愤怒 Wrath','攻击造成的伤害×2；受到的攻击伤害×2。','点穴的生命流失、欧米伽的能力伤害不因此翻倍。','https://slay-the-spire.fandom.com/wiki/Wrath'],
 ['平静 Calm','退出平静时获得2能量；进入时本身不直接给能量。','从平静切到其他姿态或退出到无姿态都可触发；再次进入同姿态不算退出。','https://slay-the-spire.fandom.com/wiki/Calm'],
 ['神格 Divinity','进入时获得3能量；攻击伤害×3；下个自己的回合开始时退出。','从平静切到神格还会结算退出平静的2能量；神格不增加受到的攻击伤害。','https://slay-the-spire.fandom.com/wiki/Divinity'],
 ['真言 Mantra','不在神格时，达到10层消耗10层并入神格，溢出保留；神格期间继续累积，下一回合退出后可再次判定入场。','光辉读取本战斗累计获得的真言；渎神直接入神格而不产真言。','https://slay-the-spire.fandom.com/wiki/Divinity'],
 ['占卜 Scry','查看抽牌堆顶部若干张，选择其中哪些移入弃牌堆，其余留在抽牌堆。','不会自动抽牌或因抽牌堆空而洗牌；空堆占卜不会回收迂回。','https://slay-the-spire.fandom.com/wiki/Scry'],
 ['保留 Retain','回合结束时不把该牌作为普通手牌弃掉。','确立基础在保留结算时降费；冥想赋予的是该次回合结束的保留。','https://slay-the-spire.fandom.com/wiki/Retain'],
 ['消耗／虚无／固有','消耗：移出本场常规循环；虚无：回合结束仍在手里则消耗；固有：进入起手。','能力牌打出后进入能力区，通常也不再随抽弃牌循环；能力与消耗不是同一关键词。','https://slaythespire.wiki.gg/wiki/Keywords'],
 ['印记 Mark','点穴施加后，使所有敌人按各自已有印记流失生命；通常不会在触发时清空。','与霜月阈值清空型月痕不同；不能把两者的层数效率直接等同。','https://www.slaythespire.gg/cards/watcher/Pressure_Points'],
 ['多段与事件粒度','以手拒之按攻击伤害段触发格挡；摆手按每次获得格挡触发。','设计月蚀时应分别定义一次出牌、每段攻击、造成伤害和获得格挡，避免隐性倍增。','https://www.slaythespire.gg/cards/watcher/Talk_to_the_Hand'],
 ['母牌与子牌升级','评估、祈祷、改造现实、欺瞒现实、立地升天升级后，默认仍生成普通子牌。','操控现实改变生成时的等级；收集明确生成奇迹+。','https://www.slaythespire.gg/cards/watcher/Master_Reality']
];
base(extra,'A22:D33');extra.getRange('A22:D22').values=[['关键规则','规则摘要','设计参考／边界','资料入口']];header(extra,'A22:D22');
rules.forEach((r,i)=>{const n=23+i;extra.getRange(`A${n}:D${n}`).values=[r];if(i%2)extra.getRange(`A${n}:D${n}`).format.fill=C.alt;fitRow(extra,n,r.slice(1),300,'D',72);extra.getRange(`D${n}`).format.font.color='#325F95';});
const examples=[
 ['循环示例（分析）','猛虎下山已生效，起点为平静：暴怒+ → 内心宁静。两牌共付2能量，退出平静返2；入愤怒抽2。','这是资源收支示例。还须能稳定重抽这两张牌，并解决启动与防御；凑齐牌名不等于已无限。'],
 ['点穴示例（算术）','同一无人工制品目标，连续打出两次未升级点穴：第一次8生命流失；第二次16；累计24。','按同一目标、无额外规则修改计算。每次只对选定目标加印记，但兑现所有目标已有印记。'],
 ['多段示例（算术）','火焰纹+的8点加成接未升级诸神之黄昏：每击5+8，重复5次，合计65基础伤害。','不含力量、易伤、姿态、格挡等修正；多敌人时会分散。应先决定月蚀是否继承攻击加成。'],
 ['初始卡组口径','打击×4、防御×4、暴怒×1、警惕×1，共10张。初始遗物净水生成的奇迹不算永久初始牌组。','“75张”是卡牌种类数量；不把初始牌副本、升级版或固定衍生牌重复计入。']
];
base(extra,'A35:C39');extra.getRange('A35:C35').values=[['辅助例子','具体过程','成立条件']];header(extra,'A35:C35');
examples.forEach((r,i)=>{const n=36+i;extra.getRange(`A${n}:C${n}`).values=[r];fitRow(extra,n,r.slice(1),300,'C',100);if(i%2)extra.getRange(`A${n}:C${n}`).format.fill=C.alt;});

wb.recalculate();
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:100},maxChars:6000});
await fs.writeFile(path.join(qa,'formula-scan.ndjson'),errors.ndjson);
const inspect=await wb.inspect({kind:'table',range:'构筑包总览!A19:D25',include:'values,formulas',tableMaxRows:7,tableMaxCols:4,maxChars:4000});
await fs.writeFile(path.join(qa,'inventory.ndjson'),inspect.ndjson);
if(JSON.stringify(overview.getRange('B20:B25').values)!==JSON.stringify([[4],[19],[35],[17],[75],[8]]))throw Error('Inventory formulas did not recalculate correctly');
for(const b of groupBlocks){
 const names=grouped.getRange(`B${b.start}:${col(b.ids.length)}${b.start}`).values[0];
 if(JSON.stringify(names)!==JSON.stringify(b.ids.map(x=>by[x].name)))throw Error('Grouped card name references differ');
}
const checks={inventory:overview.getRange('B20:B25').values,packages:d.packages.length,groupBlocks,formulaScan:errors.ndjson};
await fs.writeFile(path.join(qa,'checks.json'),JSON.stringify(checks,null,2));
const output=path.join(outDir,'杀戮尖塔1观者卡组包参考.xlsx');
await(await SpreadsheetFile.exportXlsx(wb)).save(output);
try{await fs.rename(output+'.inspect.ndjson',path.join(qa,'export.inspect.ndjson'));}catch(e){if(e.code!=='ENOENT')throw e;}
const previews=[
 ['overview','构筑包总览','A5:C15'],
 ['cards','75张卡牌','A5:D17'],
 ['cards-long','75张卡牌','BA5:BC17'],
 ['grouped','分包卡牌',`A${groupBlocks[0].heading}:D${groupBlocks[0].end}`],
 ['generated','衍生牌与规则','A5:D14'],
 ['rules','衍生牌与规则','A22:C27'],
 ['top','构筑包总览','A1:D6'],
 ['counts','构筑包总览','A19:D25'],
 ['late-group','分包卡牌',`A${groupBlocks.at(-1).heading}:D${groupBlocks.at(-1).end}`]
];
const renderNames=new Set(process.argv.slice(2));
for(const [name,sheetName,range] of previews){if(renderNames.size&&!renderNames.has(name))continue;const blob=await wb.render({sheetName,range,scale:1.3,format:'png'});await fs.writeFile(path.join(qa,name+'.png'),new Uint8Array(await blob.arrayBuffer()));}
console.log(JSON.stringify({output,inventory:checks.inventory,groupBlocks:groupBlocks.length,packageStarts,qa},null,2));
