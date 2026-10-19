"""Build the compressed showcase images used by the repository README.

Reads only files already in the repository (card illustrations, the runtime
card catalog and playtest screenshots) and writes JPEGs to docs/media/.
Run from anywhere:  python3 frostmoon/mod/tools/make_readme_media.py [--font PATH]
"""
from pathlib import Path
import argparse
import re

from PIL import Image, ImageDraw, ImageFont

MOD = Path(__file__).resolve().parents[1]
ROOT = MOD.parents[1]
ART = MOD / 'assets/cards/illustrated-v4'
OUT = ROOT / 'docs/media'
PLAYTESTS = ROOT / 'docs/playtests'

FEATURED = ['C08', 'R03', 'C10', 'R05', 'U15', 'R02', 'U22', 'R11']
RARITY_COLOR = {
    'Basic': (150, 150, 150), 'Common': (170, 185, 200), 'Uncommon': (95, 165, 235),
    'Rare': (235, 190, 85), 'Token': (120, 200, 150),
}
FONT_CANDIDATES = [
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc',
    '/System/Library/Fonts/PingFang.ttc',
    '/System/Library/Fonts/STHeiti Medium.ttc',
    'C:/Windows/Fonts/msyh.ttc',
]


def load_catalog():
    """Card id -> (name, rarity) from the generated runtime catalog.

    Skips the Q-prefixed pseudo cards used only as choice prompts (pay HP, enter form)."""
    text = (MOD / 'src/Catalog.g.cs').read_text(encoding='utf-8')
    pattern = r'\["([BCURT]\d\d)"\] = new\("\w+","([^"]+)",-?\d+,-?\d+,CardType\.\w+,CardRarity\.(\w+)'
    return {cid: (name, rarity) for cid, name, rarity in re.findall(pattern, text)}


def card_order(catalog):
    prefix = {'B': 0, 'C': 1, 'U': 2, 'R': 3, 'T': 4}
    return sorted(catalog, key=lambda c: (prefix[c[0]], int(c[1:])))


def cover(path, size):
    """Scale to fill `size`, centre-crop the overflow."""
    im = Image.open(path).convert('RGB')
    scale = max(size[0] / im.width, size[1] / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    left, top = (im.width - size[0]) // 2, (im.height - size[1]) // 2
    return im.crop((left, top, left + size[0], top + size[1]))


def card_wall(catalog, font):
    cols, tile_w, tile_h, label_h, gap = 11, 240, 160, 30, 6
    ids = card_order(catalog)
    rows = -(-len(ids) // cols)
    sheet = Image.new('RGB', (cols * (tile_w + gap) + gap, rows * (tile_h + label_h + gap) + gap), (13, 20, 32))
    draw = ImageDraw.Draw(sheet)
    for i, cid in enumerate(ids):
        x = gap + (i % cols) * (tile_w + gap)
        y = gap + (i // cols) * (tile_h + label_h + gap)
        sheet.paste(cover(ART / f'{cid}.png', (tile_w, tile_h)), (x, y))
        name, rarity = catalog[cid]
        draw.rectangle((x, y + tile_h, x + tile_w, y + tile_h + label_h), fill=(21, 32, 49))
        draw.rectangle((x, y + tile_h, x + 4, y + tile_h + label_h), fill=RARITY_COLOR[rarity])
        draw.text((x + 12, y + tile_h + label_h // 2), f'{cid}  {name}', font=font, fill=(232, 238, 245), anchor='lm')
    sheet.save(OUT / 'card-wall.jpg', quality=82, optimize=True)


def featured():
    for cid in FEATURED:
        cover(ART / f'{cid}.png', (480, 320)).save(OUT / f'card-{cid}.jpg', quality=85, optimize=True)


def iteration(font):
    shots = [
        ('v0.1-试玩版', 'v0.1 机制原型：程序化占位卡图'),
        ('v0.2.1-冰月绘卷', 'v0.2.1 接入立绘与逐牌插画'),
        ('v0.2.2-冰月绘卷', 'v0.2.2 新服装立绘与卡图适配'),
    ]
    w, h, label_h = 640, 360, 44
    strip = Image.new('RGB', (w * len(shots), h + label_h), (13, 20, 32))
    draw = ImageDraw.Draw(strip)
    for i, (folder, caption) in enumerate(shots):
        strip.paste(cover(PLAYTESTS / folder / '战斗预览.png', (w, h)), (i * w, label_h))
        draw.text((i * w + w // 2, label_h // 2), caption, font=font, fill=(232, 238, 245), anchor='mm')
    strip.save(OUT / 'iteration.jpg', quality=82, optimize=True)


def combat():
    shot = Image.open(PLAYTESTS / 'v0.2.2-冰月绘卷/战斗预览.png').convert('RGB')
    shot.save(OUT / 'combat.jpg', quality=88, optimize=True)
    select = Image.open(PLAYTESTS / 'v0.2.2-冰月绘卷/选角预览.png').convert('RGB')
    select.save(OUT / 'select.jpg', quality=88, optimize=True)
    cover_art = Image.open(MOD / 'assets/ui/character-select-cover.png').convert('RGB')
    cover_art.thumbnail((1600, 900), Image.LANCZOS)
    cover_art.save(OUT / 'cover.jpg', quality=85, optimize=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--font', help='a font file with CJK glyphs')
    args = parser.parse_args()
    font_path = args.font or next((f for f in FONT_CANDIDATES if Path(f).is_file()), None)
    if not font_path:
        raise SystemExit('No CJK font found; pass --font /path/to/font')
    OUT.mkdir(parents=True, exist_ok=True)
    catalog = load_catalog()
    assert len(catalog) == 66, len(catalog)
    card_wall(catalog, ImageFont.truetype(font_path, 15))
    featured()
    iteration(ImageFont.truetype(font_path, 20))
    combat()
    for f in sorted(OUT.glob('*.jpg')):
        print(f.relative_to(ROOT), f.stat().st_size // 1024, 'KB')


if __name__ == '__main__':
    main()
