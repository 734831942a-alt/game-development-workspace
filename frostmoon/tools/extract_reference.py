"""Extract a pinned source inventory; card interpretation is reviewed separately."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('/private/tmp/frostmoon-mzm-reference')

def body(text, marker):
    start = text.find(marker)
    if start < 0:
        return ''
    start = text.find('{', start)
    depth = 1
    end = start + 1
    while depth and end < len(text):
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start + 1:end - 1]

def compact(text):
    text = re.sub(r'//[^\n]*', '', text)
    return '\n'.join(line.strip() for line in text.splitlines() if line.strip())

def extract():
    sha = subprocess.check_output(['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'], text=True).strip()
    records = []
    for path in sorted((SOURCE / 'src/Game/CharacterContent/Cards').glob('*.cs')):
        text = path.read_text()
        ctor = re.search(r'public ' + path.stem + r'\(\)\s*:\s*base\(([^\n]+)\)', text)
        loc = text.split('"zhs" =>', 1)[-1].split('_ =>', 1)[0]
        strs = re.findall(r'"((?:\\.|[^"\\])*)"', loc)
        decoded = [json.loads('"' + x + '"') for x in strs]
        lines = text.splitlines()
        record = {
            'id': path.stem,
            'name': decoded[0] if decoded else '',
            'localization': ''.join(decoded[1:]),
            'constructor': ctor.group(1) if ctor else '',
            'keywords': re.findall(r'(?:CardKeyword|MzmCharKeywords)\.([A-Za-z]+)', body(text, 'HashSet<CardKeyword>')) if 'HashSet<CardKeyword>' in text else [],
            'multiplayer_only': 'MultiplayerConstraint => CardMultiplayerConstraint.MultiplayerOnly' in text,
            'x_cost': 'HasEnergyCostX => true' in text,
            'variables': compact(body(text, 'private readonly List<DynamicVar>')),
            'upgrade_code': compact(body(text, 'protected override void OnUpgrade')),
            'play_code': compact(body(text, 'protected override async Task OnPlay')),
            'other_logic': compact(text[text.find('public class'):text.find('public override List<(string, string)>')]),
            'path': str(path.relative_to(SOURCE)),
            'url': f'https://github.com/FFTYYY/sts2-MzmChar-mod/blob/{sha}/{path.relative_to(SOURCE)}',
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'lines': {key: next((i+1 for i,l in enumerate(lines) if marker in l), None)
                      for key, marker in [('constructor', ': base('), ('upgrade', 'void OnUpgrade'), ('play', 'Task OnPlay'), ('localization', '"zhs" =>')]},
        }
        if ctor:
            record['lines']['constructor'] = text.count('\n', 0, ctor.start()) + 1
        records.append(record)
    out = ROOT / 'data/reference_extracted.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({'repository':'https://github.com/FFTYYY/sts2-MzmChar-mod', 'commit':sha, 'retrieved':'2026-10-03', 'cards':records}, ensure_ascii=False, indent=2))
    return records

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=int, default=0)
    parser.add_argument('--count', type=int, default=15)
    parser.add_argument('--full', action='store_true')
    args = parser.parse_args()
    records = extract()
    print('CARD FILE COUNT', len(records))
    for record in records[args.start:args.start + args.count]:
        print('\n###', record['id'], record['name'], record['constructor'])
        print('TEXT', record['localization'])
        if args.full:
            print(record['other_logic'])
        else:
            print('VARS', record['variables'])
            print('UPGRADE', record['upgrade_code'])
            print('PLAY', record['play_code'])
