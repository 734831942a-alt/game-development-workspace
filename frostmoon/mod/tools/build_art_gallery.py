"""Package original illustrations and native game card renders without raster edits."""
from pathlib import Path
import argparse, json, shutil, hashlib

r = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--out', type=Path, default=r / 'art/card-gallery-v4')
parser.add_argument('--art-set', default='illustrated-v4')
parser.add_argument('--renders', type=Path, default=r / 'logs/art-v4/cards')
parser.add_argument('--prompts', type=Path, default=r / 'art/card-art-prompts-v4.json')
args = parser.parse_args()
out = args.out
version = json.loads((r / 'Frostmoon.json').read_text())['version']
for folder in ['illustrations', 'cards']:
    (out / folder).mkdir(parents=True, exist_ok=True)
design = json.loads((r.parent / 'v02/design.json').read_text())
cards = design['cards'] + design['tokens']
assert len(cards) == 66
hashes = {}
for card in cards:
    code = card['id']
    sources = [(r / f'assets/cards/{args.art_set}/{code}.png', out / f'illustrations/{code}.png')]
    for state in ['base', 'upgrade']:
        sources.append((args.renders / f'{code}-{state}.png', out / f'cards/{code}-{state}.png'))
    for src, dst in sources:
        if not src.is_file():
            raise FileNotFoundError(src)
        shutil.copy2(src, dst)
        hashes[str(dst.relative_to(out))] = hashlib.sha256(src.read_bytes()).hexdigest()
shutil.copy2(r / 'art/frostmoon-character-approved.png', out / 'character.png')
shutil.copy2(args.prompts, out / '生成提示词.json')
shutil.copy2(r / 'assets/ui/portrait-v3.png', out / 'portrait.png')
shutil.copytree(r / 'assets/ui/status-v3', out / 'status', dirs_exist_ok=True)
(out / 'SHA256.json').write_text(json.dumps(hashes, indent=2), encoding='utf-8')

html = r'''<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>霜月 · 冰月绘卷</title>
<style>
:root{color-scheme:dark;--bg:#0d1420;--panel:#152031;--ink:#e8eef5;--muted:#a0b1c7;--line:#314359;--accent:#b9ddeb}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.65 system-ui,-apple-system,"PingFang SC",sans-serif}button,input,select{font:inherit}button,select,input{color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:7px;padding:9px 14px}button,a,select{cursor:pointer}button:hover,button[aria-pressed=true]{background:#30465d;border-color:var(--accent)}a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}header{max-width:1500px;margin:auto;padding:52px 40px 28px;border-bottom:1px solid var(--line);position:relative;overflow:hidden}header small{letter-spacing:.25em;color:var(--muted)}h1{font-family:serif;font-size:48px;font-weight:500;letter-spacing:.14em;margin:9px 0}header p{color:var(--muted);max-width:780px;margin:0}header .links{margin-top:18px;display:flex;gap:25px}.tools{position:sticky;top:0;background:#0d1420f5;backdrop-filter:blur(12px);border-bottom:1px solid var(--line);z-index:3;padding:17px 40px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}.tools input{min-width:230px;flex:1}.tools .group{display:flex;gap:6px}#count{color:var(--muted);min-width:70px;text-align:right}.grid{max-width:1540px;margin:auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:24px;padding:30px 40px 60px}.card{background:var(--panel);border:1px solid #26374c;border-radius:10px;overflow:hidden;transition:transform .16s,border-color .16s}.card:hover{transform:translateY(-4px);border-color:#7896b4}.picture{padding:0;display:block;width:100%;border:0;background:transparent;border-radius:0}.picture:hover{background:#1b2b40}.picture img{display:block;width:100%;aspect-ratio:420/570;object-fit:contain}.art-view .picture img{aspect-ratio:1;object-fit:cover}.meta{padding:13px 18px 18px;border-top:1px solid #26374c}.meta h2{font-size:19px;letter-spacing:.07em;margin:0 0 4px}.meta small{color:var(--muted)}.empty{grid-column:1/-1;text-align:center;padding:60px;color:var(--muted)}dialog{border:1px solid #566a84;border-radius:12px;background:#101b2b;color:var(--ink);width:min(1150px,96vw);max-height:94vh;padding:24px}dialog::backdrop{background:#000c;backdrop-filter:blur(8px)}.detail{display:grid;grid-template-columns:minmax(280px,1.3fr) minmax(230px,1fr);gap:30px;align-items:start}.detail img{width:100%;max-height:77vh;object-fit:contain}.detail h2{font-size:30px;font-weight:500;margin:10px 0}.detail small{color:var(--muted)}.detail p{white-space:pre-line}.close{float:right;margin-bottom:12px}.detail .links{display:flex;gap:12px;flex-wrap:wrap;margin-top:26px}.detail .effect{padding:18px;background:#19293f;border-left:2px solid var(--accent);margin:22px 0}.detail footer{margin-top:30px;color:var(--muted);font-size:13px}body.modal-open{overflow:hidden}footer.page{max-width:1500px;margin:auto;color:var(--muted);padding:20px 40px 40px;border-top:1px solid var(--line)}@media(max-width:700px){header{padding:28px 20px 22px}h1{font-size:34px}.tools{padding:12px 16px;gap:8px}.grid{padding:20px 16px;gap:14px;grid-template-columns:repeat(2,minmax(0,1fr))}.meta{padding:10px}.meta h2{font-size:16px}.detail{grid-template-columns:1fr}.detail img{max-height:50vh}.tools input{min-width:180px}dialog{padding:16px}}
.art-view .picture img{aspect-ratio:3/2;object-fit:contain}.grid.compact{grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:12px}.compact .meta{padding:8px}.compact .meta h2{font-size:15px}.compact .meta small{font-size:11px}.blind .meta h2{display:none}.ui-strip{display:flex;align-items:center;gap:16px;flex-wrap:wrap;margin-top:22px}.ui-strip img{width:44px;height:44px;object-fit:contain}.ui-strip .avatar{width:62px;height:62px;border:1px solid #8299ad;border-radius:8px}.ui-strip .stages{display:flex;gap:9px;align-items:center}.stage{text-align:center;font-size:11px;color:var(--muted)}.stage img{display:block}.ui-strip span.label{font-size:13px;color:var(--muted)}
</style>
<header><small>FROSTMOON / ART COLLECTION 02</small><h1>霜月 · 冰月绘卷</h1><p>64 张主卡 · 2 张衍生牌。以霜月的动作、太刀与魔法区分每张牌。可缩小预览、隐藏名称，检查手牌中的辨识度。</p><div class="links"><a href="character.png" target="_blank">角色定稿 ↗</a><a href="生成提示词.json" download>制作提示词 ↓</a></div><div class="ui-strip" aria-label="角色头像与状态图标"><img class="avatar" src="portrait.png" alt="统一角色头像"><span class="label">霜</span><img src="status/frost.svg" alt="明亮的霜图标"><span class="label">月痕</span><div class="stages"><div class="stage"><img src="status/moon-1.svg" alt="月痕一层">1 / 8</div><div class="stage"><img src="status/moon-4.svg" alt="月痕四层">4 / 8</div><div class="stage"><img src="status/moon-7.svg" alt="月痕七层">7 / 8</div><div class="stage"><img src="status/moon-8.svg" alt="月痕满层">8 / 8</div></div></div></header>
<section class="tools" aria-label="筛选与显示"><input id="search" type="search" placeholder="搜索牌名、编号或效果…" aria-label="搜索卡牌"><select id="type" aria-label="卡牌类型"><option value="">全部类型</option><option>攻击</option><option>技能</option><option>能力</option></select><select id="rarity" aria-label="稀有度"><option value="">全部稀有度</option><option>初始</option><option>普通</option><option>罕见</option><option>稀有</option><option>衍生</option></select><div class="group"><button id="native" aria-pressed="true">完整卡牌</button><button id="art" aria-pressed="false">无字插画</button></div><button id="upgrade" aria-pressed="false">升级版</button><button id="compact" aria-pressed="false">缩小预览</button><button id="blind" aria-pressed="false">隐藏名称</button><span id="count" aria-live="polite"></span></section>
<main class="grid" id="grid"></main>
<footer class="page">完整卡牌由《杀戮尖塔 2》实际卡牌 UI 渲染，插画由内置 imagegen 按逐牌构图制作。升级版共享插画，保留游戏原生的费用、卡名、卡文与稀有度样式。__VERSION__</footer>
<dialog id="detail"><button class="close" id="close">关闭 ×</button><div class="detail"><img id="large" alt=""><section><small id="detail-meta"></small><h2 id="detail-name"></h2><p class="effect" id="effect"></p><p id="note"></p><div class="links"><a id="original" target="_blank">查看插画原图 ↗</a><a id="download" download>保存完整卡牌 ↓</a></div><footer>用牌名或编号反馈修改意见，即可定位到原图和游戏资源。</footer></section></div></dialog>
<script>
const cards=__CARDS__;
const $=id=>document.getElementById(id);let art=false,up=false,compact=false,blind=false;
const src=c=>art?`illustrations/${c.id}.png`:`cards/${c.id}-${up?'upgrade':'base'}.png`;
function show(c){$('large').src=src(c);$('large').alt=c.name;$('detail-name').textContent=c.name+(up?'＋':'');$('detail-meta').textContent=`${c.id} · ${c.type} · ${c.rarity} · ${up?c.up_cost:c.cost} 费`;$('effect').textContent=up?c.upgraded:c.base;$('note').textContent=c.note||c.origin||'';$('original').href=`illustrations/${c.id}.png`;$('download').href=`cards/${c.id}-${up?'upgrade':'base'}.png`;$('download').download=c.id+'-'+c.name+(up?'-升级':'')+'.png';$('detail').showModal();document.body.classList.add('modal-open')}
function render(){const query=$('search').value.trim().toLowerCase();const list=cards.filter(c=>(!$('type').value||c.type===$('type').value)&&(!$('rarity').value||c.rarity===$('rarity').value)&&(!query||(c.id+c.name+c.base+c.upgraded).toLowerCase().includes(query)));$('count').textContent=`${list.length} / 66`;$('grid').classList.toggle('art-view',art);$('grid').classList.toggle('compact',compact);$('grid').classList.toggle('blind',blind);$('grid').replaceChildren();for(const c of list){const item=document.createElement('article');item.className='card';const button=document.createElement('button');button.className='picture';button.setAttribute('aria-label','查看'+c.name);const img=document.createElement('img');img.src=src(c);img.alt=c.name;img.loading='lazy';button.append(img);button.onclick=()=>show(c);const meta=document.createElement('div');meta.className='meta';const title=document.createElement('h2');title.textContent=c.name+(up?'＋':'');const sub=document.createElement('small');sub.textContent=`${c.id} · ${c.type} · ${c.rarity} · ${up?c.up_cost:c.cost} 费`;meta.append(title,sub);item.append(button,meta);$('grid').append(item)}if(!list.length){const empty=document.createElement('p');empty.className='empty';empty.textContent='没有匹配的卡牌，请调整筛选条件。';$('grid').append(empty)}}
for(const id of ['search','type','rarity'])$(id).addEventListener('input',render);
$('native').onclick=()=>{art=false;blind=false;$('blind').setAttribute('aria-pressed','false');$('native').setAttribute('aria-pressed','true');$('art').setAttribute('aria-pressed','false');render()};$('art').onclick=()=>{art=true;$('native').setAttribute('aria-pressed','false');$('art').setAttribute('aria-pressed','true');render()};$('upgrade').onclick=()=>{up=!up;$('upgrade').setAttribute('aria-pressed',String(up));render()};$('compact').onclick=()=>{compact=!compact;$('compact').setAttribute('aria-pressed',String(compact));render()};$('blind').onclick=()=>{blind=!blind;$('blind').setAttribute('aria-pressed',String(blind));if(blind){art=true;$('art').setAttribute('aria-pressed','true');$('native').setAttribute('aria-pressed','false')}render()};$('close').onclick=()=>$('detail').close();$('detail').onclose=()=>document.body.classList.remove('modal-open');$('detail').onclick=e=>{if(e.target===$('detail'))$('detail').close()};render();
</script></html>'''
html = html.replace('__VERSION__', version).replace('__CARDS__', json.dumps(cards, ensure_ascii=False).replace('</', '<\\/'))
(out / 'index.html').write_text(html, encoding='utf-8')
(out / '使用说明.txt').write_text('双击 index.html 浏览全部 66 张卡牌。可搜索、筛选类型与稀有度，切换升级版或无字插画，点击卡牌放大。缩小预览配合隐藏名称，可检查插画辨识度。\nillustrations：66 张未经缩放的插画原图。cards：132 张游戏原生 UI 完整卡牌图。character.png：用户确认的角色立绘。\n制作方式：内置 imagegen，每张卡独立提示词；提示词保存在生成提示词.json。\n', encoding='utf-8')
print(f'{len(cards)} illustrations + {len(cards)*2} card renders -> {out}')
