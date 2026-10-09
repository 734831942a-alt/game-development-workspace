"""Verify inventory, provenance, design data, and exported XLSX structure; no gameplay simulation."""
import hashlib, json, re, zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
SRC=Path('/private/tmp/frostmoon-mzm-reference')
ref=json.loads((ROOT/'data/reference_cards.json').read_text())
proto=json.loads((ROOT/'data/prototype.json').read_text())
raw=json.loads((ROOT/'data/reference_extracted.json').read_text())
by_id={r['id']:r for r in ref['cards']}
assert len(by_id)==93
assert set(by_id)=={p.stem for p in (SRC/'src/Game/CharacterContent/Cards').glob('*.cs')}
for r in ref['cards']:
    p=SRC/'src/Game/CharacterContent/Cards'/f"{r['id']}.cs"
    assert hashlib.sha256(p.read_bytes()).hexdigest()==r['source_sha256']
    assert r['base_effect'] and r['upgrade_delta'] and r['roles'] and r['archetypes']
    _,loc=r['source_url'].rsplit('#L',1)
    assert f"public {r['id']}()" in p.read_text().splitlines()[int(loc)-1]
assert Counter(r['rarity'] for r in ref['cards'])==Counter(Common=20,Uncommon=38,Rare=27,Basic=4,Token=2,Ancient=2)
assert {r['id'] for r in ref['cards'] if r['multiplayer_only']}=={'BullyingYou','Ensemble','HeartResonance','HugThigh','MuOneForAll'}
assert [r['cost'] for r in ref['cards'] if r['id'] in ('HollowActor','DollWaltz')]==['X','X']
assert Counter(c['group'] for c in proto['cards'])==Counter(Frost=5,Moon=5,Bridge=3,Utility=2)
assert len({c['id'] for c in proto['cards']})==15
known={c['id'] for c in proto['cards']}|{'test_strike','test_defend'}
for name,deck in proto['fixtures'].items():
    assert set(deck)<=known
    assert sum(deck.values())==(10 if name=='starter' else 5)
link_count=0
for doc in ROOT.glob('*.md'):
    text=doc.read_text()
    for link in re.findall(r'\]\(([^)]+)\)',text):
        if link.startswith('https://github.com/FFTYYY/sts2-MzmChar-mod/blob/'):
            sha,relative=link.split('/blob/')[1].split('/',1)
            assert sha==ref['commit'],(doc,link)
            assert (SRC/relative.split('#')[0]).is_file(),(doc,link)
            link_count+=1
        elif not link.startswith('http'):
            assert (doc.parent/link.split('#')[0]).exists(),(doc,link)
book=ROOT.parent/'outputs/01a1009b-46b5-7492-aa6a-c58b009ff7e0/霜月卡池研究与原型.xlsx'
ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile(book) as z:
    assert z.testzip() is None
    workbook=ET.fromstring(z.read('xl/workbook.xml'))
    assert [s.attrib['name'] for s in workbook.findall('m:sheets/m:sheet',ns)]==['研究摘要','15张原型','参数试验','若叶睦卡池']
    all_errors=[];panes={};formula_count=0
    for name in z.namelist():
        if re.fullmatch(r'xl/worksheets/sheet\d+\.xml',name):
            t=ET.fromstring(z.read(name))
            for c in t.findall('.//m:c',ns):
                if c.attrib.get('t')=='e': all_errors.append((name,c.attrib))
                if c.find('m:f',ns) is not None:formula_count+=1
            pane=t.find('m:sheetViews/m:sheetView/m:pane',ns)
            if pane is not None: panes[name]=pane.attrib
    assert not all_errors,all_errors
    for name in ['xl/worksheets/sheet2.xml','xl/worksheets/sheet4.xml']:
        assert panes[name].get('xSplit')=='2' and panes[name].get('ySplit')=='6',panes
    table_refs=[ET.fromstring(z.read(n)).attrib['ref'] for n in z.namelist() if re.fullmatch(r'xl/tables/table\d+\.xml',n)]
    assert set(table_refs)=={'A6:W99','A6:L21','A6:E18'},table_refs
    s=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    values={c.attrib['r']:c.findtext('m:v',namespaces=ns) for c in s.findall('.//m:c',ns)}
    assert values['B13']=='93' and values['B14']=='85' and values['D14']=='80' and values['E14']=='31',values
result={'card_classes':93,'prototype_cards':15,'source_links_verified_locally':link_count,'xlsx_tables':table_refs,'xlsx_formula_errors':0,'frozen_panes':panes,'validation_scope':'Static data and exported workbook; no Mod build or gameplay tests.'}
dest=ROOT.parent/'artifacts/frostmoon-qa/deliverable-verification.json'
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
