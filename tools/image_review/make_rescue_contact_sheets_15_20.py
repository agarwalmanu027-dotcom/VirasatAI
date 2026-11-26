"""Create local inspection sheets without modifying candidates or gallery originals."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / 'tools' / 'image_review'
TARGETS = ['red_fort__st_james_church', 'sanchi_stupa__neelkantheshwar_temple',
           'city_palace_udaipur', 'city_palace_udaipur__ahar_cenotaphs',
           'mahabalipuram__cholamandal_artists_village', 'mahabalipuram__dakshinachitra',
           'mahabalipuram__muttukadu_backwaters', 'mahabalipuram__vedanthangal_bird_sanctuary',
           'jaisalmer_fort__lodhruva_jain_temples', 'jaisalmer_fort__nathmal_ji_ki_haveli',
           'mehrangarh_fort', 'mehrangarh_fort__rao_jodha_desert_rock_park',
           'mehrangarh_fort__jaswant_thada', 'mehrangarh_fort__toorji_ka_jhalra',
           'mehrangarh_fort__balsamand_lake', 'mehrangarh_fort__mahamandir_temple',
           'mehrangarh_fort__osian_temples', 'mehrangarh_fort__machia_biological_park',
           'mehrangarh_fort__singhasni_village', 'mehrangarh_fort__navchowkiya',
           'badami_cave_temples', 'badami_cave_temples__bhutanatha_group_of_temples']

def make(place_id):
    metadata_path = REVIEW / 'candidates' / place_id / 'candidates.json'
    record = json.loads(metadata_path.read_text(encoding='utf-8-sig'))
    candidates = record.get('candidates') or []
    if not candidates:
        return []
    output = REVIEW / 'rescue_sheets_15_20'
    output.mkdir(exist_ok=True)
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 16)
    paths = []
    for start in range(0, len(candidates), 12):
        batch = candidates[start:start + 12]
        rows = (len(batch) + 2) // 3
        canvas = Image.new('RGB', (1500, 55 + rows * 400), 'white')
        draw = ImageDraw.Draw(canvas)
        draw.text((12, 12), f'{record.get("display_name", place_id)} | rescue page {start // 12 + 1}', font=font, fill='black')
        for index, candidate in enumerate(batch):
            x, y = (index % 3) * 500, 55 + (index // 3) * 400
            preview = Path(candidate['preview_path'])
            if not preview.is_absolute():
                preview = ROOT / preview
            photo = Image.open(preview).convert('RGB')
            contained = ImageOps.contain(photo, (480, 310))
            canvas.paste(contained, (x + (500 - contained.width) // 2, y + (310 - contained.height) // 2))
            label = f'#{candidate["candidate_id"]} | {candidate["original_width"]} x {candidate["original_height"]}'
            title = candidate['title'].removeprefix('File:')
            draw.text((x + 8, y + 315), label, font=font, fill='black')
            for line in range(2):
                draw.text((x + 8, y + 338 + line * 20), title[line * 57:(line + 1) * 57], font=font, fill='black')
        path = output / f'{place_id}_{start // 12 + 1:02}.jpg'
        canvas.save(path, quality=95)
        paths.append(str(path))
    return paths

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--place', action='append')
    args = parser.parse_args()
    for place in args.place or TARGETS:
        for sheet in make(place):
            print(sheet)
