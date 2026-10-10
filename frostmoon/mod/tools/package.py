from pathlib import Path
import shutil,zipfile,json,hashlib
r=Path(__file__).resolve().parents[1]
version=json.loads((r/'Frostmoon.json').read_text())['version']
out=r.parents[1]/'outputs/01a1009b-46b5-7492-aa6a-c58b009ff7e0'/('小木曾和纱Mod-'+version+'-冰月绘卷')
out.mkdir(parents=True,exist_ok=True)
for n in ['BaseLib','Frostmoon']:(out/'mods'/n).mkdir(parents=True,exist_ok=True)
for f in (r/'vendor/BaseLib').glob('BaseLib.*'):shutil.copy2(f,out/'mods/BaseLib'/f.name)
shutil.copy2(r/'references/BaseLib/LICENSE.txt',out/'mods/BaseLib/LICENSE.txt')
for name,src in [('Frostmoon.dll',r/'bin/Release/net9.0/Frostmoon.dll'),('Frostmoon.json',r/'Frostmoon.json'),('Frostmoon.pck',r/'dist/Frostmoon/Frostmoon.pck')]:shutil.copy2(src,out/'mods/Frostmoon'/name)
shutil.copy2(r/'README.md',out/'使用说明.md')
shutil.copy2(r/'测试记录.txt',out/'测试记录.txt')
launcher=out.parent/'霜月Mod试玩版/启动霜月隔离试玩.command'
if launcher.is_file():
 target=out/'启动小木曾和纱隔离试玩.command'
 target.write_text(launcher.read_text().replace('霜月','小木曾和纱'))
 target.chmod(0o755)
for src,dest in [('v0.2.3/combat.png','战斗预览.png'),('v0.2.3/select.png','选角预览.png')]:
 if (r/'logs'/src).exists():shutil.copy2(r/'logs'/src,out/dest)
hashes={str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (out/'mods').rglob('*') if f.is_file()}
(out/'SHA256.json').write_text(json.dumps(hashes,indent=2))
with zipfile.ZipFile(out.parent/f'小木曾和纱Mod-{version}-安装包.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in out.rglob('*'):
  if f.is_file() and not f.name.endswith('.command'):z.write(f,'Frostmoon-'+version+'/'+str(f.relative_to(out)))
with zipfile.ZipFile(out.parent/f'小木曾和纱Mod-{version}-源码.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in ['src','assets','art/card-art-prompts-v4.json','art/character-select-cover-prompt.txt','art/frostmoon-character-approved.png','Frostmoon.csproj','Frostmoon.json','README.md','tools/generate_cards.py','tools/build_art_gallery.py','tools/make_status_icons.py','tools/build.sh','tools/package.py','tools/BuildPack/Packer.csproj','tools/BuildPack/Program.cs']:
  p=r/name
  for f in p.rglob('*') if p.is_dir() else [p]:
   if f.is_file():
    rel=str(f.relative_to(r))
    if rel.startswith('assets/cards/illustrated-') and not rel.startswith('assets/cards/illustrated-v4/'):continue
    z.write(f,'Frostmoon/'+rel)
 for f in (r/'vendor/BaseLib').glob('BaseLib.*'):z.write(f,'Frostmoon/vendor/BaseLib/'+f.name)
 z.write(r/'references/BaseLib/LICENSE.txt','Frostmoon/vendor/BaseLib/LICENSE.txt')
 z.write(r.parent/'v02/design.json','v02/design.json')
gallery=r/'art/card-gallery-v4'
if gallery.exists():
 with zipfile.ZipFile(out.parent/f'霜月-{version}-完整卡面与原画.zip','w',zipfile.ZIP_DEFLATED) as z:
  for f in gallery.rglob('*'):
   if f.is_file():z.write(f,'霜月卡册/'+str(f.relative_to(gallery)))
print(out)
