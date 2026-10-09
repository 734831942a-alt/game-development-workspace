"""Draw deterministic prototype symbols; copy the generated character without editing it."""
from pathlib import Path
from PIL import Image,ImageDraw
import math,shutil,json
r=Path(__file__).resolve().parents[1]; a=r/'assets'
for sub in ['ui','cards','scenes','localization/zhs','localization/eng']:(a/sub).mkdir(parents=True,exist_ok=True)
shutil.copy2(r/'art/frostmoon-concept.png',a/'character.png')
def symbol(name,size,mode):
 im=Image.new('RGBA',(size,size),(0,0,0,0));d=ImageDraw.Draw(im);s=size
 d.ellipse((s*.08,s*.08,s*.92,s*.92),fill='#13283d',outline='#8bbad3',width=max(1,s//40))
 if mode=='ice':
  for ang in range(0,360,60):
   x=s*.5+math.cos(math.radians(ang))*s*.31;y=s*.5+math.sin(math.radians(ang))*s*.31
   d.line((s*.5,s*.5,x,y),fill='#bceaff',width=max(2,s//25))
 elif mode=='attack':
  d.polygon([(s*.28,s*.78),(s*.68,s*.16),(s*.7,s*.37),(s*.42,s*.75)],fill='#e6f6ff')
  d.line((s*.25,s*.62,s*.51,s*.82),fill='#72bfe0',width=max(2,s//20))
 else:
  d.ellipse((s*.24,s*.2,s*.78,s*.76),fill='#daeeff');d.ellipse((s*.44,s*.13,s*.85,s*.61),fill='#13283d')
 im.save(a/name)
for name,size,mode in [('ui/portrait.png',128,'moon'),('ui/energy.png',256,'moon'),('ui/energy_text.png',24,'moon'),('ui/pendant.png',256,'moon'),('ui/ice.png',64,'ice'),('ui/moon.png',64,'moon')]:symbol(name,size,mode)
for name,mode in [('attack','attack'),('skill','ice'),('power','moon')]:
 symbol('cards/'+name+'.png',512,mode)
(a/'scenes/select.tscn').write_text('''[gd_scene load_steps=2 format=3]
[ext_resource type="Texture2D" path="res://Frostmoon/character.png" id="1"]
[node name="FrostmoonSelect" type="Control"]
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
mouse_filter = 2
[node name="Backdrop" type="ColorRect" parent="."]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
color = Color(0.035,0.065,0.12,1)
mouse_filter = 2
[node name="Portrait" type="TextureRect" parent="."]
offset_left = 1400.0
offset_top = 140.0
offset_right = 2100.0
offset_bottom = 920.0
texture = ExtResource("1")
expand_mode = 1
stretch_mode = 5
mouse_filter = 2
''')
(a/'scenes/rest.tscn').write_text('''[gd_scene load_steps=2 format=3]
[ext_resource type="Texture2D" path="res://Frostmoon/character.png" id="1"]
[node name="Frostmoon" type="Sprite2D"]
texture = ExtResource("1")
scale = Vector2(0.22,0.22)
offset = Vector2(0,-768)
''')
(a/'scenes/merchant.tscn').write_text((a/'scenes/rest.tscn').read_text())
print('Assets generated; character image copied unchanged.')
