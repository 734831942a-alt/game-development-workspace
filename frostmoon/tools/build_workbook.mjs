import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output=path.resolve(root,'../outputs/01a1009b-46b5-7492-aa6a-c58b009ff7e0');
const qa=path.resolve(root,'../artifacts/frostmoon-qa');
await fs.mkdir(output,{recursive:true}); await fs.mkdir(qa,{recursive:true});
const data=JSON.parse(await fs.readFile(path.join(root,'data/reference_cards.json'),'utf8'));
const proto=JSON.parse(await fs.readFile(path.join(root,'data/prototype.json'),'utf8'));
const stats=JSON.parse(await fs.readFile(path.join(root,'data/reference_stats.json'),'utf8'));
const wb=Workbook.create();
const summary=wb.worksheets.add('研究摘要');
const cards=wb.worksheets.add('15张原型');
const params=wb.worksheets.add('参数试验');
const ref=wb.worksheets.add('若叶睦卡池');
const colors={ink:'#20283A',navy:'#29334D',violet:'#65518C',pale:'#F2EEF8',rule:'#CCD3DE',input:'#FFF1CC'};
function col(i){let s='';for(i++;i;i=Math.floor((i-1)/26))s=String.fromCharCode(65+(i-1)%26)+s;return s;}
function fmt(sheet,range){const r=sheet.getRange(range);r.format.font={name:'Arial',size:11,color:colors.ink};r.format.verticalAlignment='center';r.format.rowHeight=25;}
function title(sheet,text,end='J',note=''){sheet.showGridLines=false;fmt(sheet,`A1:${end}4`);sheet.getRange('A2').values=[[text]];sheet.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:colors.navy};sheet.getRange(`A3:${end}3`).format.borders={bottom:{style:'thin',color:colors.rule}};if(note){sheet.getRange('A4').values=[[note]];sheet.getRange('A4').format.font={name:'Arial',size:11,italic:true,color:'#627087'};}}
function header(sheet,range){sheet.getRange(range).format={fill:colors.navy,font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},horizontalAlignment:'center',verticalAlignment:'center',wrapText:true,rowHeight:30};}
function table(sheet,name,headers,rows,widths,start=6){
  const end=start+rows.length;const last=col(headers.length-1);
  fmt(sheet,`A${start}:${last}${end}`);
  sheet.getRange(`A${start}:${last}${end}`).values=[headers,...rows];
  sheet.getRange(`A${start+1}:${last}${end}`).format.wrapText=true;
  sheet.getRange(`A${start+1}:${last}${end}`).format.verticalAlignment='top';
  widths.forEach((w,i)=>sheet.getRange(`${col(i)}${start}:${col(i)}${end}`).format.columnWidthPx=w);
  const t=sheet.tables.add(`A${start}:${last}${end}`,true,name);t.showFilterButton=true;t.style='TableStyleLight1';
  sheet.getRange(`A${start+1}:${last}${end}`).format.fill='#FFFFFF';
  header(sheet,`A${start}:${last}${start}`);
  for(let j=0;j<rows.length;j++){
    let lines=1;
    rows[j].forEach((v,i)=>{const s=String(v??'');const len=[...s].reduce((a,c)=>a+(c.codePointAt(0)>255?2:1),0);const capacity=Math.max(8,(widths[i]-16)/7);lines=Math.max(lines,...s.split('\n').map(x=>Math.ceil([...x].reduce((a,c)=>a+(c.codePointAt(0)>255?2:1),0)/capacity)),Math.ceil(len/capacity));});
    sheet.getRange(`A${start+j+1}:${last}${start+j+1}`).format.rowHeight=Math.max(48,Math.ceil(lines*15.5+12));
    if(j%2===1)sheet.getRange(`A${start+j+1}:${last}${start+j+1}`).format.fill='#F5F6FA';
  }
  sheet.freezePanes.freezeRows(start);sheet.freezePanes.freezeColumns(2);
  return {start,end,last};
}

title(ref,'若叶睦完整源码卡牌清单','Q','固定提交 03dc9ad，93类。F至H为源码效果；I、J、K、N、O为研究者标注。');
ref.getRange('A5').values=[['不可把93类都视为普通奖励牌。升级栏=基础效果加改动；关联Power与时序说明见研究报告。']];
const roleKeys=['Generator','Consumer','Payoff','Enabler','Bridge','Build-around','Utility'];
const roleCols=Object.fromEntries(roleKeys.map((r,i)=>[r,col(15+i)]));
const refHeaders=['Card ID','卡名','费用','类型','稀有度','基础效果','升级变化','固定关键词','构筑标签','设计职责','升级分类','获得范围','模式限制','纯Utility','设计判断与核对备注',...roleKeys,'源码定位'];
const refRows=data.cards.map(r=>[r.id,r.name,r.cost,r.type,r.rarity,r.base_effect,r.upgrade_delta,r.keywords,r.archetypes.join('、'),r.roles.join(' / '),r.upgrade_kind,r.scope,r.multiplayer_only?'仅多人':'单人可用',r.pure_utility?'是':'否',r.interpretation,...roleKeys.map(k=>r.roles.includes(k)?'是':'否'),r.source_url]);
// Explicit role flags also make filtering and exact-match formulas reliable across engines.
// Source URLs stay inside the sortable table so citations cannot detach from their cards.
const refDims=table(ref,'MutsumiCards',refHeaders,refRows,[175,190,64,85,100,450,290,135,200,260,90,110,100,90,430,...roleKeys.map(()=>112),530]);

title(cards,'霜月15张原型牌','L','v0.1设计提案。数字为起测参数，尚无游玩结论；文字使用基准参数快照。');
cards.getRange('A5').values=[['Frost 5 / Moon 5 / Bridge 3 / Utility 2。共同规则与事件时序见原型规则.md。']];
const pHeaders=['ID','卡名','分组','费用','类型','稀有度','目标','基础效果','升级变化','设计职责','适用构筑','首轮要观察什么'];
table(cards,'FrostmoonPrototype',pHeaders,proto.cards.map(r=>[r.id,r.name,r.group,r.cost,r.type,r.rarity,r.target,r.base,r.upgrade,r.roles.join(' / '),r.archetypes.join('、'),r.test]),[68,130,100,60,85,100,120,510,250,235,200,435]);
cards.tabColor=colors.navy;

title(params,'霜月参数试验','E','黄色格可修改。公式只计算局部算术，不模拟战斗，也不自动改写原型卡牌文字。');
const paramRows={};
proto.parameters.forEach((p,i)=>paramRows[p.id]=7+i);
const paramDims=table(params,'PrototypeParameters',['参数','单位','当前起测值','建议对照','观察目的'],proto.parameters.map(p=>[p.name,p.unit,p.seed,p.candidates,p.reason]),[230,175,110,300,590]);
params.freezePanes.unfreeze();
params.getRange(`C7:C${paramDims.end}`).format.fill=colors.input;
params.getRange(`C7:C${paramDims.end}`).format.horizontalAlignment='right';params.getRange(`C7:C${paramDims.end}`).setNumberFormat('0');
params.getRange(`C7:C${paramDims.end}`).dataValidation={rule:{type:'whole',operator:'between',formula1:1,formula2:100}};
params.getRange(`C${paramRows.transcendence_entry_draw}`).dataValidation={rule:{type:'whole',operator:'between',formula1:0,formula2:1}};
const pr=id=>`C${paramRows[id]}`;
const metrics=[
 ['完整月蚀基础伤害',`=${pr('eclipse_damage')}*${pr('eclipse_hits')}`,'未考虑格挡、死亡取消与其他修正'],
 ['每层月痕对应基础伤害',`=IF(${pr('moon_threshold')}>0,C23/${pr('moon_threshold')},"阈值须大于0")`,'无溢出且足额引爆的理论值，非效率实测'],
 ['单次基础支付的霜蚀兑换率',`=IF(${pr('hp_per_payment')}>0,${pr('frost_per_payment')}/${pr('hp_per_payment')},"自损须大于0")`,'单位：霜蚀/HP；不含凝霜与寒月返霜'],
 ['单靠基础支付的触发次数',`=IF(AND(${pr('frost_per_payment')}>0,${pr('frost_threshold')}>0),ROUNDUP(${pr('frost_threshold')}/${pr('frost_per_payment')},0),"阈值与产霜须大于0")`,'从0霜起，包含最后一次的溢出'],
 ['单靠基础支付的总HP成本',`=IF(ISNUMBER(C26),C26*${pr('hp_per_payment')},"产霜须大于0")`,'未计入治疗和其他来源，不是整场战斗损耗'],
 ['月落提前引爆线',`=IF(AND(${pr('moon_threshold')}>${pr('detonate_margin')},${pr('detonate_margin')}>0),${pr('moon_threshold')}-${pr('detonate_margin')},"提前量需介于0与阈值")`,'需大于0且小于月痕阈值']
];
fmt(params,'A21:E35');params.getRange('A21').values=[['局部算术检查']];params.getRange('A21').format.font.bold=true;
params.getRange('A22:C22').values=[['指标','说明','计算结果']];header(params,'A22:C22');
metrics.forEach((r,i)=>{const n=23+i;params.getRange(`A${n}:C${n}`).values=[[r[0],r[2],null]];params.getRange(`C${n}`).formulas=[[r[1]]];params.getRange(`A${n}:B${n}`).format.wrapText=true;params.getRange(`A${n}:C${n}`).format.rowHeight=52;});
params.getRange('C23:C29').setNumberFormat('0.00');params.getRange('C23').setNumberFormat('0');params.getRange('C26:C29').setNumberFormat('0');
params.getRange('A32:E32').values=[['等总伤害的击数对照','每击伤害','击数','总基础伤害','基础潮汐格挡']];header(params,'A32:E32');
params.getRange('A33:C34').values=[['v0.1基准',4,4],['只改变段数分配',8,2]];
params.getRange('D33:E34').formulas=[['=B33*C33','=C33'],['=B34*C34','=C34']];
params.getRange('A35').values=[['上方对照保持总量16；潮汐按每击1格挡，仅用于理解击数，不是全局参数情景。']];
params.tabColor='#AA93C3';

title(summary,'若叶睦卡池研究与霜月原型','K','2026年10月3日。参考源码已逐类核对；构筑标签为研究者判断，未实测平衡。');
fmt(summary,'A5:K39');
[220,100,110,110,110,125,125,22,195,135,140].forEach((w,i)=>summary.getRange(`${col(i)}5:${col(i)}39`).format.columnWidthPx=w);
summary.getRange('A6:G6').values=[['源码稀有度','卡牌类数','仅限多人','单人可用','Bridge','纯Utility','Build-around']];header(summary,'A6:G6');
const end=refDims.end;
const rr=c=>`'若叶睦卡池'!$${c}$7:$${c}$${end}`;
const rarities=['Common','Uncommon','Rare','Basic','Token','Ancient'];
rarities.forEach((r,i)=>{const n=7+i;summary.getRange(`A${n}`).values=[[r]];summary.getRange(`B${n}:G${n}`).formulas=[[
`=COUNTIFS(${rr('E')},A${n})`,
`=COUNTIFS(${rr('E')},A${n},${rr('M')},"仅多人")`,
`=B${n}-C${n}`,
`=COUNTIFS(${rr('E')},A${n},${rr(roleCols.Bridge)},"是")`,
`=COUNTIFS(${rr('E')},A${n},${rr('N')},"是")`,
`=COUNTIFS(${rr('E')},A${n},${rr(roleCols['Build-around'])},"是")`
]];});
summary.getRange('A13').values=[['全部卡牌类']];summary.getRange('B13:G13').formulas=[['=SUM(B7:B12)','=SUM(C7:C12)','=SUM(D7:D12)','=SUM(E7:E12)','=SUM(F7:F12)','=SUM(G7:G12)']];
summary.getRange('A14').values=[['普通奖励稀有度']];summary.getRange('B14:G14').formulas=[['=SUM(B7:B9)','=SUM(C7:C9)','=SUM(D7:D9)','=SUM(E7:E9)','=SUM(F7:F9)','=SUM(G7:G9)']];
summary.getRange('A13:G14').format.fill=colors.pale;summary.getRange('A13:G14').format.font.bold=true;
summary.getRange('I6:K6').values=[['普通奖励中的职责','张数','占85张比例']];header(summary,'I6:K6');
const roles=['Generator','Consumer','Payoff','Enabler','Bridge','Build-around','Utility'];
roles.forEach((role,i)=>{const n=7+i;summary.getRange(`I${n}`).values=[[role]];summary.getRange(`J${n}:K${n}`).formulas=[[
`=COUNTIFS(${rr('L')},"普通奖励",${rr(roleCols[role])},"是")`,`=J${n}/$B$14`
]];});summary.getRange('K7:K13').setNumberFormat('0.0%');
summary.getRange('I15').values=[['职责允许重叠，不可相加。']];
summary.getRange('A17:D17').values=[['单人普通奖励口径','张数','Bridge','纯Utility']];header(summary,'A17:D17');
summary.getRange('A18:D18').values=[['排除5张多人牌',null,null,null]];summary.getRange('B18:D18').formulas=[['=D14',`=COUNTIFS(${rr('L')},"普通奖励",${rr('M')},"单人可用",${rr(roleCols.Bridge)},"是")`,`=COUNTIFS(${rr('L')},"普通奖励",${rr('M')},"单人可用",${rr('N')},"是")`]];
summary.getRange('A19:D19').values=[['占单人奖励牌比例',null,null,null]];summary.getRange('C19:D19').formulas=[['=C18/B18','=D18/B18']];summary.getRange('C19:D19').setNumberFormat('0.0%');
summary.getRange('A22:D22').values=[['升级分类','普通奖励牌数','定义','']];header(summary,'A22:C22');
[['数值','只调整数量、倍率、次数或持续'],['费用','只改变能量费用'],['功能','关键词、生成规则或新增效果'],['混合','数值与功能同时变化']].forEach(([kind,desc],i)=>{const n=23+i;summary.getRange(`A${n}:C${n}`).values=[[kind,null,desc]];summary.getRange(`B${n}`).formulas=[[`=COUNTIFS(${rr('L')},"普通奖励",${rr('K')},A${n})`]];});
summary.getRange('F22:G22').values=[['霜月主分组','张数']];header(summary,'F22:G22');
['Frost','Moon','Bridge','Utility'].forEach((g,i)=>{const n=23+i;summary.getRange(`F${n}`).values=[[g]];summary.getRange(`G${n}`).formulas=[[`=COUNTIFS('15张原型'!$C$7:$C$21,F${n})`]];});
summary.getRange('A29').values=[['设计结论']];summary.getRange('A29').format.font.bold=true;
const findings=[
'Common已有7张桥梁，让基础牌参与资源循环。',
'Uncommon有11张构筑支点，Rare有10张；构筑支点不应只放在稀有牌。',
'31张奖励牌被标为Bridge，7张为纯Utility。标签是可讨论的设计判断。',
'霜月先测跨回合混合循环：超然加速标记，退出后月蚀返霜。',
'待验证：2次回合结束的窗口、HP支出、提前引爆、留霜是否值得。',
'研究边界：已核查源码与算术，未运行Mod、未模拟战斗、未验证胜率。'
];findings.forEach((s,i)=>summary.getRange(`A${30+i}`).values=[[s]]);
summary.getRange('C23:C26').format.wrapText=false;
// Explanatory cells overflow intentionally into adjacent empty space.
summary.getRange('C23:C26').format.font.color='#627087';
summary.getRange('A37').values=[['全文报告：frostmoon/研究结论.md；实现与测试规格：frostmoon/原型规则.md']];
summary.tabColor=colors.navy;

// Change an input and restore it to verify actual recalculation, not just cached numbers.
wb.recalculate();
const baseline=params.getRange('C27').values[0][0];
params.getRange(pr('frost_threshold')).values=[[7]];wb.recalculate();
const changed=params.getRange('C27').values[0][0];
params.getRange(pr('frost_threshold')).values=[[6]];wb.recalculate();
if(baseline!==6||changed!==8||params.getRange('C27').values[0][0]!==6)throw new Error(`Parameter recalculation failed ${baseline} ${changed}`);
const result=summary.getRange('B13:G14').values;
if(result[0][0]!==93||result[1][0]!==85||result[1][2]!==80||result[1][3]!==stats.reward.roles.Bridge)throw new Error('Inventory formulas failed '+JSON.stringify(result));
const groups=summary.getRange('G23:G26').values.flat();if(JSON.stringify(groups)!=='[5,5,3,2]')throw new Error('Prototype count mismatch '+groups);
const inspected=await wb.inspect({kind:'table',range:'研究摘要!A6:G19',include:'values,formulas',tableMaxRows:14,tableMaxCols:7,maxChars:10000});
await fs.writeFile(path.join(qa,'summary-inspection.ndjson'),inspected.ndjson);
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:100},maxChars:6000});
await fs.writeFile(path.join(qa,'formula-errors.ndjson'),errors.ndjson);
const previews=[['研究摘要','A1:K37','summary'],['15张原型','A1:I10','prototype'],['15张原型','G16:L21','prototype-bridge'],['参数试验','A1:E18','parameters'],['参数试验','A21:E35','calculations'],['若叶睦卡池','A1:G11','reference-effects'],['若叶睦卡池','H6:O11','reference-tags'],['若叶睦卡池','F51:G54','reference-long']];
for(const [sheetName,range,name] of previews){const blob=await wb.render({sheetName,range,scale:1.3,format:'png'});await fs.writeFile(path.join(qa,name+'.png'),new Uint8Array(await blob.arrayBuffer()));}
const exported=await SpreadsheetFile.exportXlsx(wb);await exported.save(path.join(output,'霜月卡池研究与原型.xlsx'));
const inspectSidecar=path.join(output,'霜月卡池研究与原型.xlsx.inspect.ndjson');
try{await fs.rename(inspectSidecar,path.join(qa,'export-inspection.ndjson'));}catch(e){if(e.code!=='ENOENT')throw e;}
await fs.writeFile(path.join(qa,'workbook-checks.json'),JSON.stringify({reference_classes:93,reward:85,solo:80,groups,parameter_recalculation:{baseline,changed,restored:6},formula_scan:errors.ndjson},null,2));
console.log(JSON.stringify({output,inventory:result,groups,recalculation:[baseline,changed,6],formulaScan:errors.ndjson}));
