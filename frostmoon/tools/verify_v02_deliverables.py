"""Read-only verification of the exported files; not gameplay validation."""
import json, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

root=Path(__file__).resolve().parents[1]
out=root.parent/'outputs/01a1009b-46b5-7492-aa6a-c58b009ff7e0'
qa=root.parent/'artifacts/frostmoon-v02-qa'
d=json.loads((root/'v02/design.json').read_text())
rules=json.loads((root/'v02/rules.json').read_text())
checks=json.loads((qa/'workbook-checks.json').read_text())
ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def col(i):
 s='';i+=1
 while i:
  i,r=divmod(i-1,26);s=chr(65+r)+s
 return s
with zipfile.ZipFile(out/'霜月三形态卡池v0.2.xlsx') as z:
 assert z.testzip() is None
 ss=ET.fromstring(z.read('xl/sharedStrings.xml'))
 strings=[''.join(x.itertext()) for x in ss]
 wb=ET.fromstring(z.read('xl/workbook.xml'))
 assert [s.attrib['name'] for s in wb.findall('m:sheets/m:sheet',ns)]==['方案与规则','64张卡牌','逐组审阅','样例卡组','参数与算术','衍生与来源']
 sheets=[ET.fromstring(z.read(f'xl/worksheets/sheet{i}.xml')) for i in range(1,7)]
 def cells(sheet):
  result={}
  for c in sheet.findall('.//m:c',ns):
   assert c.attrib.get('t')!='e',c.attrib
   v=c.findtext('m:v',namespaces=ns)
   if c.attrib.get('t')=='s':v=strings[int(v)]
   elif c.attrib.get('t')=='inlineStr':v=''.join(c.find('m:is',ns).itertext())
   result[c.attrib['r']]=(v,c.findtext('m:f',namespaces=ns))
  return result
 allcells=[cells(s) for s in sheets];master=allcells[1]
 attrs=['name','id','rarity','type','cost','up_cost','base','upgraded','delta','mechanics','role','builds','note','phase']
 for i,c in enumerate(d['cards']):
  for j,k in enumerate(attrs):
   expected=c[k]
   if isinstance(expected,list):expected='、'.join(expected)
   assert master[f'{col(i+1)}{j+5}'][0]==str(expected),(c['id'],k)
  assert master[f'{col(i+1)}19'][0]=='待审阅'
 assert len({master[f'{col(i+1)}6'][0] for i in range(64)})==64
 by={c['id']:i for i,c in enumerate(d['cards'])}
 for b in checks['blocks']:
  for i,ident in enumerate(b['ids']):
   for j,k in enumerate(attrs):
    expected=master[f'{col(by[ident]+1)}{j+5}'][0]
    val,formula=allcells[2][f'{col(i+1)}{b["start"]+j}']
    assert val==expected and formula,(ident,k,val,expected)
 for b in checks['deckRanges']:assert allcells[3][f'C{b["total"]}'][0]=='20'
 assert [allcells[4][f'B{r}'][0] for r in range(30,38)]==list(map(str,[28,40,12,16,32,4,18,24]))
 pane=sheets[1].find('m:sheetViews/m:sheetView/m:pane',ns)
 assert pane.attrib['xSplit']=='1' and pane.attrib['ySplit']=='5'
 validation=sheets[1].find('m:dataValidations/m:dataValidation',ns)
 assert validation is not None
 formulas=sum(f is not None for s in allcells for v,f in s.values())

wns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with zipfile.ZipFile(out/'霜月三形态设计说明v0.2.docx') as z:
 assert z.testzip() is None
 t=ET.fromstring(z.read('word/document.xml'))
 text=''.join(e.text or '' for e in t.findall('.//w:t',wns))
 count=0
 for page in rules['pages']:
  assert page['title'] in text
  for b in page['blocks']:
   expected=([b['text']] if b['type'] in ('p','h') else [str(v) for row in [b['headers'],*b['rows']] for v in row] if b['type']=='table' else [s[0] for s in b['items']])
   for value in expected:assert value in text,value;count+=1
 styles=ET.fromstring(z.read('word/styles.xml'))
 assert not styles.findall('.//w:pBdr',wns)
result={'exported_character_cards':64,'complete_base_and_upgrade_fields_verified':True,'review_mirrors_verified':64,'sample_deck_sizes':[20]*4,'formula_cells':formulas,'formula_errors':0,'document_content_items_verified':count,'scope':'Exported file integrity and consistency only; no host game or balance simulation.'}
(qa/'delivery-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
