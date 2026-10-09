"""Author deterministic vector UI symbols; does not edit generated raster art."""
from pathlib import Path
import math

root = Path(__file__).resolve().parents[1] / 'assets/ui/status-v3'
root.mkdir(parents=True, exist_ok=True)
head = '<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">'
for amount in range(9):
    body = ['<circle cx="128" cy="128" r="112" fill="#080d25" stroke="#d3c6ff" stroke-width="7"/>',
            '<circle cx="128" cy="128" r="100" fill="#343553"/>']
    for segment in range(amount):
        a, b = [math.radians(-90 + n * 45) for n in (segment, segment + 1)]
        x1, y1 = 128 + 100 * math.cos(a), 128 + 100 * math.sin(a)
        x2, y2 = 128 + 100 * math.cos(b), 128 + 100 * math.sin(b)
        body.append(f'<path d="M128 128 L{x1:.3f} {y1:.3f} A100 100 0 0 1 {x2:.3f} {y2:.3f} Z" fill="#fff1c7"/>')
    # Craters are included only once their complete silhouette lies in the illuminated region.
    for x, y, radius, stage in [(160, 65, 13, 1), (187, 111, 18, 2), (165, 170, 12, 4), (95, 184, 15, 5), (67, 120, 19, 7), (103, 73, 12, 8)]:
        if amount >= stage:
            body.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="#d8c9a5"/>')
            body.append(f'<circle cx="{x-3}" cy="{y-3}" r="{radius-3}" fill="#e8daba"/>')
    # Thin sector dividers communicate eighths without overpowering the lunar silhouette.
    if amount < 8:
        for n in range(8):
            a = math.radians(-90 + n * 45)
            x, y = 128 + 100 * math.cos(a), 128 + 100 * math.sin(a)
            body.append(f'<path d="M128 128 L{x:.3f} {y:.3f}" stroke="#666078" stroke-width="2"/>')
    body.append('<circle cx="128" cy="128" r="102" fill="none" stroke="#eee1ff" stroke-width="3"/>')
    (root / f'moon-{amount}.svg').write_text(head + ''.join(body) + '</svg>')

body = ['<path d="M128 10 L231 69 L231 187 L128 246 L25 187 L25 69 Z" fill="#083a64" stroke="#6ef4ff" stroke-width="8"/>',
        '<path d="M128 25 L217 77 L217 179 L128 231 L39 179 L39 77 Z" fill="#087fa6"/>']
for n in range(6):
    a = math.radians(-90 + n * 60)
    ex, ey = 128 + 87 * math.cos(a), 128 + 87 * math.sin(a)
    body.append(f'<path d="M128 128 L{ex:.3f} {ey:.3f}" stroke="#edffff" stroke-width="14" stroke-linecap="round"/>')
    bx, by = 128 + 56 * math.cos(a), 128 + 56 * math.sin(a)
    for sign in [-1, 1]:
        x = bx + 27 * math.cos(a + sign * math.pi/3)
        y = by + 27 * math.sin(a + sign * math.pi/3)
        body.append(f'<path d="M{bx:.3f} {by:.3f} L{x:.3f} {y:.3f}" stroke="#edffff" stroke-width="10" stroke-linecap="round"/>')
body.append('<path d="M128 102 L151 128 L128 154 L105 128 Z" fill="#ffffff"/>')
(root / 'frost.svg').write_text(head + ''.join(body) + '</svg>')
print('10 vector status icons written')
